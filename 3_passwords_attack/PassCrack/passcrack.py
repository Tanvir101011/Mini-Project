#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import hashlib
import itertools
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('passcrack.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PassCrack:
    def __init__(self, algorithm: str, hash_value: str = None, hash_file: str = None,
                 wordlist: str = None, charset: str = None, min_len: int = 1, max_len: int = 4,
                 threads: int = 5, quiet: bool = False):
        self.algorithm = algorithm.upper()
        self.hash_value = hash_value
        self.hash_file = hash_file
        self.wordlist = wordlist
        self.charset = charset or 'abcdefghijklmnopqrstuvwxyz0123456789'
        self.min_len = min_len
        self.max_len = max_len
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'passcrack-output'
        self.output_file = os.path.join(self.output_dir,
            f"results_{self.algorithm.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir,
            f"results_{self.algorithm.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = []
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('passcrack.log')]

        # Supported algorithms
        self.supported_algorithms = ['MD5', 'SHA1', 'SHA256', 'NTLM']
        self.hash_functions = {
            'MD5': hashlib.md5,
            'SHA1': hashlib.sha1,
            'SHA256': hashlib.sha256,
            'NTLM': lambda x: hashlib.new('md4', x.encode('utf-16le')).hexdigest()
        }

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
        if not self.wordlist and not self.charset:
            logger.error("Either --wordlist or --charset must be specified")
            return False
        if self.wordlist and not os.path.isfile(self.wordlist):
            logger.error(f"Wordlist file not found: {self.wordlist}")
            return False
        if self.min_len < 1 or self.max_len < self.min_len:
            logger.error("Invalid length: min_len must be >= 1 and <= max_len")
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

    def load_wordlist(self) -> List[str]:
        """Load words from wordlist file."""
        if not self.wordlist:
            return []
        try:
            with open(self.wordlist, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading wordlist {self.wordlist}: {e}")
            return []

    def hash_password(self, password: str) -> str:
        """Compute hash for a password."""
        hash_func = self.hash_functions[self.algorithm]
        return hash_func(password.encode('utf-8')).hexdigest()

    def check_password(self, password: str, target_hash: str) -> Dict:
        """Check if password matches the target hash."""
        computed_hash = self.hash_password(password)
        if computed_hash.lower() == target_hash.lower():
            return {'password': password, 'hash': computed_hash, 'status': 'success'}
        return {'password': password, 'hash': computed_hash, 'status': 'failed'}

    def dictionary_attack(self, hash_value: str, words: List[str]) -> List[Dict]:
        """Perform dictionary attack."""
        results = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.check_password, word, hash_value) for word in words]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result['status'] == 'success':
                    logger.info(f"Hash cracked: {hash_value} -> {result['password']}")
                    self.results.append(f"[{hash_value}] Cracked: {result['password']}")
        return results

    def brute_force_attack(self, hash_value: str) -> List[Dict]:
        """Perform brute-force attack."""
        results = []
        for length in range(self.min_len, self.max_len + 1):
            logger.info(f"Trying length {length} for {hash_value}")
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [
                    executor.submit(self.check_password, ''.join(combo), hash_value)
                    for combo in itertools.product(self.charset, repeat=length)
                ]
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    if result['status'] == 'success':
                        logger.info(f"Hash cracked: {hash_value} -> {result['password']}")
                        self.results.append(f"[{hash_value}] Cracked: {result['password']}")
                        return results  # Stop on first match
        return results

    def crack_hashes(self) -> None:
        """Crack hashes using dictionary or brute-force attack."""
        if not self.validate_inputs():
            sys.exit(1)

        logger.info(f"Starting PassCrack: algorithm={self.algorithm}, output={self.output_file}")
        hashes = self.load_hashes()
        if not hashes:
            logger.error("No valid hashes to process")
            sys.exit(1)

        words = self.load_wordlist()
        for hash_value in hashes:
            result = {'hash': hash_value, 'algorithm': self.algorithm, 'results': []}
            if words:
                logger.info(f"Running dictionary attack on {hash_value}")
                result['results'].extend(self.dictionary_attack(hash_value, words))
            if not any(r['status'] == 'success' for r in result['results']):
                logger.info(f"Running brute-force attack on {hash_value}")
                result['results'].extend(self.brute_force_attack(hash_value))

            self.save_results(hash_value, result)

        logger.info(f"Hash cracking complete. Results saved to {self.output_file} and {self.json_file}")

    def save_results(self, hash_value: str, result: Dict) -> None:
        """Save results to text and JSON files."""
        try:
            with open(self.output_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Hash: {hash_value} ({self.algorithm})\n")
                for res in result['results']:
                    if res['status'] == 'success':
                        f.write(f"Cracked: {res['password']} (Hash: {res['hash']})\n")
                f.write("\n")

            json_data = {
                'algorithm': self.algorithm,
                'hashes': [result],
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_cracked': len(self.results)
            }
            with open(self.json_file, 'w') as f:
                json.dump(json_data, f, indent=4)

        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="PassCrack: A password hash cracker.",
        epilog="Example: ./passcrack.py MD5 -h 098f6bcd4621d373cade4e832627b4f6 -w wordlist.txt"
    )
    parser.add_argument('algorithm', choices=['MD5', 'SHA1', 'SHA256', 'NTLM'],
                       help="Hash algorithm")
    parser.add_argument('-h', '--hash', help="Single hash value to crack")
    parser.add_argument('-f', '--file', help="File with one hash per line")
    parser.add_argument('-w', '--wordlist', help="Wordlist file for dictionary attack")
    parser.add_argument('-c', '--charset', help="Character set for brute-force (default: lowercase + digits)")
    parser.add_argument('-m', '--min-len', type=int, default=1,
                       help="Minimum length for brute-force (default: 1)")
    parser.add_argument('-M', '--max-len', type=int, default=4,
                       help="Maximum length for brute-force (default: 4)")
    parser.add_argument('-T', '--threads', type=int, default=5,
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true',
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         PassCrack v1.0
       Password Hash Cracker
    ==============================
    """)

    try:
        cracker = PassCrack(
            algorithm=args.algorithm,
            hash_value=args.hash,
            hash_file=args.file,
            wordlist=args.wordlist,
            charset=args.charset,
            min_len=args.min_len,
            max_len=args.max_len,
            threads=args.threads,
            quiet=args.quiet
        )
        cracker.crack_hashes()
    except KeyboardInterrupt:
        logger.info("Hash cracking interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()