#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import itertools
import os
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wordforge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WordForge:
    def __init__(self, min_len: int, max_len: int, charset: str, pattern: str = None, 
                 output: str = None, json_output: bool = False, quiet: bool = False):
        self.min_len = min_len
        self.max_len = max_len
        self.charset = charset
        self.pattern = pattern
        self.output = output or f"wordforge_list_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        self.json_output = f"{os.path.splitext(self.output)[0]}.json" if json_output else None
        self.quiet = quiet
        self.word_count = 0
        self.results = []
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('wordforge.log')]

    def validate_inputs(self) -> bool:
        """Validate input parameters."""
        if self.min_len < 1:
            logger.error("Minimum length must be at least 1")
            return False
        if self.max_len < self.min_len:
            logger.error("Maximum length must be greater than or equal to minimum length")
            return False
        if not self.charset:
            logger.error("Character set cannot be empty")
            return False
        if self.pattern and len(self.pattern) > self.max_len:
            logger.error("Pattern length cannot exceed maximum length")
            return False
        return True

    def generate_words(self) -> None:
        """Generate wordlist based on charset and length."""
        logger.info(f"Starting WordForge: min_len={self.min_len}, max_len={self.max_len}, "
                   f"charset={self.charset}, output={self.output}")
        
        try:
            with open(self.output, 'w') as f:
                if self.pattern:
                    self.generate_pattern_words(f)
                else:
                    self.generate_combinations(f)

            if self.json_output:
                self.save_json_results()

            logger.info(f"Wordlist generation complete. {self.word_count} words saved to {self.output}")
            if self.json_output:
                logger.info(f"JSON output saved to {self.json_output}")

        except Exception as e:
            logger.error(f"Error generating wordlist: {e}")
            sys.exit(1)

    def generate_combinations(self, file_handle) -> None:
        """Generate all combinations for given lengths."""
        for length in range(self.min_len, self.max_len + 1):
            for combo in itertools.product(self.charset, repeat=length):
                word = ''.join(combo)
                file_handle.write(word + '\n')
                self.results.append(word)
                self.word_count += 1
                if self.word_count % 10000 == 0:
                    logger.info(f"Generated {self.word_count} words...")

    def generate_pattern_words(self, file_handle) -> None:
        """Generate words based on a pattern (e.g., @ for letters, # for digits)."""
        pattern_map = {
            '@': 'abcdefghijklmnopqrstuvwxyz',
            '#': '0123456789',
            '%': '!@#$%^&*()'
        }
        chars = []
        for char in self.pattern:
            if char in pattern_map:
                chars.append(pattern_map[char])
            else:
                chars.append(char)

        for combo in itertools.product(*chars):
            word = ''.join(combo)
            file_handle.write(word + '\n')
            self.results.append(word)
            self.word_count += 1
            if self.word_count % 10000 == 0:
                logger.info(f"Generated {self.word_count} words...")

    def save_json_results(self) -> None:
        """Save results in JSON format."""
        try:
            with open(self.json_output, 'w') as f:
                json.dump({
                    "min_len": self.min_len,
                    "max_len": self.max_len,
                    "charset": self.charset,
                    "pattern": self.pattern,
                    "word_count": self.word_count,
                    "words": self.results,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving JSON output: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="WordForge: A wordlist generator for security testing.",
        epilog="Example: ./wordforge.py -m 4 -M 6 -c abc123 -o wordlist.txt"
    )
    parser.add_argument('-m', '--min-len', type=int, default=1, 
                       help="Minimum word length (default: 1)")
    parser.add_argument('-M', '--max-len', type=int, default=4, 
                       help="Maximum word length (default: 4)")
    parser.add_argument('-c', '--charset', default='abcdefghijklmnopqrstuvwxyz', 
                       help="Character set for wordlist (default: lowercase letters)")
    parser.add_argument('-p', '--pattern', 
                       help="Pattern for wordlist (e.g., @@## for two letters, two digits)")
    parser.add_argument('-o', '--output', 
                       help="Output file for wordlist (default: wordforge_list_<timestamp>.txt)")
    parser.add_argument('-j', '--json', action='store_true', 
                       help="Generate JSON output alongside text")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         WordForge v1.0
       Wordlist Generator
    ==============================
    """)

    forger = WordForge(
        min_len=args.min_len,
        max_len=args.max_len,
        charset=args.charset,
        pattern=args.pattern,
        output=args.output,
        json_output=args.json,
        quiet=args.quiet
    )

    if not forger.validate_inputs():
        sys.exit(1)

    try:
        forger.generate_words()
    except KeyboardInterrupt:
        logger.info("Wordlist generation interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()