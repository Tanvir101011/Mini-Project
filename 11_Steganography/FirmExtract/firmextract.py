import argparse
import csv
import os
from pathlib import Path
import sys
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import magic
import logging
import shutil
import subprocess

class FirmExtract:
    """Handle firmware analysis and extraction."""
    def __init__(self, firmware_path, output_dir='firmextract_output'):
        self.firmware_path = firmware_path
        self.output_dir = output_dir
        self.firmware_data = None
        self.signatures = []
        self.logger = logging.getLogger(__name__)
        self.mime = magic.Magic(mime=True)

    def load_firmware(self):
        """Load firmware file into memory."""
        try:
            with open(self.firmware_path, 'rb') as f:
                self.firmware_data = f.read()
            return True
        except Exception as e:
            self.logger.error(f"Error loading {self.firmware_path}: {e}")
            return False

    def scan_signatures(self):
        """Scan firmware for file signatures."""
        if not self.load_firmware():
            return False
        self.signatures = []
        offset = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        while offset < len(self.firmware_data):
            try:
                chunk = self.firmware_data[offset:offset + chunk_size]
                sig = self.mime.from_buffer(chunk)
                if sig != 'application/octet-stream':  # Ignore generic binary
                    self.signatures.append({
                        'offset': offset,
                        'type': sig,
                        'description': self._get_description(sig),
                        'size': self._estimate_size(offset, sig)
                    })
                offset += 1024  # Step size to avoid excessive overlap
            except Exception as e:
                self.logger.warning(f"Error scanning at offset {offset}: {e}")
                offset += 1024
        return True

    def _get_description(self, mime_type):
        """Map MIME types to human-readable descriptions."""
        descriptions = {
            'application/x-executable': 'ELF executable',
            'application/x-gzip': 'Gzip compressed data',
            'application/x-xz': 'XZ compressed data',
            'application/x-tar': 'Tar archive',
            'application/x-uboot': 'U-Boot image',
            'application/x-squashfs': 'SquashFS filesystem',
            'application/x-jffs2': 'JFFS2 filesystem',
            'application/x-trx': 'TRX firmware header',
            'text/plain': 'ASCII text',
            'image/jpeg': 'JPEG image'
        }
        return descriptions.get(mime_type, mime_type)

    def _estimate_size(self, offset, mime_type):
        """Estimate size of detected file (simplified)."""
        # In real-world, use format-specific parsing (e.g., ELF headers, gzip headers)
        remaining = len(self.firmware_data) - offset
        return min(remaining, 1024 * 1024)  # Cap at 1MB for safety

    def extract_files(self, recursive=False):
        """Extract identified files to output directory."""
        if not self.signatures:
            self.logger.error("No signatures to extract. Run scan first.")
            return False
        os.makedirs(self.output_dir, exist_ok=True)
        for sig in self.signatures:
            try:
                output_path = os.path.join(self.output_dir, f"offset_{sig['offset']}_{sig['type'].split('/')[-1]}")
                with open(output_path, 'wb') as f:
                    f.write(self.firmware_data[sig['offset']:sig['offset'] + sig['size']])
                self.logger.info(f"Extracted {sig['description']} to {output_path}")
                if recursive and sig['type'] in ['application/x-gzip', 'application/x-tar', 'application/x-xz']:
                    self._recursive_extract(output_path)
            except Exception as e:
                self.logger.error(f"Error extracting at offset {sig['offset']}: {e}")
        return True

    def _recursive_extract(self, file_path):
        """Recursively extract archives."""
        try:
            temp_dir = os.path.join(self.output_dir, 'temp_recursive')
            os.makedirs(temp_dir, exist_ok=True)
            if file_path.endswith('gzip') or file_path.endswith('gz'):
                subprocess.run(['tar', '-xzf', file_path, '-C', temp_dir], check=True)
            elif file_path.endswith('xz'):
                subprocess.run(['tar', '-xJf', file_path, '-C', temp_dir], check=True)
            elif file_path.endswith('tar'):
                subprocess.run(['tar', '-xf', file_path, '-C', temp_dir], check=True)
            self.logger.info(f"Recursively extracted {file_path} to {temp_dir}")
        except Exception as e:
            self.logger.error(f"Error in recursive extraction of {file_path}: {e}")

    def entropy_analysis(self, plot=False):
        """Perform entropy analysis on firmware data."""
        if not self.load_firmware():
            return None
        block_size = 1024
        entropy_values = []
        for i in range(0, len(self.firmware_data), block_size):
            block = self.firmware_data[i:i + block_size]
            if len(block) == 0:
                continue
            freq = np.histogram(np.frombuffer(block, dtype=np.uint8), bins=256, density=True)[0]
            entropy = -np.sum([p * np.log2(p + 1e-10) for p in freq if p > 0])
            entropy_values.append(entropy)
        if plot:
            os.makedirs(self.output_dir, exist_ok=True)
            plt.figure(figsize=(10, 6))
            plt.plot(entropy_values)
            plt.title('Entropy Analysis')
            plt.xlabel('Block Index')
            plt.ylabel('Entropy')
            output_plot = os.path.join(self.output_dir, 'entropy_plot.png')
            plt.savefig(output_plot)
            plt.close()
            self.logger.info(f"Entropy plot saved to {output_plot}")
        return entropy_values

    def save_results(self):
        """Save scan results to CSV."""
        if not self.signatures:
            self.logger.error("No results to save.")
            return
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, 'scan_results.csv')
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['offset', 'type', 'description', 'size']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for sig in self.signatures:
                    writer.writerow(sig)
            self.logger.info(f"Results saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

    def generate_summary(self, entropy_values):
        """Generate a summary report."""
        summary_file = os.path.join(self.output_dir, 'summary.txt')
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"FirmExtract Summary Report - {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Firmware: {self.firmware_path}\n")
                f.write(f"File Size: {len(self.firmware_data) if self.firmware_data else 0} bytes\n")
                f.write(f"Signatures Found: {len(self.signatures)}\n")
                for sig in self.signatures[:5]:  # Limit to first 5 for brevity
                    f.write(f"Offset: {sig['offset']}, Type: {sig['description']}, Size: {sig['size']} bytes\n")
                if len(self.signatures) > 5:
                    f.write(f"... {len(self.signatures) - 5} more signatures ...\n")
                avg_entropy = np.mean(entropy_values) if entropy_values else 0
                f.write(f"Average Entropy: {avg_entropy:.2f}\n")
                if avg_entropy > 7.5:
                    f.write("Warning: High entropy suggests compressed or encrypted data.\n")
                f.write("-" * 50 + "\n")
            self.logger.info(f"Summary report saved to {summary_file}")
        except Exception as e:
            self.logger.error(f"Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="FirmExtract: Analyze and extract firmware images.")
    parser.add_argument('-i', '--input', required=True, help="Input firmware image file.")
    parser.add_argument('-a', '--action', choices=['scan', 'extract', 'entropy'], required=True, help="Action to perform.")
    parser.add_argument('-o', '--output-dir', default='firmextract_output', help="Output directory (default: firmextract_output).")
    parser.add_argument('--recursive', action='store_true', help="Enable recursive extraction.")
    parser.add_argument('--plot', action='store_true', help="Generate entropy plot (for entropy action).")
    parser.add_argument('--verbose', action='store_true', help="Print detailed results.")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Validate input
    input_path = Path(args.input)
    if not input_path.is_file():
        logger.error(f"Input {args.input} is not a valid file.")
        sys.exit(1)

    firm = FirmExtract(args.input, args.output_dir)
    entropy_values = []

    if args.action == 'scan':
        if firm.scan_signatures():
            firm.save_results()
            if args.verbose:
                for sig in firm.signatures[:10]:  # Limit to first 10
                    logger.info(f"Offset: {sig['offset']}, Type: {sig['description']}, Size: {sig['size']} bytes")
                if len(firm.signatures) > 10:
                    logger.info(f"... {len(firm.signatures) - 10} more signatures ...")
    elif args.action == 'extract':
        if firm.scan_signatures():
            firm.extract_files(recursive=args.recursive)
    elif args.action == 'entropy':
        entropy_values = firm.entropy_analysis(plot=args.plot)
        if not entropy_values:
            sys.exit(1)

    # Generate summary
    firm.generate_summary(entropy_values)
    logger.info(f"Analysis complete. Results in {args.output_dir}")

if __name__ == "__main__":
    main()