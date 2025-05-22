#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import json
import sqlite3
import time
import socket
import redis
import pylibmc
import etcd3
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keyvalue_assess.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KeyValueAssess:
    def __init__(self, db_type: str, host: str, port: int, password: Optional[str] = None,
                 output_dir: str = 'keyvalue_assess-output', quiet: bool = False):
        self.db_type = db_type.lower()
        self.host = host
        self.port = port
        self.password = password
        self.output_dir = os.path.abspath(output_dir)
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"keyvalue_assess_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'keyvalue_assess.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.results = []
        self.actions = []
        self.conn = None
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('keyvalue_assess.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    db_type TEXT,
                    host TEXT,
                    port INTEGER,
                    action TEXT,
                    status TEXT,
                    output_path TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, action: str, status: str, output_path: str = ''):
        """Store action details in database."""
        timestamp = datetime.now().strftime('%Y-%m-d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (db_type, host, port, action, status, output_path, timestamp) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (self.db_type, self.host, self.port, action, status, output_path, timestamp)
            )
            conn.commit()
        self.actions.append({
            'db_type': self.db_type,
            'host': self.host,
            'port': self.port,
            'action': action,
            'status': status,
            'output_path': output_path,
            'timestamp': timestamp
        })

    def check_port_open(self) -> bool:
        """Check if the database port is open."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            if result == 0:
                status = f"Port {self.port} is open on {self.host}"
                logger.info(status)
                self.store_action("Check Port", status)
                return True
            else:
                status = f"Port {self.port} is closed on {self.host}"
                logger.warning(status)
                self.store_action("Check Port", status)
                return False
        except Exception as e:
            status = f"Port check failed: {e}"
            logger.error(status)
            self.store_action("Check Port", status)
            return False

    def connect_db(self):
        """Connect to the key-value database."""
        try:
            if self.db_type == 'redis':
                self.conn = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    decode_responses=True
                )
                self.conn.ping()
            elif self.db_type == 'memcached':
                self.conn = pylibmc.Client(
                    [f"{self.host}:{self.port}"],
                    binary=True
                )
                self.conn.set('test_key', 'test_value')  # Test connection
                self.conn.get('test_key')
            elif self.db_type == 'etcd':
                self.conn = etcd3.client(
                    host=self.host,
                    port=self.port
                )
                self.conn.put('/test', 'test_value')  # Test connection
                self.conn.get('/test')
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            status = f"Connected to {self.db_type} database at {self.host}:{self.port}"
            logger.info(status)
            self.store_action("Connect", status)
        except (redis.RedisError, pylibmc.Error, etcd3.exceptions.Etcd3Exception) as e:
            status = f"Connection failed: {e}"
            logger.error(status)
            self.store_action("Connect", status)
            self.conn = None

    def check_default_credentials(self):
        """Check for default or weak credentials."""
        default_creds = {
            'redis': [None, 'redis', ''],
            'memcached': [None],  # Memcached typically has no auth
            'etcd': [None]  # etcd uses auth tokens or no auth by default
        }
        weak = default_creds.get(self.db_type, [])
        if not weak:
            return

        for pwd in weak:
            try:
                if self.db_type == 'redis':
                    conn = redis.Redis(
                        host=self.host,
                        port=self.port,
                        password=pwd,
                        decode_responses=True
                    )
                    conn.ping()
                    conn.close()
                    status = f"Default/weak credentials found: {pwd if pwd else 'no password'}"
                    logger.warning(status)
                    self.results.append({'check': 'Default Credentials', 'status': 'Vulnerable', 'details': status})
                    self.store_action("Check Default Credentials", status)
                elif self.db_type in ['memcached', 'etcd']:
                    # Memcached and etcd without auth are checked in authentication
                    pass
            except redis.RedisError:
                pass

    def check_version(self):
        """Check database version for known vulnerabilities."""
        try:
            if not self.conn:
                self.connect_db()
            if not self.conn:
                return

            version = ''
            if self.db_type == 'redis':
                version = self.conn.info()['redis_version']
            elif self.db_type == 'memcached':
                stats = self.conn.get_stats()
                version = stats[0][1].get('version', 'unknown') if stats else 'unknown'
            elif self.db_type == 'etcd':
                status = self.conn.status()
                version = status.version

            # Simplified version check (real-world would query CVE database)
            vulnerable_versions = {
                'redis': ['5.0', '6.0'],
                'memcached': ['1.5', '1.4'],
                'etcd': ['3.3', '3.4']
            }
            is_vulnerable = any(v in version for v in vulnerable_versions.get(self.db_type, [])) if version != 'unknown' else False
            status = f"Database version: {version} {'(potentially vulnerable)' if is_vulnerable else ''}"
            logger.info(status)
            self.results.append({
                'check': 'Version Check',
                'status': 'Vulnerable' if is_vulnerable else 'OK',
                'details': status
            })
            self.store_action("Check Version", status)
        except Exception as e:
            status = f"Version check failed: {e}"
            logger.error(status)
            self.store_action("Check Version", status)

    def check_authentication(self):
        """Check if authentication is enabled."""
        try:
            if self.db_type == 'redis' and not self.password:
                conn = redis.Redis(
                    host=self.host,
                    port=self.port,
                    decode_responses=True
                )
                conn.ping()
                conn.close()
                status = "No authentication configured for Redis"
                logger.warning(status)
                self.results.append({'check': 'Authentication Check', 'status': 'Vulnerable', 'details': status})
                self.store_action("Check Authentication", status)
            elif self.db_type == 'memcached':
                conn = pylibmc.Client([f"{self.host}:{self.port}"], binary=True)
                conn.set('test_key', 'test_value')
                conn.get('test_key')
                status = "No authentication configured for Memcached"
                logger.warning(status)
                self.results.append({'check': 'Authentication Check', 'status': 'Vulnerable', 'details': status})
                self.store_action("Check Authentication", status)
            elif self.db_type == 'etcd':
                conn = etcd3.client(host=self.host, port=self.port)
                conn.put('/test', 'test_value')
                conn.get('/test')
                status = "No authentication configured for etcd"
                logger.warning(status)
                self.results.append({'check': 'Authentication Check', 'status': 'Vulnerable', 'details': status})
                self.store_action("Check Authentication", status)
            else:
                status = "Authentication appears to be configured"
                logger.info(status)
                self.results.append({'check': 'Authentication Check', 'status': 'OK', 'details': status})
                self.store_action("Check Authentication", status)
        except Exception as e:
            status = f"Authentication check failed: {e}"
            logger.error(status)
            self.store_action("Check Authentication", status)

    def check_exposed(self):
        """Check if database is exposed to external networks."""
        if self.host in ['localhost', '127.0.0.1', '::1']:
            status = "Database is bound to localhost (not externally exposed)"
            logger.info(status)
            self.results.append({'check': 'Exposure Check', 'status': 'OK', 'details': status})
            self.store_action("Check Exposure", status)
        else:
            status = f"Database is bound to {self.host} (potentially exposed externally)"
            logger.warning(status)
            self.results.append({'check': 'Exposure Check', 'status': 'Vulnerable', 'details': status})
            self.store_action("Check Exposure", status)

    def save_results(self):
        """Save assessment results to JSON and text files."""
        report_file = os.path.join(self.output_dir, f"keyvalue_assess_report_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        os.makedirs(self.output_dir, exist_ok=True)

        with open(report_file, 'w') as f:
            f.write(f"Key-Value Database Assessment Report\n")
            f.write(f"Database: {self.db_type} at {self.host}:{self.port}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for result in self.results:
                f.write(f"Check: {result['check']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Details: {result['details']}\n")
                f.write("-" * 50 + "\n")

        with open(self.json_file, 'w') as f:
            json.dump({
                'db_type': self.db_type,
                'host': self.host,
                'port': self.port,
                'results': self.results,
                'actions': self.actions,
                'timestamp': datetime.now().strftime('%Y-%m-d %H:%M:%S')
            }, f, indent=4)

        logger.info(f"Results saved to {report_file} and {self.json_file}")
        self.store_action("Save Results", f"Results saved to {report_file}", report_file)

    def close(self):
        """Close database connection."""
        if self.conn:
            if self.db_type == 'redis':
                self.conn.close()
            # Memcached and etcd connections close automatically
            logger.info("Database connection closed")
            self.store_action("Close", "Connection closed")

def main():
    parser = argparse.ArgumentParser(
        description="KeyValueAssess: Tool for key-value database security assessment.",
        epilog="Example: ./keyvalue_assess.py -t redis -H localhost -P 6379"
    )
    parser.add_argument('-t', '--type', choices=['redis', 'memcached', 'etcd'], required=True,
                        help="Database type (redis, memcached, etcd)")
    parser.add_argument('-H', '--host', default='localhost', help="Database host (default: localhost)")
    parser.add_argument('-P', '--port', type=int, help="Database port (default: 6379 for redis, 11211 for memcached, 2379 for etcd)")
    parser.add_argument('-p', '--password', help="Database password (for redis)")
    parser.add_argument('-o', '--output', default='keyvalue_assess-output',
                        help="Output directory (default: keyvalue_assess-output)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    # Set default ports if not provided
    if not args.port:
        args.port = 6379 if args.type == 'redis' else 11211 if args.type == 'memcached' else 2379

    print("""
    ==============================
          KeyValueAssess v1.0
      Key-Value Security Tool
    ==============================
    WARNING: Use only on databases you own or have explicit permission to assess.
    Unauthorized access may violate laws or terms of service.
    ==============================
    """)

    try:
        assessor = KeyValueAssess(
            db_type=args.type,
            host=args.host,
            port=args.port,
            password=args.password,
            output_dir=args.output,
            quiet=args.quiet
        )

        assessor.check_port_open()
        assessor.check_default_credentials()
        assessor.check_version()
        assessor.check_authentication()
        assessor.check_exposed()
        assessor.save_results()
        assessor.close()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()