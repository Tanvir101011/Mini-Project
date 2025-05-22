#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import re
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hashident.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HashIDent:
    def __init__(self, hash_value: str = None, hash_file: str = None, 
                 json_output: bool = False, quiet: bool = False):
        self.hash_value = hash_value
        self.hash_file = hash_file
        self.json_output = json_output
        self.quiet = quiet
        self.output_dir = 'hashident-output'
        self.output_file = os.path.join(self.output_dir, 
            f"results_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"results_{time.strftime('%Y%m%d_%H%M%S')}.json") if json_output else None
        os.makedirs(self.output_dir, exist_ok=True)
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('hashident.log')]
        
        # Hash identification patterns
        self.hash_patterns = [
            {'name': 'MD4', 'length': 32, 'regex': r'^[0-9a-fA-F]{32}$', 'confidence': 0.9},
            {'name': 'MD5', 'length': 32, 'regex': r'^[0-9a-fA-F]{32}$', 'confidence': 0.9},
            {'name': 'SHA1', 'length': 40, 'regex': r'^[0-9a-fA-F]{40}$', 'confidence': 0.95},
            {'name': 'SHA224', 'length': 56, 'regex': r'^[0-9a-fA-F]{56}$', 'confidence': 0.85},
            {'name': 'SHA256', 'length': 64, 'regex': r'^[0-9a-fA-F]{64}$', 'confidence': 0.95},
            {'name': 'SHA384', 'length': 96, 'regex': r'^[0-9a-fA-F]{96}$', 'confidence': 0.85},
            {'name': 'SHA512', 'length': 128, 'regex': r'^[0-9a-fA-F]{128}$', 'confidence': 0.95},
            {'name': 'NTLM', 'length': 32, 'regex': r'^[0-9a-fA-F]{32}$', 'confidence': 0.8},
            {'name': 'MySQL323', 'length': 16, 'regex': r'^[0-9a-fA-F]{16}$', 'confidence': 0.7},
            {'name': 'MySQL', 'length': 40, 'regex': r'^\*[0-9a-fA-F]{40}$', 'confidence': 0.9},
            {'name': 'LM', 'length': 32, 'regex': r'^[0-9a-fA-F]{32}$', 'confidence': 0.7},
            {'name': 'bcrypt', 'length': None, 'regex': r'^\$2[ayb]\$[0-9]{2}\$[A-Za-z0-9./]{53}$', 'confidence': 0.95},
            {'name': 'WPA-PSK', 'length': 64, 'regex': r'^[0-9a-fA-F]{64}$', 'confidence': 0.8}
        ]

    def validate_inputs(self) -> bool:
        """Validate input parameters."""
        if not self.hash_value and not self.hash_file:
            logger.error("Either --hash or --file must be specified")
            return False
        if self.hash_file and not os.path.isfile(self.hash_file):
            logger.error(f"Hash file not found: {self.hash_file}")
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

    def identify_hash(self, hash_value: str) -> List[Dict]:
        """Identify possible hash types based on characteristics."""
        possible_types = []
        hash_value = hash_value.strip()
        
        for pattern in self.hash_patterns:
            length_match = pattern['length'] is None or len(hash_value) == pattern['length']
            regex_match = bool(re.match(pattern['regex'], hash_value))
            
            if length_match and regex_match:
                possible_types.append({
                    'algorithm': pattern['name'],
                    'confidence': pattern['confidence'],
                    'details': f"Length: {len(hash_value)}, Regex: {pattern['regex']}"
                })
        
        # Sort by confidence (descending)
        possible_types.sort(key=lambda x: x['confidence'], reverse=True)
        
        if not possible_types:
            possible_types.append({
                'algorithm': 'Unknown',
                'confidence': 0.0,
                'details': 'No matching patterns found'
            })
        
        return possible_types

    def process_hashes(self) -> None:
        """Process all hashes and identify their types."""
        if not self.validate_inputs():
            sys.exit(1)

        logger.info(f"Starting HashIDent: output={self.output_file}")
        hashes = self.load_hashes()
        if not hashes:
            logger.error("No valid hashes to process")
            sys.exit(1)

        results = []
        for hash_value in hashes:
            possible_types = self.identify_hash(hash_value)
            results.append({
                'hash': hash_value,
                'possible_types': possible_types
            })
            logger.info(f"Hash: {hash_value}")
            for pt in possible_types:
                logger.info(f"  Possible: {pt['algorithm']} (Confidence: {pt['confidence']:.2%}) - {pt['details']}")

            self.save_results(hash_value, possible_types)

        if self.json_output:
            self.save_json_results(results)

        logger.info(f"Hash identification complete. Results saved to {self.output_file}")
        if self.json_output:
            logger.info(f"JSON output saved to {self.json_file}")

    def save_results(self, hash_value: str, possible_types: List[Dict]) -> None:
        """Save results to text file."""
        try:
            with open(self.output_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Hash: {hash_value}\n")
                for pt in possible_types:
                    f.write(f"  {pt['algorithm']}: Confidence {pt['confidence']:.2%} - {pt['details']}\n")
                f.write("\n")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def save_json_results(self, results: List[Dict]) -> None:
        """Save results in JSON format."""
        try:
            with open(self.json_file, 'w') as f:
                json.dump({
                    'results': results,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'total_hashes': len(results)
                }, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving JSON output: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="HashIDent: Identify hash algorithms based on format.",
        epilog="Example: ./hashident.py -h 098f6bcd4621d373cade4e832627b4f6"
    )
    parser.add_argument('-h', '--hash', help="Single hash value to identify")
    parser.add_argument('-f', '--file', help="File with one hash per line")
    parser.add_argument('-j', '--json', action='store_true', 
                       help="Generate JSON output alongside text")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         HashIDent v1.0
       Hash Type Identifier
    ==============================
    """)

    try:
        identifier = HashIDent(
            hash_value=args.hash,
            hash_file=args.file,
            json_output=args.json,
            quiet=args.quiet
        )
        identifier.process_hashes()
    except KeyboardInterrupt:
        logger.info("Hash identification interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()