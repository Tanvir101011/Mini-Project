#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import socket
import threading
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import struct
import select

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('natpiercer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NatPiercer:
    def __init__(self, mode: str, local_ip: str = '0.0.0.0', local_port: int = 2222,
                 proxy_host: str = None, proxy_port: int = 2222, remote_host: str = None,
                 remote_port: int = None, threads: int = 5, quiet: bool = False):
        self.mode = mode
        self.local_ip = local_ip
        self.local_port = local_port
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'natpiercer-output'
        self.output_file = os.path.join(self.output_dir, 
            f"piercer_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"piercer_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'natpiercer.db')
        os.makedirs(self.output_dir, exist_ok=True)
        self.connections = []
        self.running = True
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('natpiercer.log')]

    def init_db(self):
        """Initialize SQLite database for storing connection logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT,
                    local_ip TEXT,
                    local_port INTEGER,
                    proxy_host TEXT,
                    proxy_port INTEGER,
                    remote_host TEXT,
                    remote_port INTEGER,
                    status TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_connection(self, status: str):
        """Store connection details in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO connections (mode, local_ip, local_port, proxy_host, proxy_port, '
                'remote_host, remote_port, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (self.mode, self.local_ip, self.local_port, self.proxy_host, self.proxy_port,
                 self.remote_host, self.remote_port, status, timestamp)
            )
            conn.commit()
        self.connections.append({
            'mode': self.mode,
            'local_ip': self.local_ip,
            'local_port': self.local_port,
            'proxy_host': self.proxy_host,
            'proxy_port': self.proxy_port,
            'remote_host': self.remote_host,
            'remote_port': self.remote_port,
            'status': status,
            'timestamp': timestamp
        })

    def create_udp_socket(self):
        """Create and bind UDP socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.local_ip, self.local_port))
        sock.setblocking(False)
        return sock

    def keep_alive(self, sock: socket.socket, dest_addr: tuple):
        """Send keep-alive packets to maintain NAT mappings."""
        while self.running:
            try:
                sock.sendto(b'KA', dest_addr)
                time.sleep(5)
            except Exception as e:
                logger.error(f"Keep-alive error: {e}")
                break

    def server_mode(self):
        """Run in server mode, accepting client connections."""
        logger.info(f"Starting server on {self.local_ip}:{self.local_port}")
        sock = self.create_udp_socket()
        self.store_connection('Server started')

        # Start keep-alive thread (send to a dummy address, e.g., 1.2.3.4)
        keep_alive_thread = threading.Thread(
            target=self.keep_alive, args=(sock, ('1.2.3.4', self.proxy_port))
        )
        keep_alive_thread.daemon = True
        keep_alive_thread.start()

        clients = {}
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while self.running:
                readable, _, _ = select.select([sock], [], [], 1.0)
                if not readable:
                    continue

                try:
                    data, addr = sock.recvfrom(1024)
                    client_id = f"{addr[0]}:{addr[1]}"

                    if data == b'KA':
                        clients[client_id] = addr
                        logger.info(f"Keep-alive from {client_id}")
                        continue

                    if client_id not in clients:
                        logger.info(f"New client: {client_id}")
                        clients[client_id] = addr
                        self.store_connection(f"Client connected: {client_id}")

                    # Forward data to remote host if specified
                    if self.remote_host and self.remote_port:
                        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:
                            tcp_sock.connect((self.remote_host, self.remote_port))
                            tcp_sock.sendall(data)
                            response = tcp_sock.recv(4096)
                            sock.sendto(response, addr)
                        except Exception as e:
                            logger.error(f"Error forwarding to {self.remote_host}:{self.remote_port}: {e}")
                        finally:
                            tcp_sock.close()
                except Exception as e:
                    logger.error(f"Server error: {e}")

        sock.close()

    def client_mode(self):
        """Run in client mode, connecting to server."""
        logger.info(f"Starting client on {self.local_ip}:{self.local_port} to {self.proxy_host}:{self.proxy_port}")
        sock = self.create_udp_socket()
        self.store_connection('Client started')

        # Start keep-alive thread
        keep_alive_thread = threading.Thread(
            target=self.keep_alive, args=(sock, (self.proxy_host, self.proxy_port))
        )
        keep_alive_thread.daemon = True
        keep_alive_thread.start()

        # Connect to remote host via proxy
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            while self.running:
                try:
                    # Send data to proxy
                    sock.sendto(b'INIT', (self.proxy_host, self.proxy_port))
                    readable, _, _ = select.select([sock], [], [], 5.0)
                    if not readable:
                        continue

                    data, addr = sock.recvfrom(4096)
                    if data == b'KA':
                        logger.info(f"Keep-alive from server {addr}")
                        continue

                    # Handle response
                    logger.info(f"Received data from {addr}: {len(data)} bytes")
                    self.store_connection(f"Data received from {addr}")

                    # Forward to local TCP service if specified
                    if self.remote_host and self.remote_port:
                        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:
                            tcp_sock.connect((self.remote_host, self.remote_port))
                            tcp_sock.sendall(data)
                            response = tcp_sock.recv(4096)
                            sock.sendto(response, (self.proxy_host, self.proxy_port))
                        except Exception as e:
                            logger.error(f"Error forwarding to {self.remote_host}:{self.remote_port}: {e}")
                        finally:
                            tcp_sock.close()
                except Exception as e:
                    logger.error(f"Client error: {e}")

        sock.close()

    def run(self):
        """Run NatPiercer in specified mode."""
        logger.info("Starting NatPiercer")
        try:
            if self.mode == 'server':
                self.server_mode()
            elif self.mode == 'client':
                if not self.proxy_host or not self.remote_host or not self.remote_port:
                    logger.error("Client mode requires proxy_host, remote_host, and remote_port")
                    sys.exit(1)
                self.client_mode()
            else:
                logger.error("Invalid mode. Use 'server' or 'client'")
                sys.exit(1)
        finally:
            self.save_results()

    def save_results(self):
        """Save connection logs to files."""
        with open(self.output_file, 'a') as f:
            f.write("=== NatPiercer Results ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for conn in self.connections:
                f.write(f"[{conn['timestamp']}] {conn['mode']}: {conn['status']}, "
                        f"Local={conn['local_ip']}:{conn['local_port']}, "
                        f"Proxy={conn['proxy_host']}:{conn['proxy_port']}, "
                        f"Remote={conn['remote_host']}:{conn['remote_port']}\n")
        
        with open(self.json_file, 'w') as f:
            json.dump({
                'mode': self.mode,
                'local_ip': self.local_ip,
                'local_port': self.local_port,
                'proxy_host': self.proxy_host,
                'proxy_port': self.proxy_port,
                'remote_host': self.remote_host,
                'remote_port': self.remote_port,
                'connections': self.connections,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="NatPiercer: NAT traversal tool for direct communication.",
        epilog="Example: ./natpiercer.py -s -p 8080 (server) or "
               "./natpiercer.py -c 127.0.0.1 8000 192.168.1.202 8080 google.com 80 (client)"
    )
    parser.add_argument('-m', '--mode', required=True, choices=['server', 'client'],
                       help="Mode: server or client")
    parser.add_argument('-l', '--local-ip', default='0.0.0.0',
                       help="Local IP address (default: 0.0.0.0)")
    parser.add_argument('-p', '--local-port', type=int, default=2222,
                       help="Local port (default: 2222)")
    parser.add_argument('--proxy-host', help="Proxy server host (client mode)")
    parser.add_argument('--proxy-port', type=int, default=2222,
                       help="Proxy server port (default: 2222)")
    parser.add_argument('--remote-host', help="Remote host to connect to (client mode)")
    parser.add_argument('--remote-port', type=int, help="Remote port (client mode)")
    parser.add_argument('-T', '--threads', type=int, default=5,
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true',
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         NatPiercer v1.0
      NAT Traversal Tool
    ==============================
    """)

    try:
        piercer = NatPiercer(
            mode=args.mode,
            local_ip=args.local_ip,
            local_port=args.local_port,
            proxy_host=args.proxy_host,
            proxy_port=args.proxy_port,
            remote_host=args.remote_host,
            remote_port=args.remote_port,
            threads=args.threads,
            quiet=args.quiet
        )
        piercer.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()