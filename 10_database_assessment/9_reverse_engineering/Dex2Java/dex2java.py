#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import subprocess
import shutil
import json
import sqlite3
import time
import zipfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dex2java.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Dex2Java:
    def __init__(self, input_path: str, output_dir: str = 'dex2java-output',
                 quiet: bool = False):
        self.input_path = os.path.abspath(input_path)
        self.output_dir = os.path.abspath(output_dir)
        self.quiet = quiet
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"dex2java_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'dex2java.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.actions = []
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('dex2java.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_path TEXT,
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
                'INSERT INTO actions (input_path, action, status, output_path, timestamp) '
                'VALUES (?, ?, ?, ?, ?)',
                (self.input_path, action, status, output_path, timestamp)
            )
            conn.commit()
        self.actions.append({
            'input_path': self.input_path,
            'action': action,
            'status': status,
            'output_path': output_path,
            'timestamp': timestamp
        })

    def run_command(self, cmd: list, action: str) -> bool:
        """Run a shell command and log the result."""
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            status = f"{action} succeeded: {result.stdout.strip()}"
            logger.info(status)
            self.store_action(action, status)
            return True
        except subprocess.CalledProcessError as e:
            status = f"{action} failed: {e.stderr.strip()}"
            logger.error(status)
            self.store_action(action, status)
            return False
        except Exception as e:
            status = f"{action} failed: {str(e)}"
            logger.error(status)
            self.store_action(action, status)
            return False

    def extract_dex(self):
        """Extract .dex files from APK if input is an APK."""
        if not self.input_path.endswith('.apk'):
            return [self.input_path]  # Assume input is already a .dex file

        dex_files = []
        apk_name = os.path.splitext(os.path.basename(self.input_path))[0]
        extract_dir = os.path.join(self.output_dir, f"{apk_name}_extracted")
        os.makedirs(extract_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(self.input_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith('.dex'):
                        zip_ref.extract(file, extract_dir)
                        dex_files.append(os.path.join(extract_dir, file))
            if not dex_files:
                status = "No .dex files found in APK"
                logger.error(status)
                self.store_action("Extract DEX", status)
                return []
            status = f"Extracted {len(dex_files)} .dex files to {extract_dir}"
            logger.info(status)
            self.store_action("Extract DEX", status, extract_dir)
            return dex_files
        except Exception as e:
            status = f"DEX extraction failed: {str(e)}"
            logger.error(status)
            self.store_action("Extract DEX", status)
            return []

    def convert_dex_to_jar(self, dex_file: str):
        """Convert a single .dex file to .jar."""
        dex_name = os.path.splitext(os.path.basename(dex_file))[0]
        jar_file = os.path.join(self.output_dir, f"{dex_name}.jar")

        # Use d2j-dex2jar (dex2jar binary) for conversion
        cmd = ['d2j-dex2jar', dex_file, '-o', jar_file]
        if self.run_command(cmd, f"Convert {dex_name}.dex to {dex_name}.jar"):
            return jar_file
        return None

    def convert(self):
        """Convert .dex file(s) to .jar file(s)."""
        dex_files = self.extract_dex() if self.input_path.endswith('.apk') else [self.input_path]
        if not dex_files:
            logger.error("No .dex files to convert")
            return False

        jar_files = []
        for dex_file in dex_files:
            jar_file = self.convert_dex_to_jar(dex_file)
            if jar_file:
                jar_files.append(jar_file)

        if jar_files:
            status = f"Converted {len(jar_files)} .dex files to .jar in {self.output_dir}"
            logger.info(status)
            self.store_action("Convert", status, self.output_dir)
            return True
        else:
            status = "Conversion failed for all .dex files"
            logger.error(status)
            self.store_action("Convert", status)
            return False

    def analyze(self, jar_file: str):
        """Analyze the generated .jar file for basic information."""
        jar_name = os.path.splitext(os.path.basename(jar_file))[0]
        analysis_file = os.path.join(self.log_dir, f"{jar_name}_analysis.txt")

        try:
            cmd = ['jar', 'tf', jar_file]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            with open(analysis_file, 'w') as f:
                f.write("=== JAR Contents ===\n")
                f.write(result.stdout)
            status = f"Analyzed {jar_name}.jar, output saved to {analysis_file}"
            logger.info(status)
            self.store_action("Analyze", status, analysis_file)
            return True
        except Exception as e:
            status = f"Analysis failed: {str(e)}"
            logger.error(status)
            self.store_action("Analyze", status)
            return False

    def save_results(self):
        """Save action logs to JSON file."""
        with open(self.json_file, 'w') as f:
            json.dump({
                'input_path': self.input_path,
                'output_dir': self.output_dir,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Dex2Java: Tool for converting Android .dex files to .jar files.",
        epilog="Example: ./dex2java.py -a convert -i classes.dex -o output_dir"
    )
    parser.add_argument('-a', '--action', choices=['convert', 'analyze'],
                        required=True, help="Action to perform (convert, analyze)")
    parser.add_argument('-i', '--input', required=True,
                        help="Path to input .dex or .apk file")
    parser.add_argument('-o', '--output', default='dex2java-output',
                        help="Output directory (default: dex2java-output)")
    parser.add_argument('-j', '--jar-file',
                        help="Path to .jar file (required for analyze)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
           Dex2Java v1.0
      DEX to JAR Converter
    ==============================
    """)

    try:
        dex2java = Dex2Java(
            input_path=args.input,
            output_dir=args.output,
            quiet=args.quiet
        )

        if args.action == 'convert':
            dex2java.convert()
        elif args.action == 'analyze':
            if not args.jar_file:
                logger.error("JAR file path required for analysis")
                sys.exit(1)
            dex2java.analyze(args.jar_file)

        dex2java.save_results()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()