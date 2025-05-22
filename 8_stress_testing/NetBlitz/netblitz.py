#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from scapy.all import Raw, sendp
from scapy.layers.inet import IP, TCP, UDP, ICMP
import random
import socket
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netblitz.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NetBlitz:
    def __init__(self, target_ip: str, target_port: int = 80, protocol: str = 'TCP',
                 packet_rate: int = 100, duration: int = 10, threads: int = 5,
                 quiet: bool = False):
        self.target_ip = target_ip
        self.target_port = target_port
        self.protocol = protocol.upper()
        self.packet_rate = packet_rate
        self.duration = duration
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'netblitz-output'
        self.output_file = os.path.join(self.output_dir,
            f"blitz_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir,
            f"blitz_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'netblitz.db')
        self.interface = 'eth0'  # Default to eth0 per lab setup
        os.makedirs(self.output_dir, exist_ok=True)
        self.actions = []
        self.running = True
        self.packets_sent = 0
        self.lock = threading.Lock()
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('netblitz.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_ip TEXT,
                    target_port INTEGER,
                    protocol TEXT,
                    packet_rate INTEGER,
                    packets_sent INTEGER,
                    status TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, packets_sent: int, status: str):
        """Store action details in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (target_ip, target_port, protocol, packet_rate, packets_sent, status, timestamp) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (self.target_ip, self.target_port, self.protocol, self.packet_rate, packets_sent, status, timestamp)
            )
            conn.commit()
        self.actions.append({
            'target_ip': self.target_ip,
            'target_port': self.target_port,
            'protocol': self.protocol,
            'packet_rate': self.packet_rate,
            'packets_sent': packets_sent,
            'status': status,
            'timestamp': timestamp
        })

    def craft_packet(self):
        """Craft a packet based on specified protocol."""
        try:
            src_ip = socket.gethostbyname(socket.gethostname())
            packet = IP(dst=self.target_ip, src=src_ip)
            if self.protocol == 'TCP':
                packet = packet / TCP(sport=random.randint(1024, 65535),
                                     dport=self.target_port, flags='S') / Raw(load=b'\x00' * 20)
            elif self.protocol == 'UDP':
                packet = packet / UDP(sport=random.randint(1024, 65535),
                                     dport=self.target_port) / Raw(load=b'\x00' * 20)
            elif self.protocol == 'ICMP':
                packet = packet / ICMP(type=8, code=0) / Raw(load=b'\x00' * 20)
            else:
                raise ValueError(f"Unsupported protocol: {self.protocol}")
            return packet
        except Exception as e:
            logger.error(f"Failed to craft packet: {e}")
            return None

    def flood_target(self):
        """Send packets to the target at specified rate."""
        start_time = time.time()
        packets_sent_local = 0
        try:
            while self.running and (time.time() - start_time) < self.duration:
                packet = self.craft_packet()
                if packet:
                    sendp(packet, iface=self.interface, verbose=False)
                    with self.lock:
                        packets_sent_local += 1
                        self.packets_sent += 1
                time.sleep(1.0 / self.packet_rate)
            status = f"Sent {packets_sent_local} {self.protocol} packets to {self.target_ip}:{self.target_port}"
            logger.info(status)
            self.store_action(packets_sent_local, status)
        except Exception as e:
            status = f"Flood failed: {e}"
            logger.error(status)
            self.store_action(packets_sent_local, status)

    def run(self):
        """Run NetBlitz to flood the target."""
        logger.info(f"Starting NetBlitz against {self.target_ip}:{self.target_port} with {self.protocol}")
        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [executor.submit(self.flood_target) for _ in range(self.threads)]
                start_time = time.time()
                while self.running and (time.time() - start_time) < self.duration:
                    time.sleep(1)
                self.running = False
                for future in futures:
                    future.result()
        except KeyboardInterrupt:
            logger.info("NetBlitz stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error: {e}")
            self.running = False
        finally:
            self.save_results()

    def save_results(self):
        """Save action logs to files."""
        with open(self.output_file, 'a') as f:
            f.write("=== NetBlitz Results ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for action in self.actions:
                f.write(f"[{action['timestamp']}] {action['status']}, "
                        f"Target={action['target_ip']}:{action['target_port']}, "
                        f"Protocol={action['protocol']}, Rate={action['packet_rate']}, "
                        f"Packets={action['packets_sent']}\n")
        
        with open(self.json_file, 'w') as f:
            json.dump({
                'target_ip': self.target_ip,
                'target_port': self.target_port,
                'protocol': self.protocol,
                'packet_rate': self.packet_rate,
                'duration': self.duration,
                'total_packets_sent': self.packets_sent,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="NetBlitz: Tool to simulate packet floods for network stress testing.",
        epilog="Example: sudo ./netblitz.py -t 192.168.1.100 -p 80 -P TCP -r 100 -d 10"
    )
    parser.add_argument('-t', '--target-ip', required=True,
                        help="Target IP address of network device")
    parser.add_argument('-p', '--target-port', type=int, default=80,
                        help="Target port (default: 80)")
    parser.add_argument('-P', '--protocol', choices=['TCP', 'UDP', 'ICMP'], default='TCP',
                        help="Protocol to use (TCP, UDP, ICMP; default: TCP)")
    parser.add_argument('-r', '--packet-rate', type=int, default=100,
                        help="Packets per second per thread (default: 100)")
    parser.add_argument('-d', '--duration', type=int, default=10,
                        help="Flood duration in seconds (default: 10)")
    parser.add_argument('-T', '--threads', type=int, default=5,
                        help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
           NetBlitz v1.0
      Network Stress Tester
    ==============================
    """)

    try:
        blitz = NetBlitz(
            target_ip=args.target_ip,
            target_port=args.target_port,
            protocol=args.protocol,
            packet_rate=args.packet_rate,
            duration=args.duration,
            threads=args.threads,
            quiet=args.quiet
        )
        blitz.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()