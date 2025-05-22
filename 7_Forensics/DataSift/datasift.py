import argparse
import re
import csv
import os
from pathlib import Path
import sys
from datetime import datetime

def get_patterns():
    """Define regex patterns for data extraction."""
    return {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'url': re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'),
        'credit_card': re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
        'phone': re.compile(r'\b(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b')
    }

def extract_context(data, start, end, context_size=50):
    """Extract surrounding context for a match."""
    start_context = max(0, start - context_size)
    end_context = min(len(data), end + context_size)
    return data[start_context:end_context].replace('\n', ' ').strip()

def scan_file(file_path, patterns, chunk_size=8192):
    """Scan a file for patterns and yield matches with metadata."""
    results = []
    try:
        with open(file_path, 'rb') as f:
            offset = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                try:
                    text = chunk.decode('utf-8', errors='ignore')
                except UnicodeDecodeError:
                    text = chunk.decode('latin1', errors='ignore')
                
                for data_type, pattern in patterns.items():
                    for match in pattern.finditer(text):
                        start, end = match.start(), match.end()
                        context = extract_context(text, start, end)
                        results.append({
                            'type': data_type,
                            'value': match.group(),
                            'file': file_path,
                            'offset': offset + start,
                            'context': context
                        })
                offset += len(chunk)
    except Exception as e:
        print(f"[!] Error scanning {file_path}: {e}")
    return results

def scan_directory(dir_path, patterns):
    """Recursively scan a directory for files."""
    results = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            results.extend(scan_file(file_path, patterns))
    return results

def save_results(results, output_dir):
    """Save results to CSV files by data type."""
    os.makedirs(output_dir, exist_ok=True)
    by_type = {}
    
    for result in results:
        data_type = result['type']
        if data_type not in by_type:
            by_type[data_type] = []
        by_type[data_type].append(result)
    
    for data_type, items in by_type.items():
        output_file = os.path.join(output_dir, f"{data_type}_results.csv")
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['type', 'value', 'file', 'offset', 'context'])
                writer.writeheader()
                writer.writerows(items)
            print(f"[*] Saved {len(items)} {data_type} results to {output_file}")
        except Exception as e:
            print(f"[!] Error saving {data_type} results: {e}")

def generate_summary(results, output_dir):
    """Generate a summary report."""
    summary = {'email': 0, 'url': 0, 'credit_card': 0, 'phone': 0}
    for result in results:
        summary[result['type']] += 1
    
    summary_file = os.path.join(output_dir, 'summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"DataSift Summary Report - {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            for data_type, count in summary.items():
                f.write(f"{data_type.capitalize()}: {count}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total items extracted: {len(results)}\n")
        print(f"[*] Summary report saved to {summary_file}")
    except Exception as e:
        print(f"[!] Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="DataSift: Extract structured data from unstructured sources.")
    parser.add_argument('-i', '--input', required=True, help="Input file or directory to scan.")
    parser.add_argument('-o', '--output', default='datasift_output', help="Output directory for results (default: datasift_output).")
    parser.add_argument('-c', '--chunk-size', type=int, default=8192, help="Chunk size for reading files (default: 8192).")
    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[!] Input path {args.input} does not exist.")
        sys.exit(1)

    print("[*] Starting data extraction...")
    patterns = get_patterns()

    # Scan input
    if input_path.is_file():
        results = scan_file(input_path, patterns, args.chunk_size)
    else:
        results = scan_directory(input_path, patterns)

    if not results:
        print("[!] No data extracted.")
        sys.exit(0)

    # Save results and summary
    save_results(results, args.output)
    generate_summary(results, args.output)
    print(f"[*] Extraction complete. Total items found: {len(results)}")

if __name__ == "__main__":
    main()