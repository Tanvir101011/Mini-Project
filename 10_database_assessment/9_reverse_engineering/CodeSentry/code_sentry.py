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
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('code_sentry.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CodeSentry:
    def __init__(self, input_path: str, output_dir: str = 'code_sentry-output',
                 quiet: bool = False):
        self.input_path = os.path.abspath(input_path)
        self.output_dir = os.path.abspath(output_dir)
        self.quiet = quiet
        self.log_dir = os.path.join(self.output_dir, 'logs')
        self.json_file = os.path.join(self.log_dir,
            f"code_sentry_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.log_dir, 'code_sentry.db')
        os.makedirs(self.log_dir, exist_ok=True)
        self.actions = []
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('code_sentry.log')]

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

    def run_command(self, cmd: List[str], action: str) -> bool:
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

    def extract_dex(self) -> List[str]:
        """Extract .dex files from APK or return input .dex file."""
        if not self.input_path.endswith('.apk'):
            return [self.input_path]  # Assume input is .dex or .class

        dex_files = []
        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        extract_dir = os.path.join(self.output_dir, f"{input_name}_extracted")
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

    def extract_class(self) -> List[str]:
        """Extract .class files from JAR or return input .class file."""
        if not self.input_path.endswith('.jar'):
            return [self.input_path]  # Assume input is .class

        class_files = []
        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        extract_dir = os.path.join(self.output_dir, f"{input_name}_extracted")
        os.makedirs(extract_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(self.input_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith('.class'):
                        zip_ref.extract(file, extract_dir)
                        class_files.append(os.path.join(extract_dir, file))
            if not class_files:
                status = "No .class files found in JAR"
                logger.error(status)
                self.store_action("Extract Class", status)
                return []
            status = f"Extracted {len(class_files)} .class files to {extract_dir}"
            logger.info(status)
            self.store_action("Extract Class", status, extract_dir)
            return class_files
        except Exception as e:
            status = f"Class extraction failed: {str(e)}"
            logger.error(status)
            self.store_action("Extract Class", status)
            return []

    def decompile_to_java(self, force: bool = False):
        """Decompile .dex, .apk, .class, or .jar to Java source code using jadx."""
        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        java_dir = os.path.join(self.output_dir, f"{input_name}_java")
        if os.path.exists(java_dir) and force:
            shutil.rmtree(java_dir)
        os.makedirs(java_dir, exist_ok=True)

        cmd = ['jadx', '-d', java_dir, self.input_path]
        if self.run_command(cmd, f"Decompile {input_name} to Java"):
            status = f"Decompiled to Java source in {java_dir}"
            logger.info(status)
            self.store_action("Decompile Java", status, java_dir)
            return True
        return False

    def decompile_to_smali(self, force: bool = False):
        """Disassemble .dex or .apk to smali code using baksmali."""
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
            status = f"Disassembled to smali in {smali_dir}"
            logger.info(status)
            self.store_action("Decompile Smali", status, smali_dir)
            return True
        return False

    def view_bytecode(self):
        """View Java bytecode for .class or .jar files using javap."""
        class_files = self.extract_class() if self.input_path.endswith('.jar') else [self.input_path]
        if not class_files:
            logger.error("No .class files to view")
            return False

        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        bytecode_file = os.path.join(self.log_dir, f"{input_name}_bytecode.txt")

        try:
            with open(bytecode_file, 'w') as f:
                for class_file in class_files:
                    cmd = ['javap', '-c', class_file]
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    f.write(f"=== Bytecode for {class_file} ===\n")
                    f.write(result.stdout)
                    f.write("\n")
            status = f"Bytecode saved to {bytecode_file}"
            logger.info(status)
            self.store_action("View Bytecode", status, bytecode_file)
            return True
        except Exception as e:
            status = f"Bytecode viewing failed: {str(e)}"
            logger.error(status)
            self.store_action("View Bytecode", status)
            return False

    def analyze(self):
        """Analyze input file for basic information."""
        input_name = os.path.splitext(os.path.basename(self.input_path))[0]
        analysis_file = os.path.join(self.log_dir, f"{input_name}_analysis.txt")

        try:
            info = []
            if self.input_path.endswith(('.dex', '.apk')):
                cmd = ['aapt', 'dump', 'badging', self.input_path]
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                info.append("=== APK/DEX Info ===\n")
                info.append(result.stdout)
            elif self.input_path.endswith(('.class', '.jar')):
                class_files = self.extract_class() if self.input_path.endswith('.jar') else [self.input_path]
                info.append("=== Class/JAR Info ===\n")
                for class_file in class_files:
                    cmd = ['javap', '-public', class_file]
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    info.append(f"Class: {class_file}\n")
                    info.append(result.stdout)
                    info.append("\n")

            with open(analysis_file, 'w') as f:
                f.writelines(info)
            status = f"Analysis saved to {analysis_file}"
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
                'timestamp': time.strftime('%Y-%m-d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="CodeSentry: Tool for analyzing and decompiling bytecode.",
        epilog="Example: ./code_sentry.py -a decompile-java -i classes.dex -o output_dir"
    )
    parser.add_argument('-a', '--action', choices=['decompile-java', 'decompile-smali', 'view-bytecode', 'analyze'],
                        required=True, help="Action to perform (decompile-java, decompile-smali, view-bytecode, analyze)")
    parser.add_argument('-i', '--input', required=True,
                        help="Path to input .dex, .apk, .class, or .jar file")
    parser.add_argument('-o', '--output', default='code_sentry-output',
                        help="Output directory (default: code_sentry-output)")
    parser.add_argument('-f', '--force', action='store_true',
                        help="Force overwrite of output directory for decompilation")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
          CodeSentry v1.0
      Bytecode Analysis Tool
    ==============================
    """)

    try:
        sentry = CodeSentry(
            input_path=args.input,
            output_dir=args.output,
            quiet=args.quiet
        )

        if args.action == 'decompile-java':
            sentry.decompile_to_java(force=args.force)
        elif args.action == 'decompile-smali':
            if args.input.endswith(('.class', '.jar')):
                logger.error("Smali decompilation not supported for .class or .jar files")
                sys.exit(1)
            sentry.decompile_to_smali(force=args.force)
        elif args.action == 'view-bytecode':
            if not args.input.endswith(('.class', '.jar')):
                logger.error("Bytecode viewing only supported for .class or .jar files")
                sys.exit(1)
            sentry.view_bytecode()
        elif args.action == 'analyze':
            sentry.analyze()

        sentry.save_results()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()