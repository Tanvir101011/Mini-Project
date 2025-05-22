import argparse
import re
import csv
import os
from pathlib import Path
import sys
import binascii
import subprocess
from datetime import datetime

def get_signatures():
    """Define file signatures for common formats."""
    return [
        {'type': 'ZIP', 'signature': b'\x50\x4B\x03\x04', 'extension': '.zip'},
        {'type': 'PNG', 'signature': b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', 'extension': '.png'},
        {'type': 'ELF', 'signature': b'\x7F\x45\x4C\x46', 'extension': '.elf'},
        {'type': 'PE', 'signature': b'\x4D\x5A', 'extension': '.exe'},
        {'type': 'TAR', 'signature': b'\x75\x73\x74\x61\x72', 'offset': 257, 'extension': '.tar'},
        {'type': 'JPEG', 'signature': b'\xFF\xD8\xFF', 'extension': '.jpg'},
        {'type': 'GZIP', 'signature': b'\x1F\x8B\x08', 'extension': '.gz'}
    ]

def scan_file(file_path, signatures, chunk_size=8192):
    """Scan a file for signatures and return matches with offsets."""
    results = []
    try:
        with open(file_path, 'rb') as f:
            offset = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                for sig in signatures:
                    signature = sig['signature']
                    sig_offset = sig.get('offset', 0)
                    if sig_offset == 0:
                        # Search for signature in chunk
                        pos = 0
                        while True:
                            idx = chunk.find(signature, pos)
                            if idx == -1:
                                break
                            results.append({
                                'type': sig['type'],
                                'offset': offset + idx,
                                'extension': sig['extension']
                            })
                            pos = idx + 1
                    elif offset <= sig_offset < offset + len(chunk):
                        # Check specific offset for signatures like TAR
                        if chunk[sig_offset - offset:sig_offset - offset + len(signature)] == signature:
                            results.append({
                                'type': sig['type'],
                                'offset': sig_offset,
                                'extension': sig['extension']
                            })
                offset += len(chunk)
    except Exception as e:
        print(f"[!] Error scanning {file_path}: {e}")
    return results

def verify_file_type(file_path, offset, file_type):
    """Verify file type using the 'file' command."""
    try:
        temp_file = f"temp_{offset}.bin"
        with open(file_path, 'rb') as f:
            f.seek(offset)
            data = f.read(1024 * 1024)  # Read up to 1MB for verification
        with open(temp_file, 'wb') as f:
            f.write(data)
        result = subprocess.check_output(['file', temp_file], text=True)
        os.remove(temp_file)
        return file_type.lower() in result.lower()
    except Exception as e:
        print(f"[!] Error verifying file type at offset {offset}: {e}")
        return False

def extract_file(file_path, result, output_dir):
    """Extract embedded file starting at the given offset."""
    try:
        output_file = os.path.join(output_dir, f"{result['type']}_{result['offset']}{result['extension']}")
        with open(file_path, 'rb') as f:
            f.seek(result['offset'])
            data = f.read(1024 * 1024)  # Extract up to 1MB (simplified)
            with open(output_file, 'wb') as out:
                out.write(data)
        print(f"[*] Extracted {result['type']} to {output_file}")
        return output_file
    except Exception as e:
        print(f"[!] Error extracting {result['type']} at offset {result['offset']}: {e}")
        return None

def save_results(results, output_dir, input_file):
    """Save scan results to a CSV file."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'binscan_results.csv')
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['input_file', 'type', 'offset', 'extension'])
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'input_file': input_file,
                    'type': result['type'],
                    'offset': result['offset'],
                    'extension': result['extension']
                })
        print(f"[*] Results saved to {output_file}")
    except Exception as e:
        print(f"[!] Error saving results: {e}")

def generate_summary(results, output_dir):
    """Generate a summary report."""
    summary = {}
    for result in results:
        file_type = result['type']
        summary[file_type] = summary.get(file_type, 0) + 1
    
    summary_file = os.path.join(output_dir, 'summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"BinScan Summary Report - {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            for file_type, count in summary.items():
                f.write(f"{file_type}: {count}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total signatures found: {len(results)}\n")
        print(f"[*] Summary report saved to {summary_file}")
    except Exception as e:
        print(f"[!] Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="BinScan: Analyze and extract embedded files from binaries.")
    parser.add_argument('-f', '--file', required=True, help="Input binary file to scan.")
    parser.add_argument('-o', '--output', default='binscan_output', help="Output directory for results and extracted files (default: binscan_output).")
    parser.add_argument('-e', '--extract', action='store_true', help="Extract detected files.")
    parser.add_argument('-c', '--chunk-size', type=int, default=8192, help="Chunk size for reading files (default: 8192).")
    args = parser.parse_args()

    # Validate input
    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"[!] Input file {args.file} does not exist.")
        sys.exit(1)

    print(f"[*] Starting analysis of {args.file}...")
    signatures = get_signatures()

    # Scan file
    results = scan_file(args.file, signatures, args.chunk_size)
    if not results:
        print("[!] No signatures found.")
        sys.exit(0)

    # Verify and filter results
    verified_results = []
    for result in results:
        if verify_file_type(args.file, result['offset'], result['type']):
            verified_results.append(result)
            print(f"[+] Found {result['type']} at offset 0x{result['offset']:x}")
        else:
            print(f"[!] False positive for {result['type']} at offset 0x{result['offset']:x}")

    if not verified_results:
        print("[!] No verified signatures found.")
        sys.exit(0)

    # Extract files if requested
    if args.extract:
        os.makedirs(args.output, exist_ok=True)
        for result in verified_results:
            extract_file(args.file, result, args.output)

    # Save results and summary
    save_results(verified_results, args.output, args.file)
    generate_summary(verified_results, args.output)
    print(f"[*] Analysis complete. Total signatures found: {len(verified_results)}")

if __name__ == "__main__":
    main()