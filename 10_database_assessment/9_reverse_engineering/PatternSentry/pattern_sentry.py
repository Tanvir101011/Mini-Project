#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import re
import json
import sqlite3
import time
import binascii
from typing import List, Dict, Any
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pattern_sentry.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PatternSentry:
    def __init__(self, rules_file: str, target: str, output_dir: str = 'pattern_sentry-output',
                 quiet: bool = False):
        self.rules_file = os.path.abspath(rules_file)
        self.target = os.path.abspath(target) if os.path.exists(target) else target
        self.output_dir = os.path.abspath(output_dir)
        self.quiet = quiet
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"pattern_sentry_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'pattern_sentry.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.actions = []
        self.rules = []
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('pattern_sentry.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT,
                    rule_name TEXT,
                    status TEXT,
                    output_path TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_action(self, rule_name: str, status: str, output_path: str = ''):
        """Store action details in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO actions (target, rule_name, status, output_path, timestamp) '
                'VALUES (?, ?, ?, ?, ?)',
                (self.target, rule_name, status, output_path, timestamp)
            )
            conn.commit()
        self.actions.append({
            'target': self.target,
            'rule_name': rule_name,
            'status': status,
            'output_path': output_path,
            'timestamp': timestamp
        })

    def parse_rules(self):
        """Parse rules from the rules file."""
        try:
            with open(self.rules_file, 'r') as f:
                content = f.read()
            
            # Simple rule parser (supports basic YARA-like syntax)
            rule_pattern = re.compile(
                r'rule\s+(\w+)\s*\{([^}]*)\}', re.DOTALL | re.MULTILINE
            )
            meta_pattern = re.compile(r'meta:\s*([\s\S]*?)(?=(strings:|condition:))', re.DOTALL)
            strings_pattern = re.compile(r'strings:\s*([\s\S]*?)(?=(condition:))', re.DOTALL)
            condition_pattern = re.compile(r'condition:\s*([\s\S]*?)(?=\s*\})', re.DOTALL)
            string_def_pattern = re.compile(r'\$(\w+)\s*=\s*"(.*?)"(?:\s*\{([^}]*)\})?', re.DOTALL)
            hex_string_pattern = re.compile(r'\$(\w+)\s*=\s*\{([0-9A-Fa-f\s]*)\}', re.DOTALL)

            for rule_match in rule_pattern.finditer(content):
                rule_name = rule_match.group(1)
                rule_body = rule_match.group(2).strip()
                
                rule = {'name': rule_name, 'meta': {}, 'strings': {}, 'condition': ''}

                # Parse meta
                meta_match = meta_pattern.search(rule_body)
                if meta_match:
                    meta_content = meta_match.group(1).strip()
                    for line in meta_content.split('\n'):
                        line = line.strip()
                        if '=' in line:
                            key, value = map(str.strip, line.split('=', 1))
                            rule['meta'][key] = value.replace('"', '')

                # Parse strings
                strings_match = strings_pattern.search(rule_body)
                if strings_match:
                    strings_content = strings_match.group(1).strip()
                    # Text strings
                    for string_match in string_def_pattern.finditer(strings_content):
                        string_id = string_match.group(1)
                        string_value = string_match.group(2)
                        modifiers = string_match.group(3) or ''
                        rule['strings'][string_id] = {
                            'value': string_value,
                            'type': 'text',
                            'modifiers': modifiers.split() if modifiers else []
                        }
                    # Hex strings
                    for hex_match in hex_string_pattern.finditer(strings_content):
                        string_id = hex_match.group(1)
                        hex_value = hex_match.group(2).replace(' ', '')
                        rule['strings'][string_id] = {
                            'value': hex_value,
                            'type': 'hex',
                            'modifiers': []
                        }

                # Parse condition
                condition_match = condition_pattern.search(rule_body)
                if condition_match:
                    rule['condition'] = condition_match.group(1).strip()

                self.rules.append(rule)
                logger.info(f"Parsed rule: {rule_name}")

        except Exception as e:
            logger.error(f"Failed to parse rules file: {e}")
            self.store_action("parse_rules", f"Failed: {str(e)}")
            sys.exit(1)

    def evaluate_condition(self, condition: str, matches: Dict[str, bool]) -> bool:
        """Evaluate a rule's condition using matched strings."""
        try:
            # Replace string IDs with their match status (True/False)
            for string_id in matches:
                condition = condition.replace(f'${string_id}', str(matches[string_id]).lower())
            # Replace logical operators for Python eval
            condition = condition.replace('and', ' and ').replace('or', ' or ').replace('not', ' not ')
            # Basic safety check to prevent arbitrary code execution
            if re.match(r'^[\s\w$()=<>!&|]*$', condition):
                return eval(condition, {"__builtins__": {}}, {})
            else:
                logger.error(f"Invalid condition syntax: {condition}")
                return False
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a single file against all rules."""
        results = []
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                text_content = content.decode('utf-8', errors='ignore')

            for rule in self.rules:
                matches = {}
                for string_id, string_data in rule['strings'].items():
                    matched = False
                    if string_data['type'] == 'text':
                        pattern = string_data['value']
                        if 'nocase' in string_data['modifiers']:
                            pattern = re.compile(re.escape(pattern), re.IGNORECASE)
                            matched = bool(pattern.search(text_content))
                        else:
                            matched = pattern in text_content
                    elif string_data['type'] == 'hex':
                        hex_pattern = binascii.unhexlify(string_data['value'])
                        matched = hex_pattern in content
                    matches[string_id] = matched

                if self.evaluate_condition(rule['condition'], matches):
                    status = f"Match for rule {rule['name']} in {file_path}"
                    logger.info(status)
                    self.store_action(rule['name'], status, file_path)
                    results.append({
                        'rule_name': rule['name'],
                        'file': file_path,
                        'meta': rule['meta'],
                        'matched_strings': [k for k, v in matches.items() if v]
                    })
                else:
                    status = f"No match for rule {rule['name']} in {file_path}"
                    self.store_action(rule['name'], status)

        except Exception as e:
            status = f"Scan failed for {file_path}: {str(e)}"
            logger.error(status)
            self.store_action("scan_file", status)
        
        return results

    def scan(self):
        """Scan the target (file or directory) against rules."""
        results = []
        if os.path.isfile(self.target):
            results.extend(self.scan_file(self.target))
        elif os.path.isdir(self.target):
            for root, _, files in os.walk(self.target):
                for file in files:
                    file_path = os.path.join(root, file)
                    results.extend(self.scan_file(file_path))
        else:
            status = f"Invalid target: {self.target}"
            logger.error(status)
            self.store_action("scan", status)
            return []

        if not results:
            logger.info(f"No matches found for {self.target}")
        
        return results

    def save_results(self, results: List[Dict[str, Any]]):
        """Save scan results to JSON file."""
        with open(self.json_file, 'w') as f:
            json.dump({
                'target': self.target,
                'rules_file': self.rules_file,
                'output_dir': self.output_dir,
                'results': results,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="PatternSentry: Tool for pattern-based file analysis.",
        epilog="Example: ./pattern_sentry.py -r rules.yar -t sample.exe -o output_dir"
    )
    parser.add_argument('-r', '--rules', required=True,
                        help="Path to rules file")
    parser.add_argument('-t', '--target', required=True,
                        help="Path to target file or directory")
    parser.add_argument('-o', '--output', default='pattern_sentry-output',
                        help="Output directory (default: pattern_sentry-output)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         PatternSentry v1.0
      Pattern Matching Tool
    ==============================
    """)

    try:
        sentry = PatternSentry(
            rules_file=args.rules,
            target=args.target,
            output_dir=args.output,
            quiet=args.quiet
        )
        sentry.parse_rules()
        results = sentry.scan()
        sentry.save_results(results)

        if results:
            print("\nMatches Found:")
            for result in results:
                print(f"- Rule: {result['rule_name']}, File: {result['file']}")
                print(f"  Matched Strings: {', '.join(result['matched_strings'])}")
                print(f"  Meta: {result['meta']}")
        else:
            print("\nNo matches found.")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()