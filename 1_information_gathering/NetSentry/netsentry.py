import argparse
import logging
import socket
import sys
import time
from datetime import datetime
from scapy.all import IP, TCP, UDP, sr1, ICMP

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('netsentry.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class NetSentry:
    def __init__(self, gateway, target, ports, protocol='TCP', ttl=64, quiet=False):
        self.gateway = gateway
        self.target = target
        self.ports = self.parse_ports(ports)
        self.protocol = protocol.upper()
        self.ttl = ttl
        self.quiet = quiet
        self.results = []

    def parse_ports(self, ports):
        """Parse port range or list (e.g., '80-85' or '80,443')."""
        if '-' in ports:
            start, end = map(int, ports.split('-'))
            return list(range(start, end + 1))
        return [int(p) for p in ports.split(',')]

    def send_probe(self, port):
        """Send a probe packet and check response."""
        try:
            packet = IP(dst=self.target, ttl=self.ttl)
            if self.protocol == 'TCP':
                packet /= TCP(dport=port, flags='S')
            elif self.protocol == 'UDP':
                packet /= UDP(dport=port)
            else:
                raise ValueError("Unsupported protocol")

            response = sr1(packet, timeout=2, verbose=0)
            result = {
                'port': port,
                'protocol': self.protocol,
                'status': 'unknown',
                'response': 'no_response'
            }

            if response:
                if response.haslayer(ICMP) and response[ICMP].type == 11:
                    result['status'] = 'allowed'
                    result['response'] = 'gateway_passed'
                elif response.haslayer(TCP) or response.haslayer(UDP):
                    result['status'] = 'allowed'
                    result['response'] = 'direct_response'
                else:
                    result['status'] = 'blocked'
                    result['response'] = 'other_response'
            else:
                result['status'] = 'blocked'

            self.results.append(result)
            logging.info(f"Port {port}/{self.protocol}: {result['status']} ({result['response']})")

        except Exception as e:
            logging.error(f"Error probing port {port}/{self.protocol}: {str(e)}")
            self.results.append({
                'port': port,
                'protocol': self.protocol,
                'status': 'error',
                'response': str(e)
            })

    def start(self):
        """Start probing ports."""
        logging.info(f"Starting NetSentry: Gateway={self.gateway}, Target={self.target}, Ports={self.ports}")
        for port in self.ports:
            self.send_probe(port)
            time.sleep(0.2)  # Avoid overwhelming the network

        # Save results to text file
        output_file = f"netsentry_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w') as f:
            for result in self.results:
                f.write(f"Port {result['port']}/{result['protocol']}: {result['status']} ({result['response']})\n")
        logging.info(f"Results saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="NetSentry - A tool to explore network port behavior.")
    parser.add_argument('gateway', help='Gateway IP address')
    parser.add_argument('target', help='Target IP address')
    parser.add_argument('-p', '--ports', required=True, help='Ports to probe (e.g., 80-85 or 80,443)')
    parser.add_argument('-P', '--protocol', choices=['TCP', 'UDP'], default='TCP', help='Protocol (default: TCP)')
    parser.add_argument('-t', '--ttl', type=int, default=64, help='Time to live (default: 64)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('netsentry.log')]

    sentry = NetSentry(
        gateway=args.gateway,
        target=args.target,
        ports=args.ports,
        protocol=args.protocol,
        ttl=args.ttl,
        quiet=args.quiet
    )

    try:
        sentry.start()
    except KeyboardInterrupt:
        logging.info("NetSentry stopped")

if __name__ == "__main__":
    main()