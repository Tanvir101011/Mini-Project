#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import requests
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hashsnipe.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HashSnipe:
    def __init__(self, algorithm: str, hash_value: str = None, hash_file: str = None, 
                 google_search: bool = False, quiet: bool = False):
        self.algorithm = algorithm.upper()
        self.hash_value = hash_value
        self.hash_file = hash_file
        self.google_search = google_search
        self.quiet = quiet
        self.output_dir = 'hashsnipe-output'
        self.output_file = os.path.join(self.output_dir, 
            f"results_{self.algorithm.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"results_{self.algorithm.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = []
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('hashsnipe.log')]
        
        # Supported algorithms
        self.supported_algorithms = [
            'MD4', 'MD5', 'SHA1', 'SHA224', 'SHA256', 'SHA384', 'SHA512',
            'NTLM', 'MYSQL', 'LDAP_MD5', 'LDAP_SHA1'
        ]
        
        # API endpoints (simplified for demonstration; use real APIs cautiously)
        self.api_endpoints = [
            {'name': 'CrackStation', 'url': 'https://crackstation.net/', 'method': 'lookup'},
            {'name': 'Hashes.com', 'url': 'https://hashes.com/en/decrypt/hash', 'method': 'post'}
        ]

    def validate_inputs(self) -> bool:
        """Validate input parameters."""
        if self.algorithm not in self.supported_algorithms:
            logger.error(f"Unsupported algorithm: {self.algorithm}. Supported: {', '.join(self.supported_algorithms)}")
            return False
        if not self.hash_value and not self.hash_file:
            logger.error("Either --hash or --file must be specified")
            return False
        if self.hash_file and not os.path.isfile(self.hash_file):
            logger.error(f"Hash file not found: {self.hash_file}")
            return False
        if self.google_search and self.hash_file:
            logger.error("Google search (-g) is only supported with single hash (-h)")
            return False
        return True

    def load_hashes(self) -> List[str]:
        """Load hashes from file or single hash."""
        if self.hash_value:
            return [self.hash_value]
        try:
            with open(self.hash_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading hash file {self.hash_file}: {e}")
            return []

    def query_api(self, hash_value: str, endpoint: Dict) -> Dict:
        """Query an online hash-cracking API."""
        try:
            # Placeholder: Implement actual API calls (e.g., CrackStation, Hashes.com)
            # This is a mock response for demonstration
            logger.info(f"Querying {endpoint['name']} for hash: {hash_value}")
            time.sleep(1)  # Simulate API delay
            if endpoint['name'] == 'CrackStation':
                # Mock response
                if hash_value == '098f6bcd4621d373cade4e832627b4f6':  # MD5 for 'test'
                    return {'status': 'success', 'password': 'test', 'message': 'Hash cracked'}
                return {'status': 'failed', 'password': None, 'message': 'Hash not found'}
            return {'status': 'failed', 'password': None, 'message': 'API not implemented'}
        except Exception as e:
            logger.error(f"Error querying {endpoint['name']}: {e}")
            return {'status': 'error', 'password': None, 'message': str(e)}

    def google_hash(self, hash_value: str) -> List[str]:
        """Search hash on Google (placeholder)."""
        logger.info(f"Searching Google for hash: {hash_value}")
        try:
            # Placeholder: Implement Google search API or web scraping
            return [f"Mock Google result for {hash_value}"]
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []

    def crack_hashes(self) -> None:
        """Crack hashes using online services."""
        if not self.validate_inputs():
            sys.exit(1)

        logger.info(f"Starting HashSnipe: algorithm={self.algorithm}, output={self.output_file}")
        hashes = self.load_hashes()
        if not hashes:
            logger.error("No valid hashes to process")
            sys.exit(1)

        for hash_value in hashes:
            result = {'hash': hash_value, 'algorithm': self.algorithm, 'results': []}
            for endpoint in self.api_endpoints:
                api_result = self.query_api(hash_value, endpoint)
                result['results'].append({
                    'service': endpoint['name'],
                    'status': api_result['status'],
                    'password': api_result['password'],
                    'message': api_result['message']
                })
                if api_result['status'] == 'success':
                    logger.info(f"Hash cracked: {hash_value} -> {api_result['password']} ({endpoint['name']})")
                    self.results.append(f"[{hash_value}] Cracked: {api_result['password']} ({endpoint['name']})")

            if self.google_search and not any(r['status'] == 'success' for r in result['results']):
                google_results = self.google_hash(hash_value)
                result['google_results'] = google_results
                if google_results:
                    logger.info(f"Google results for {hash_value}: {', '.join(google_results)}")

            self.save_results(hash_value, result)

        logger.info(f"Hash cracking complete. Results saved to {self.output_file} and {self.json_file}")

    def save_results(self, hash_value: str, result: Dict) -> None:
        """Save results to text and JSON files."""
        try:
            with open(self.output_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Hash: {hash_value} ({self.algorithm})\n")
                for res in result['results']:
                    status = res['status'].upper()
                    msg = f"{res['service']}: {status}"
                    if res['password']:
                        msg += f" - Password: {res['password']}"
                    msg += f" - {res['message']}"
                    f.write(f"{msg}\n")
                if 'google_results' in result:
                    f.write(f"Google: {', '.join(result['google_results'])}\n")
                f.write("\n")

            json_data = {
                'algorithm': self.algorithm,
                'hashes': [result],
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_hashes': len(self.results)
            }
            with open(self.json_file, 'a') as f:
                json.dump(json_data, f, indent=4)

        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="HashSnipe: Crack hashes using online services.",
        epilog="Example: ./hashsnipe.py MD5 -h 098f6bcd4621d373cade4e832627b4f6"
    )
    parser.add_argument('algorithm', choices=[
        'MD4', 'MD5', 'SHA1', 'SHA224', 'SHA256', 'SHA384', 'SHA512',
        'NTLM', 'MYSQL', 'LDAP_MD5', 'LDAP_SHA1'
    ], help="Hash algorithm")
    parser.add_argument('-h', '--hash', help="Single hash value to crack")
    parser.add_argument('-f', '--file', help="File with one hash per line")
    parser.add_argument('-g', '--google', action='store_true', 
                       help="Search hash on Google if not cracked (single hash only)")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         HashSnipe v1.0
       Online Hash Cracker
    ==============================
    """)

    try:
        sniper = HashSnipe(
            algorithm=args.algorithm,
            hash_value=args.hash,
            hash_file=args.file,
            google_search=args.google,
            quiet=args.quiet
        )
        sniper.crack_hashes()
    except KeyboardInterrupt:
        logger.info("Hash cracking interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()