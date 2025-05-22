#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import json
import sqlite3
import time
import socket
import mysql.connector
import psycopg2
import sqlite3 as sqlite
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_assess.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DBAssess:
    def __init__(self, db_type: str, host: str, port: int, user: str, password: str, database: Optional[str] = None,
                 output_dir: str = 'db_assess-output', quiet: bool = False):
        self.db_type = db_type.lower()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.output_dir = os.path.abspath(output_dir)
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"db_assess_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'db_assess.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.results = []
        self.actions = []
        self.conn = None
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('db_assess.log')]

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
        """Connect to the database."""
        try:
            if self.db_type == 'mysql':
                self.conn = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            elif self.db_type == 'postgresql':
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            elif self.db_type == 'sqlite':
                if not self.database or not os.path.exists(self.database):
                    raise FileNotFoundError(f"SQLite database file not found: {self.database}")
                self.conn = sqlite.connect(self.database)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            status = f"Connected to {self.db_type} database at {self.host}:{self.port}"
            logger.info(status)
            self.store_action("Connect", status)
        except (mysql.connector.Error, psycopg2.Error, sqlite.Error, FileNotFoundError) as e:
            status = f"Connection failed: {e}"
            logger.error(status)
            self.store_action("Connect", status)
            self.conn = None

    def check_default_credentials(self):
        """Check for default or weak credentials."""
        default_creds = {
            'mysql': [('root', ''), ('root', 'root'), ('admin', 'admin')],
            'postgresql': [('postgres', 'postgres'), ('admin', 'admin')],
            'sqlite': []  # SQLite does not use credentials
        }
        weak = default_creds.get(self.db_type, [])
        if not weak:
            return

        for user, pwd in weak:
            try:
                if self.db_type == 'mysql':
                    conn = mysql.connector.connect(
                        host=self.host,
                        port=self.port,
                        user=user,
                        password=pwd,
                        database=self.database
                    )
                elif self.db_type == 'postgresql':
                    conn = psycopg2.connect(
                        host=self.host,
                        port=self.port,
                        user=user,
                        password=pwd,
                        database=self.database
                    )
                conn.close()
                status = f"Default/weak credentials found: {user}:{pwd}"
                logger.warning(status)
                self.results.append({'check': 'Default Credentials', 'status': 'Vulnerable', 'details': status})
                self.store_action("Check Default Credentials", status)
            except (mysql.connector.Error, psycopg2.Error):
                pass

    def check_version(self):
        """Check database version for known vulnerabilities."""
        try:
            if not self.conn:
                self.connect_db()
            if not self.conn:
                return

            version = ''
            if self.db_type == 'mysql':
                cursor = self.conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()
            elif self.db_type == 'postgresql':
                cursor = self.conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                cursor.close()
            elif self.db_type == 'sqlite':
                version = sqlite.sqlite_version

            # Simplified version check (real-world would query CVE database)
            vulnerable_versions = {
                'mysql': ['5.5', '5.6'],
                'postgresql': ['9.0', '9.1'],
                'sqlite': ['3.0']
            }
            is_vulnerable = any(v in version for v in vulnerable_versions.get(self.db_type, []))
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

    def check_permissions(self):
        """Check for excessive user permissions."""
        try:
            if not self.conn:
                self.connect_db()
            if not self.conn or self.db_type == 'sqlite':
                return  # SQLite does not have user permissions

            permissions = []
            if self.db_type == 'mysql':
                cursor = self.conn.cursor()
                cursor.execute("SHOW GRANTS FOR CURRENT_USER")
                permissions = [row[0] for row in cursor.fetchall()]
                cursor.close()
            elif self.db_type == 'postgresql':
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM information_schema.role_table_grants WHERE grantee = CURRENT_USER")
                permissions = [f"{row[7]} on {row[5]}" for row in cursor.fetchall()]
                cursor.close()

            excessive = any('ALL PRIVILEGES' in p or 'SUPER' in p or 'WITH GRANT OPTION' in p for p in permissions)
            status = f"Permissions: {', '.join(permissions[:3])} {'(excessive)' if excessive else ''}"
            logger.info(status)
            self.results.append({
                'check': 'Permissions Check',
                'status': 'Vulnerable' if excessive else 'OK',
                'details': status
            })
            self.store_action("Check Permissions", status)
        except Exception as e:
            status = f"Permissions check failed: {e}"
            logger.error(status)
            self.store_action("Check Permissions", status)

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
        report_file = os.path.join(self.output_dir, f"db_assess_report_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        os.makedirs(self.output_dir, exist_ok=True)

        with open(report_file, 'w') as f:
            f.write(f"Database Assessment Report\n")
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
            self.conn.close()
            logger.info("Database connection closed")
            self.store_action("Close", "Connection closed")

def main():
    parser = argparse.ArgumentParser(
        description="DBAssess: Tool for database security assessment.",
        epilog="Example: ./db_assess.py -t mysql -H localhost -P 3306 -u root -p password"
    )
    parser.add_argument('-t', '--type', choices=['mysql', 'postgresql', 'sqlite'], required=True,
                        help="Database type (mysql, postgresql, sqlite)")
    parser.add_argument('-H', '--host', default='localhost', help="Database host (default: localhost)")
    parser.add_argument('-P', '--port', type=int, help="Database port (default: 3306 for mysql, 5432 for postgresql)")
    parser.add_argument('-u', '--user', default='root', help="Database user (default: root)")
    parser.add_argument('-p', '--password', default='', help="Database password (default: empty)")
    parser.add_argument('-d', '--database', help="Database name (or SQLite file path)")
    parser.add_argument('-o', '--output', default='db_assess-output',
                        help="Output directory (default: db_assess-output)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    # Set default ports if not provided
    if not args.port:
        args.port = 3306 if args.type == 'mysql' else 5432 if args.type == 'postgresql' else None

    print("""
    ==============================
          DBAssess v1.0
      Database Security Tool
    ==============================
    WARNING: Use only on databases you own or have explicit permission to assess.
    Unauthorized access may violate laws or terms of service.
    ==============================
    """)

    try:
        assessor = DBAssess(
            db_type=args.type,
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
            output_dir=args.output,
            quiet=args.quiet
        )

        assessor.check_port_open()
        assessor.check_default_credentials()
        assessor.check_version()
        assessor.check_permissions()
        assessor.check_exposed()
        assessor.save_results()
        assessor.close()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()