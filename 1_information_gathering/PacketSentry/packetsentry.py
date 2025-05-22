import argparse
import logging
import sys
import time
from datetime import datetime
from scapy.all import sniff, rdpcap, wrpcap, IP, TCP, UDP, DNS, HTTP
from scapy.error import Scapy_Exception

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('packetsentry.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class PacketSentry:
    def __init__(self, interface=None, pcap_file=None, filter_protocol=None, filter_ip=None, filter_port=None, output_pcap=None, count=0, quiet=False):
        self.interface = interface
        self.pcap_file = pcap_file
        self.filter_protocol = filter_protocol.lower() if filter_protocol else None
        self.filter_ip = filter_ip
        self.filter_port = int(filter_port) if filter_port else None
        self.output_pcap = output_pcap
        self.count = int(count) if count else 0
        self.quiet = quiet
        self.results = []
        self.output_file = f"packetsentry_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    def build_filter(self):
        """Build a Scapy filter string based on user inputs."""
        filters = []
        if self.filter_protocol:
            if self.filter_protocol in ['tcp', 'udp']:
                filters.append(self.filter_protocol)
            elif self.filter_protocol == 'http':
                filters.append('tcp port 80 or tcp port 443')
            elif self.filter_protocol == 'dns':
                filters.append('udp port 53')
        if self.filter_ip:
            filters.append(f"host {self.filter_ip}")
        if self.filter_port:
            filters.append(f"port {self.filter_port}")
        return ' and '.join(filters) if filters else None

    def analyze_packet(self, packet):
        """Analyze a single packet and extract relevant information."""
        result = {'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'protocol': 'unknown', 'src': '', 'dst': '', 'summary': ''}

        try:
            # Extract IP layer information
            if packet.haslayer(IP):
                result['src'] = packet[IP].src
                result['dst'] = packet[IP].dst

            # Identify protocol
            if packet.haslayer(TCP):
                result['protocol'] = 'TCP'
                result['summary'] = f"TCP {packet[TCP].sport} -> {packet[TCP].dport}"
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    if packet.haslayer(HTTP):
                        result['protocol'] = 'HTTP'
                        result['summary'] += f" {packet[HTTP].method or packet[HTTP].path or 'HTTP'}"
            elif packet.haslayer(UDP):
                result['protocol'] = 'UDP'
                result['summary'] = f"UDP {packet[UDP].sport} -> {packet[UDP].dport}"
                if packet[UDP].dport == 53 or packet[UDP].sport == 53:
                    if packet.haslayer(DNS):
                        result['protocol'] = 'DNS'
                        result['summary'] += f" {packet[DNS].qname.decode() if packet[DNS].qname else 'DNS'}"
            else:
                result['summary'] = f"Other protocol (len={len(packet)})"

            # Apply filters
            if self.filter_protocol and self.filter_protocol.lower() not in result['protocol'].lower():
                return None
            if self.filter_ip and self.filter_ip not in (result['src'], result['dst']):
                return None
            if self.filter_port and packet.haslayer(TCP) and self.filter_port not in (packet[TCP].sport, packet[TCP].dport):
                return None
            if self.filter_port and packet.haslayer(UDP) and self.filter_port not in (packet[UDP].sport, packet[UDP].dport):
                return None

            return result
        except Exception as e:
            logging.error(f"Error analyzing packet: {str(e)}")
            return None

    def process_packet(self, packet):
        """Process a captured packet."""
        result = self.analyze_packet(packet)
        if result:
            self.results.append(result)
            if not self.quiet:
                logging.info(f"{result['timestamp']} {result['protocol']} {result['src']} -> {result['dst']} {result['summary']}")

    def save_results(self):
        """Save analysis results to a file."""
        with open(self.output_file, 'w') as f:
            for result in self.results:
                f.write(f"[{result['timestamp']}] {result['protocol']}\n")
                f.write(f"Source: {result['src']} -> Destination: {result['dst']}\n")
                f.write(f"Summary: {result['summary']}\n")
                f.write(f"{'-'*50}\n")
        logging.info(f"Results saved to {self.output_file}")

    def save_pcap(self, packets):
        """Save captured packets to a PCAP file."""
        if self.output_pcap and packets:
            try:
                wrpcap(self.output_pcap, packets)
                logging.info(f"Packets saved to {self.output_pcap}")
            except Exception as e:
                logging.error(f"Error saving PCAP: {str(e)}")

    def start(self):
        """Start packet capture or analysis."""
        packets = []
        try:
            if self.pcap_file:
                # Read from PCAP file
                logging.info(f"Reading packets from {self.pcap_file}")
                packets = rdpcap(self.pcap_file)
                for packet in packets:
                    self.process_packet(packet)
            else:
                # Capture live packets
                if not self.interface:
                    logging.error("No interface specified for live capture")
                    return
                scapy_filter = self.build_filter()
                logging.info(f"Starting capture on {self.interface} (filter: {scapy_filter or 'none'})")
                sniff(iface=self.interface, filter=scapy_filter, prn=self.process_packet, count=self.count, store=1, prn_store=packets.append)

            # Save results and packets
            self.save_results()
            self.save_pcap(packets)
        except Scapy_Exception as e:
            logging.error(f"Scapy error: {str(e)}")
        except KeyboardInterrupt:
            logging.info("PacketSentry stopped by user")
            self.save_results()
            self.save_pcap(packets)
        except Exception as e:
            logging.error(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="PacketSentry - A tool to capture and analyze network packets for learning.")
    parser.add_argument('-i', '--interface', help='Network interface for live capture (e.g., eth0)')
    parser.add_argument('-r', '--pcap-file', help='PCAP file to read packets from')
    parser.add_argument('-f', '--filter-protocol', help='Filter by protocol (e.g., tcp, udp, http, dns)')
    parser.add_argument('--filter-ip', help='Filter by source or destination IP')
    parser.add_argument('--filter-port', help='Filter by source or destination port')
    parser.add_argument('-o', '--output-pcap', help='Output PCAP file to save captured packets')
    parser.add_argument('-c', '--count', default=0, help='Number of packets to capture (0 for unlimited, default: 0)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    if not args.interface and not args.pcap_file:
        logging.error("Must specify either an interface (-i) or a PCAP file (-r)")
        sys.exit(1)

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('packetsentry.log')]

    sentry = PacketSentry(
        interface=args.interface,
        pcap_file=args.pcap_file,
        filter_protocol=args.filter_protocol,
        filter_ip=args.filter_ip,
        filter_port=args.filter_port,
        output_pcap=args.output_pcap,
        count=args.count,
        quiet=args.quiet
    )

    try:
        sentry.start()
    except KeyboardInterrupt:
        logging.info("PacketSentry stopped by user")

if __name__ == "__main__":
    main()