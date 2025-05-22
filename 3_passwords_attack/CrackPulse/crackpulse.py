#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import hashlib
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crackpulse.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CrackPulse:
    def __init__(self, algorithm: str, hash_value: str = None, hash_file: str = None,
                 wordlist: str = None, charset: str = None, min_len: int = 1, max_len: int = 4,
                 threads: int = 4, quiet: bool = False):
        self.algorithm = algorithm.lower()
        self.hash_value = hash_value
        self.hash_file = hash_file
        self.wordlist = wordlist
        self.charset = charset or 'abcdefghijklmnopqrstuvwxyz'
        self.min_len = min_len
        self.max_len = max_len
        self.threads = threads
        self.quiet = quiet
        self.output_dir = 'crackpulse-output'
        self.output_file = os.path.join(self.output_dir,
            f"results_{self.algorithm}_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir,
            f"results_{self.algorithm}_{time.strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = []
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('crackpulse.log')]

        # Supported algorithms
        self.supported_algorithms = ['md5', 'sha1', 'sha256', 'ntlm']
        self.hash_functions = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'ntlm': lambda x: hashlib.new('md4', x.encode('utf-16le')).hexdigest()
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
            logger.error("Either --wordlist or --charset must be specified for brute-force")
            return False
        if self.wordlist and not os.path.isfile(self.wordlist):
            logger.error(f"Wordlist file not found: {self.wordlist}")
            return False
        if self.min_len < 1 or self.max_len < self.min_len:
            logger.error("Invalid length range: min_len must be >= 1 and <= max_len")
            return False
        return True

    def load_hashes(self) -> List[str]:
        """Load hashes from file or single hash."""
        if self.hash_value:
            return [self.hash_value.lower()]
        try:
            with open(self.hash_file, 'r') as f:
                return [line.strip().lower() for line in f if line.strip()]
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

    def hash_string(self, text: str) -> str:
        """Hash a string using the specified algorithm."""
        try:
            hasher = self.hash_functions[self.algorithm](text.encode('utf-8'))
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error hashing string: {e}")
            return ''

    def check_word(self, word: str, target_hash: str) -> Dict:
        """Check if a word's hash matches the target hash."""
        computed_hash = self.hash_string(word)
        if computed_hash == target_hash:
            return {'status': 'success', 'password': word, 'hash': target_hash}
        return {'status': 'failed', 'password': None, 'hash': target_hash}

    def dictionary_attack(self, hash_value: str) -> List[Dict]:
        """Perform dictionary attack on a hash."""
        results = []
        words = self.load_wordlist()
        if not words:
            logger.warning(f"No words loaded for dictionary attack on {hash_value}")
            return results

        logger.info(f"Starting dictionary attack on {hash_value} with {len(words)} words")
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.check_word, word, hash_value) for word in words]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result['status'] == 'success':
                    logger.info(f"Hash cracked: {hash_value} -> {result['password']}")
                    self.results.append(f"[{hash_value}] Cracked: {result['password']}")
        return results

    def brute_force_attack(self, hash_value: str) -> List[Dict]:
        """Perform brute-force attack on a hash."""
        results = []
        logger.info(f"Starting brute-force attack on {hash_value}, lengths {self.min_len}-{self.max_len}")

        for length in range(self.min_len, self.max_len + 1):
            for combo in itertools.product(self.charset, repeat=length):
                word = ''.join(combo)
                result = self.check_word(word, hash_value)
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

        logger.info(f"Starting CrackPulse: algorithm={self.algorithm}, output={self.output_file}")
        hashes = self.load_hashes()
        if not hashes:
            logger.error("No valid hashes to process")
            sys.exit(1)

        json_results = []
        for hash_value in hashes:
            result = {'hash': hash_value, 'algorithm': self.algorithm, 'attempts': []}
            
            # Try dictionary attack first if wordlist is provided
            if self.wordlist:
                result['attempts'].extend(self.dictionary_attack(hash_value))
            
            # Try brute-force if no match found and charset is provided
            if not any(r['status'] == 'success' for r in result['attempts']) and self.charset:
                result['attempts'].extend(self.brute_force_attack(hash_value))

            json_results.append(result)
            self.save_results(hash_value, result)

        # Save JSON summary
        with open(self.json_file, 'w') as f:
            json.dump({
                'algorithm': self.algorithm,
                'hashes': json_results,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_cracked': len(self.results)
            }, f, indent=4)

        logger.info(f"Cracking complete. Results saved to {self.output_file} and {self.json_file}")

    def save_results(self, hash_value: str, result: Dict) -> None:
        """Save results to text and JSON files."""
        try:
            with open(self.output_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Hash: {hash_value} ({self.algorithm})\n")
                for attempt in result['attempts']:
                    if attempt['status'] == 'success':
                        f.write(f"Cracked: {attempt['password']}\n")
                    else:
                        f.write(f"Attempted: {attempt.get('password', 'N/A')} - Failed\n")
                f.write("\n")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="CrackPulse: Local password hash cracking tool.",
        epilog="Example: ./crackpulse.py md5 -h 098f6bcd4621d373cade4e832627b4f6 -w wordlist.txt"
    )
    parser.add_argument('algorithm', choices=['md5', 'sha1', 'sha256', 'ntlm'],
                       help="Hash algorithm")
    parser.add_argument('-h', '--hash', help="Single hash value to crack")
    parser.add_argument('-f', '--file', help="File with one hash per line")
    parser.add_argument('-w', '--wordlist', help="Wordlist file for dictionary attack")
    parser.add_argument('-c', '--charset', help="Character set for brute-force (default: lowercase letters)")
    parser.add_argument('-m', '--min-len', type=int, default=1, help="Minimum length for brute-force (default: 1)")
    parser.add_argument('-M', '--max-len', type=int, default=4, help="Maximum length for brute-force (default: 4)")
    parser.add_argument('-t', '--threads', type=int, default=4, help="Number of threads (default: 4)")
    parser.add_argument('-q', '--quiet', action='store_true', help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         CrackPulse v1.0
      Local Hash Cracker
    ==============================
    """)

    try:
        cracker = CrackPulse(
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
        logger.info("Cracking interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()