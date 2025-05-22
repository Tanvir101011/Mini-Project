#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import subprocess
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import threading
from scapy.all import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netsentry.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NetSentry:
    def __init__(self, interface: str, channel: int = 0, min_power: int = -100, 
                 capture: bool = False, threads: int = 5, quiet: bool = False):
        self.interface = interface
        self.channel = channel
        self.min_power = min_power
        self.capture = capture
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'netsentry-output'
        self.output_file = os.path.join(self.output_dir, 
            f"sentry_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"sentry_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'netsentry.db')
        self.cap_file = os.path.join(self.output_dir, 
            f"capture_{time.strftime('%Y%m%d_%H%M%S')}.pcap") if capture else None
        os.makedirs(self.output_dir, exist_ok=True)
        self.networks = {}
        self.devices = {}
        self.running = True
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('netsentry.log')]

    def init_db(self):
        """Initialize SQLite database for storing networks and devices."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS networks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ssid TEXT,
                    bssid TEXT,
                    channel INTEGER,
                    signal INTEGER,
                    encryption TEXT,
                    packets INTEGER,
                    timestamp TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mac TEXT,
                    associated_bssid TEXT,
                    signal INTEGER,
                    packets INTEGER,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_network(self, ssid: str, bssid: str, channel: int, signal: int, 
                     encryption: str, packets: int):
        """Store or update network in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO networks (ssid, bssid, channel, signal, encryption, packets, timestamp) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (ssid, bssid, channel, signal, encryption, packets, timestamp)
            )
            conn.commit()
        self.networks[bssid] = {
            'ssid': ssid,
            'bssid': bssid,
            'channel': channel,
            'signal': signal,
            'encryption': encryption,
            'packets': packets,
            'timestamp': timestamp
        }

    def store_device(self, mac: str, associated_bssid: str, signal: int, packets: int):
        """Store or update device in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO devices (mac, associated_bssid, signal, packets, timestamp) '
                'VALUES (?, ?, ?, ?, ?)',
                (mac, associated_bssid, signal, packets, timestamp)
            )
            conn.commit()
        self.devices[mac] = {
            'mac': mac,
            'associated_bssid': associated_bssid,
            'signal': signal,
            'packets': packets,
            'timestamp': timestamp
        }

    def setup_monitor_mode(self):
        """Set wireless interface to monitor mode."""
        logger.info(f"Setting {self.interface} to monitor mode")
        try:
            subprocess.check_call(['airmon-ng', 'check', 'kill'], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call(['airmon-ng', 'start', self.interface], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.interface = f"{self.interface}mon"
            if self.channel > 0:
                subprocess.check_call(['iwconfig', self.interface, 'channel', str(self.channel)], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Monitor mode enabled")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable monitor mode: {e}")
            sys.exit(1)

    def packet_handler(self, pkt):
        """Process captured packets."""
        if not self.running:
            return
        
        if pkt.haslayer(Dot11Beacon):
            bssid = pkt[Dot11].addr2
            if bssid:
                ssid = pkt[Dot11Elt].info.decode('utf-8', errors='ignore') or '<hidden>'
                channel = int(ord(pkt[Dot11Elt:3].info)) if pkt[Dot11Elt:3] else 0
                signal = pkt[RadioTap].dBm_AntSignal if pkt[RadioTap].dBm_AntSignal else -100
                encryption = 'OPEN'
                if pkt[Dot11Beacon].network_stats().get('crypto'):
                    encryption = '/'.join(pkt[Dot11Beacon].network_stats()['crypto'])
                packets = self.networks.get(bssid, {}).get('packets', 0) + 1
                
                if signal >= self.min_power:
                    self.store_network(ssid, bssid, channel, signal, encryption, packets)
                    logger.info(f"Network: SSID={ssid}, BSSID={bssid}, Channel={channel}, Signal={signal}dBm")

        elif pkt.haslayer(Dot11):
            src = pkt[Dot11].addr2
            dst = pkt[Dot11].addr1
            if src and src != 'ff:ff:ff:ff:ff:ff':
                associated_bssid = pkt[Dot11].addr3 if pkt[Dot11].type == 2 else ''
                signal = pkt[RadioTap].dBm_AntSignal if pkt[RadioTap].dBm_AntSignal else -100
                packets = self.devices.get(src, {}).get('packets', 0) + 1
                
                if signal >= self.min_power:
                    self.store_device(src, associated_bssid, signal, packets)
                    logger.info(f"Device: MAC={src}, Associated BSSID={associated_bssid}, Signal={signal}dBm")

        if self.capture and self.cap_file:
            wrpcap(self.cap_file, pkt, append=True)

    def channel_hopper(self):
        """Hop between channels (1-13) for scanning."""
        if self.channel > 0:
            return
        while self.running:
            for ch in range(1, 14):
                try:
                    subprocess.check_call(['iwconfig', self.interface, 'channel', str(ch)], 
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(0.2)
                except subprocess.CalledProcessError:
                    logger.warning(f"Failed to switch to channel {ch}")
                if not self.running:
                    break

    def scan_networks(self):
        """Start packet sniffing and channel hopping."""
        logger.info("Starting network and device scanning")
        hopper_thread = threading.Thread(target=self.channel_hopper)
        hopper_thread.daemon = True
        hopper_thread.start()

        try:
            sniff(iface=self.interface, prn=self.packet_handler, store=0)
        except Exception as e:
            logger.error(f"Error during sniffing: {e}")
            self.running = False

    def save_results(self):
        """Save results to files."""
        with open(self.output_file, 'a') as f:
            f.write("=== NetSentry Results ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Networks:\n")
            for net in self.networks.values():
                f.write(f"SSID: {net['ssid']}, BSSID: {net['bssid']}, "
                        f"Channel: {net['channel']}, Signal: {net['signal']}dBm, "
                        f"Encryption: {net['encryption']}, Packets: {net['packets']}\n")
            f.write("\nDevices:\n")
            for dev in self.devices.values():
                f.write(f"MAC: {dev['mac']}, Associated BSSID: {dev['associated_bssid']}, "
                        f"Signal: {dev['signal']}dBm, Packets: {dev['packets']}\n")
        
        with open(self.json_file, 'w') as f:
            json.dump({
                'interface': self.interface,
                'channel': self.channel,
                'networks': list(self.networks.values()),
                'devices': list(self.devices.values()),
                'capture_file': self.cap_file if self.capture else None,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

    def run(self):
        """Run NetSentry scanning tool."""
        logger.info("Starting NetSentry")
        self.setup_monitor_mode()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.submit(self.scan_networks)
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("NetSentry stopped by user")
                self.running = False
        
        self.save_results()
        self.cleanup()

    def cleanup(self):
        """Clean up monitor mode."""
        logger.info("Cleaning up")
        try:
            subprocess.check_call(['airmon-ng', 'stop', self.interface], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass

def main():
    parser = argparse.ArgumentParser(
        description="NetSentry: Wireless network and device scanner.",
        epilog="Example: ./netsentry.py -i wlan0 --capture --min-power -80 -T 5"
    )
    parser.add_argument('-i', '--interface', required=True, 
                       help="Wireless interface (e.g., wlan0)")
    parser.add_argument('-c', '--channel', type=int, default=0, 
                       help="Channel to scan (default: all)")
    parser.add_argument('--min-power', type=int, default=-100, 
                       help="Minimum signal strength in dBm (default: -100)")
    parser.add_argument('--capture', action='store_true', 
                       help="Capture packets to PCAP file")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         NetSentry v1.0
      Wireless Network Scanner
    ==============================
    """)

    try:
        netsentry = NetSentry(
            interface=args.interface,
            channel=args.channel,
            min_power=args.min_power,
            capture=args.capture,
            threads=args.threads,
            quiet=args.quiet
        )
        netsentry.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()