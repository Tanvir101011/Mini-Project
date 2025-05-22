import argparse
import logging
import sys
import time
import binascii
from datetime import datetime
from scapy.all import sniff, sendp, Raw, IP, TCP, UDP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('packetcraft.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class PacketCraft:
    def __init__(self, interface=None, filter_ip=None, filter_port=None, max_packets=100, inject_payload=None, inject_count=1, quiet=False):
        self.interface = interface
        self.filter_ip = filter_ip
        self.filter_port = filter_port
        self.max_packets = max_packets
        self.inject_payload = inject_payload
        self.inject_count = inject_count
        self.quiet = quiet
        self.packet_count = 0
        self.captured_packets = []
        self.output_file = f"packetcraft_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    def process_packet(self, packet):
        """Process sniffed packets and log in hex format."""
        if self.packet_count >= self.max_packets:
            return False  # Stop sniffing

        try:
            if self.filter_ip and self.filter_ip not in (packet[IP].src, packet[IP].dst):
                return
            if self.filter_port and packet.haslayer(TCP) and self.filter_port not in (packet[TCP].sport, packet[TCP].dport):
                return
            if self.filter_port and packet.haslayer(UDP) and self.filter_port not in (packet[UDP].sport, packet[UDP].dport):
                return

            raw_data = bytes(packet)
            hex_data = binascii.hexlify(raw_data).decode('utf-8')
            packet_info = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'src_ip': packet[IP].src if packet.haslayer(IP) else 'unknown',
                'dst_ip': packet[IP].dst if packet.haslayer(IP) else 'unknown',
                'hex_data': hex_data
            }
            self.captured_packets.append(packet_info)
            logging.info(f"Captured packet: {packet_info['src_ip']} -> {packet_info['dst_ip']}, {len(hex_data)//2} bytes")

            with open(self.output_file, 'a') as f:
                f.write(f"[{packet_info['timestamp']}] {packet_info['src_ip']} -> {packet_info['dst_ip']}\n")
                f.write(f"Hex: {hex_data}\n")
                f.write(f"{'-'*50}\n")

            self.packet_count += 1
        except Exception as e:
            logging.error(f"Error processing packet: {str(e)}")

    def inject_packet(self):
        """Inject custom packet with user-defined payload."""
        try:
            if not self.inject_payload:
                logging.error("No payload specified for injection")
                return

            # Convert payload (hex or ASCII)
            try:
                if self.inject_payload.startswith('0x'):
                    payload = binascii.unhexlify(self.inject_payload[2:])
                else:
                    payload = self.inject_payload.encode('utf-8')
            except Exception as e:
                logging.error(f"Invalid payload format: {str(e)}")
                return

            # Create a simple IP/TCP packet with the payload
            packet = IP(dst="127.0.0.1")/TCP(dport=80)/Raw(load=payload)
            for _ in range(self.inject_count):
                sendp(packet, iface=self.interface, verbose=0)
                logging.info(f"Injected packet: {len(payload)} bytes to 127.0.0.1:80")
                time.sleep(0.1)  # Avoid flooding
        except Exception as e:
            logging.error(f"Error injecting packet: {str(e)}")

    def start(self):
        """Start sniffing or injecting packets."""
        logging.info(f"Starting PacketCraft: Interface={self.interface or 'any'}, FilterIP={self.filter_ip or 'all'}, FilterPort={self.filter_port or 'all'}, MaxPackets={self.max_packets}")
        
        if self.inject_payload:
            self.inject_packet()
        else:
            filter_str = "ip" + (f" and port {self.filter_port}" if self.filter_port else "")
            try:
                sniff(
                    iface=self.interface,
                    filter=filter_str,
                    prn=self.process_packet,
                    store=0,
                    stop_filter=lambda x: self.packet_count >= self.max_packets
                )
            except Exception as e:
                logging.error(f"Error during sniffing: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="PacketCraft - A tool to sniff and inject network packets for learning.")
    parser.add_argument('-i', '--interface', help='Network interface (e.g., eth0)')
    parser.add_argument('-f', '--filter-ip', help='Filter by source or destination IP')
    parser.add_argument('-p', '--filter-port', type=int, help='Filter by source or destination port')
    parser.add_argument('-m', '--max-packets', type=int, default=100, help='Max packets to capture (default: 100)')
    parser.add_argument('-j', '--inject-payload', help='Payload to inject (hex with 0x prefix or ASCII)')
    parser.add_argument('-c', '--inject-count', type=int, default=1, help='Number of packets to inject (default: 1)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('packetcraft.log')]

    crafter = PacketCraft(
        interface=args.interface,
        filter_ip=args.filter_ip,
        filter_port=args.filter_port,
        max_packets=args.max_packets,
        inject_payload=args.inject_payload,
        inject_count=args.inject_count,
        quiet=args.quiet
    )

    try:
        crafter.start()
    except KeyboardInterrupt:
        logging.info("PacketCraft stopped")

if __name__ == "__main__":
    main()