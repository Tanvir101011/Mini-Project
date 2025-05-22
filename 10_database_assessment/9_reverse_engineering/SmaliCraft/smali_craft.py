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
        logging.FileHandler('smali_craft.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmaliCraft:
    def __init__(self, input_path: str, output_dir: str = 'smali_craft-output',
                 quiet: bool = False):
        self.input_path = os.path.abspath(input_path)
        self.output_dir = os.path.abspath(output_dir)
        self.quiet = quiet
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"smali_craft_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'smali_craft.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.actions = []
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('smali_craft.log')]

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
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
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

    def disassemble(self, force: bool = False):
        """Disassemble .dex file(s) to .smali."""
        dex_files = self.extract_dex() if self.input_path.endswith('.apk') else [self.input_path]
        if not dex_files:
            logger.error("No .dex files to disassemble")
            return False

        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        smali_dir = os.path.join(self.output_dir, f"{input_name}_smali")
        if os.path.exists(smali_dir) and force:
            shutil.rmtree(smali_dir)
        os.makedirs(smali_dir, exist_ok=True)

        success = False
        for dex_file in dex_files:
            cmd = ['baksmali', 'disassemble', dex_file, '-o', smali_dir]
            if self.run_command(cmd, f"Disassemble {os.path.basename(dex_file)} to smali"):
                success = True

        if success:
            status = f"Disassembled .dex files to {smali_dir}"
            logger.info(status)
            self.store_action("Disassemble", status, smali_dir)
            return True
        else:
            status = "Disassembly failed for all .dex files"
            logger.error(status)
            self.store_action("Disassemble", status)
            return False

    def assemble(self, smali_dir: str):
        """Assemble .smali files back to .dex."""
        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        dex_file = os.path.join(self.output_dir, f"{input_name}.dex")

        cmd = ['smali', 'assemble', smali_dir, '-o', dex_file]
        if self.run_command(cmd, f"Assemble smali from {smali_dir} to {dex_file}"):
            status = f"Assembled smali to {dex_file}"
            logger.info(status)
            self.store_action("Assemble", status, dex_file)
            return True
        else:
            status = "Assembly failed"
            logger.error(status)
            self.store_action("Assemble", status)
            return False

    def analyze(self, smali_dir: str):
        """Analyze .smali files for basic statistics."""
        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        analysis_file = os.path.join(self.log_dir, f"{input_name}_analysis.txt")

        try:
            smali_count = 0
            total_lines = 0
            for root, _, files in os.walk(smali_dir):
                for file in files:
                    if file.endswith('.smali'):
                        smali_count += 1
                        with open(os.path.join(root, file), 'r') as f:
                            total_lines += len(f.readlines())

            with open(analysis_file, 'w') as f:
                f.write("=== Smali Analysis ===\n")
                f.write(f"Total .smali files: {smali_count}\n")
                f.write(f"Total lines of smali code: {total_lines}\n")
                f.write(f"Smali directory: {smali_dir}\n")

            status = f"Analyzed smali, output saved to {analysis_file}"
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
        description="SmaliCraft: Tool for disassembling and assembling Android .smali files.",
        epilog="Example: ./smali_craft.py -a disassemble -i classes.dex -o output_dir"
    )
    parser.add_argument('-a', '--action', choices=['disassemble', 'assemble', 'analyze'],
                        required=True, help="Action to perform (disassemble, assemble, analyze)")
    parser.add_argument('-i', '--input', required=True,
                        help="Path to input .dex or .apk file")
    parser.add_argument('-o', '--output', default='smali_craft-output',
                        help="Output directory (default: smali_craft-output)")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Force overwrite of output directory for disassemble")
    parser.add_argument('-s', '--smali-dir',
                        help="Smali directory path (required for assemble or analyze)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
           SmaliCraft v1.0
      Smali Assembler/Disassembler
    ==============================
    """)

    try:
        smali_craft = SmaliCraft(
            input_path=args.input,
            output_dir=args.output,
            quiet=args.quiet
        )

        if args.action == 'disassemble':
            smali_craft.disassemble(force=args.force)
        elif args.action == 'assemble':
            if not args.smali_dir:
                logger.error("Smali directory required for assembly")
                sys.exit(1)
            smali_craft.assemble(args.smali_dir)
        elif args.action == 'analyze':
            if not args.smali_dir:
                logger.error("Smali directory required for analysis")
                sys.exit(1)
            smali_craft.analyze(args.smali_dir)

        smali_craft.save_results()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()