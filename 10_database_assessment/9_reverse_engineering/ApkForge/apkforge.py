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
from concurrent.futures import ThreadPoolExecutor
import zipfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('apkforge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APKForge:
    def __init__(self, apk_path: str, output_dir: str = 'apkforge-output',
                 quiet: bool = False):
        self.apk_path = os.path.abspath(apk_path)
        self.output_dir = os.path.abspath(output_dir)
        self.quiet = quiet
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"forge_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'apkforge.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.actions = []
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('apkforge.log')]

    def init_db(self):
        """Initialize SQLite database for storing action logs."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apk_path TEXT,
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
                'INSERT INTO actions (apk_path, action, status, output_path, timestamp) '
                'VALUES (?, ?, ?, ?, ?)',
                (self.apk_path, action, status, output_path, timestamp)
            )
            conn.commit()
        self.actions.append({
            'apk_path': self.apk_path,
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

    def decompile(self, force: bool = False):
        """Decompile APK into resources and smali code."""
        apk_name = os.path.splitext(os.path.basename(self.apk_path))[0]
        decompile_dir = os.path.join(self.output_dir, f"{apk_name}_decompiled")
        if os.path.exists(decompile_dir) and force:
            shutil.rmtree(decompile_dir)
        os.makedirs(decompile_dir, exist_ok=True)

        # Extract resources and smali using aapt and apktool-like logic
        cmd = ['aapt', 'dump', 'xmltree', self.apk_path, 'AndroidManifest.xml']
        if not self.run_command(cmd, f"Dump AndroidManifest.xml for {apk_name}"):
            return False

        # Simulate decompilation by extracting APK contents
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                zip_ref.extractall(decompile_dir)
            status = f"Decompiled {apk_name} to {decompile_dir}"
            logger.info(status)
            self.store_action("Decompile", status, decompile_dir)
            return True
        except Exception as e:
            status = f"Decompilation failed: {str(e)}"
            logger.error(status)
            self.store_action("Decompile", status)
            return False

    def rebuild(self, decompile_dir: str):
        """Rebuild APK from decompiled resources."""
        apk_name = os.path.splitext(os.path.basename(self.apk_path))[0]
        rebuilt_apk = os.path.join(self.output_dir, f"{apk_name}_rebuilt.apk")
        temp_zip = os.path.join(self.output_dir, f"{apk_name}_temp.zip")

        # Rebuild APK by zipping decompiled contents
        try:
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for root, _, files in os.walk(decompile_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, decompile_dir)
                        zip_ref.write(file_path, arcname)
            shutil.move(temp_zip, rebuilt_apk)

            # Align and sign the APK
            cmd_align = ['zipalign', '-v', '-p', '4', rebuilt_apk,
                         rebuilt_apk + '.aligned']
            if not self.run_command(cmd_align, f"Align {apk_name} APK"):
                return False
            shutil.move(rebuilt_apk + '.aligned', rebuilt_apk)

            cmd_sign = ['apksigner', 'sign', '--ks', '/tmp/debug.keystore',
                        '--ks-pass', 'pass:android', rebuilt_apk]
            if not self.run_command(cmd_sign, f"Sign {apk_name} APK"):
                return False

            status = f"Rebuilt and signed {apk_name} to {rebuilt_apk}"
            logger.info(status)
            self.store_action("Rebuild", status, rebuilt_apk)
            return True
        except Exception as e:
            status = f"Rebuild failed: {str(e)}"
            logger.error(status)
            self.store_action("Rebuild", status)
            return False

    def analyze(self):
        """Analyze APK for basic information (e.g., manifest, permissions)."""
        apk_name = os.path.splitext(os.path.basename(self.apk_path))[0]
        analysis_file = os.path.join(self.log_dir, f"{apk_name}_analysis.txt")

        try:
            cmd = ['aapt', 'dump', 'badging', self.apk_path]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            with open(analysis_file, 'w') as f:
                f.write(result.stdout)
            status = f"Analyzed {apk_name}, output saved to {analysis_file}"
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
                'apk_path': self.apk_path,
                'output_dir': self.output_dir,
                'actions': self.actions,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="APKForge: Tool for reverse engineering and modifying Android APKs.",
        epilog="Example: ./apkforge.py -a decompile -i app.apk -o output_dir"
    )
    parser.add_argument('-a', '--action', choices=['decompile', 'rebuild', 'analyze'],
                        required=True, help="Action to perform (decompile, rebuild, analyze)")
    parser.add_argument('-i', '--input', required=True,
                        help="Path to input APK file")
    parser.add_argument('-o', '--output', default='apkforge-output',
                        help="Output directory (default: apkforge-output)")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Force overwrite of output directory for decompile")
    parser.add_argument('-d', '--decompile-dir',
                        help="Decompiled directory path (required for rebuild)")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
           APKForge v1.0
      APK Reverse Engineering
    ==============================
    """)

    try:
        forge = APKForge(
            apk_path=args.input,
            output_dir=args.output,
            quiet=args.quiet
        )

        if args.action == 'decompile':
            forge.decompile(force=args.force)
        elif args.action == 'rebuild':
            if not args.decompile_dir:
                logger.error("Decompiled directory required for rebuild")
                sys.exit(1)
            forge.rebuild(args.decompile_dir)
        elif args.action == 'analyze':
            forge.analyze()

        forge.save_results()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()