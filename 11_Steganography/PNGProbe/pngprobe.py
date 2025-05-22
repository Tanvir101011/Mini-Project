import argparse
import struct
import zlib
import csv
import os
from pathlib import Path
import sys
from datetime import datetime

def read_png(file_path):
    """Read PNG file content and validate signature."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        # PNG signature: \x89PNG\r\n\x1a\n
        if not data.startswith(b'\x89PNG\x0D\x0A\x1A\x0A'):
            print(f"[!] {file_path} is not a valid PNG file.")
            sys.exit(1)
        return data
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        sys.exit(1)

def parse_chunks(data):
    """Parse PNG chunks and extract details."""
    chunks = []
    offset = 8  # Skip PNG signature
    standard_chunks = {'IHDR', 'PLTE', 'IDAT', 'IEND', 'tEXt', 'zTXt', 'iTXt', 'tIME', 'gAMA', 'cHRM', 'sRGB', 'iCCP'}
    
    while offset < len(data):
        try:
            # Read chunk length (4 bytes)
            length = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            # Read chunk type (4 bytes)
            chunk_type = data[offset:offset+4].decode('ascii')
            offset += 4
            # Read chunk data
            chunk_data = data[offset:offset+length]
            offset += length
            # Read CRC (4 bytes)
            crc = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            
            # Validate CRC
            calculated_crc = zlib.crc32(data[offset-8-length:offset-4]) & 0xFFFFFFFF
            crc_valid = crc == calculated_crc
            
            # Decode chunk data
            decoded_data = None
            if chunk_type == 'IHDR' and length == 13:
                width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack('>IIBBBBB', chunk_data)
                decoded_data = {
                    'width': width,
                    'height': height,
                    'bit_depth': bit_depth,
                    'color_type': color_type,
                    'compression': compression,
                    'filter_method': filter_method,
                    'interlace': interlace
                }
            elif chunk_type in ('tEXt', 'zTXt', 'iTXt'):
                try:
                    if chunk_type == 'zTXt':
                        null_idx = chunk_data.find(b'\x00')
                        keyword = chunk_data[:null_idx].decode('ascii')
                        compression_method = chunk_data[null_idx+1]
                        compressed_data = chunk_data[null_idx+2:]
                        if compression_method == 0:  # zlib
                            decoded_data = zlib.decompress(compressed_data).decode('utf-8', errors='ignore')
                        else:
                            decoded_data = 'Unsupported compression'
                    else:
                        text = chunk_data.decode('utf-8', errors='ignore')
                        keyword, value = text.split('\x00', 1) if '\x00' in text else (text, '')
                        decoded_data = {'keyword': keyword, 'value': value}
                except Exception as e:
                    decoded_data = f"Error decoding: {e}"
            
            chunks.append({
                'type': chunk_type,
                'length': length,
                'offset': offset - length - 12,
                'crc_valid': crc_valid,
                'data': decoded_data if decoded_data else chunk_data[:100].hex(),  # Limit raw data
                'is_standard': chunk_type in standard_chunks
            })
        except Exception as e:
            print(f"[!] Error parsing chunk at offset {offset}: {e}")
            break
    
    return chunks

def save_results(chunks, output_dir, input_file):
    """Save chunk details to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'pngprobe_results.csv')
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['input_file', 'chunk_type', 'offset', 'length', 'crc_valid', 'is_standard', 'data']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for chunk in chunks:
                writer.writerow({
                    'input_file': input_file,
                    'chunk_type': chunk['type'],
                    'offset': chunk['offset'],
                    'length': chunk['length'],
                    'crc_valid': chunk['crc_valid'],
                    'is_standard': chunk['is_standard'],
                    'data': str(chunk['data'])[:500]  # Limit for safety
                })
        print(f"[*] Results saved to {output_file}")
    except Exception as e:
        print(f"[!] Error saving results: {e}")

def generate_summary(chunks, output_dir):
    """Generate a summary report."""
    total_chunks = len(chunks)
    invalid_crcs = sum(1 for c in chunks if not c['crc_valid'])
    non_standard = sum(1 for c in chunks if not c['is_standard'])
    ihdr = next((c for c in chunks if c['type'] == 'IHDR'), None)
    
    summary_file = os.path.join(output_dir, 'summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"PNGProbe Summary Report - {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total Chunks: {total_chunks}\n")
            f.write(f"Invalid CRCs: {invalid_crcs}\n")
            f.write(f"Non-Standard Chunks: {non_standard}\n")
            if ihdr and isinstance(ihdr['data'], dict):
                f.write("\nIHDR Details:\n")
                f.write(f"  Width: {ihdr['data']['width']}\n")
                f.write(f"  Height: {ihdr['data']['height']}\n")
                f.write(f"  Bit Depth: {ihdr['data']['bit_depth']}\n")
                f.write(f"  Color Type: {ihdr['data']['color_type']}\n")
                f.write(f"  Compression: {ihdr['data']['compression']}\n")
                f.write(f"  Filter Method: {ihdr['data']['filter_method']}\n")
                f.write(f"  Interlace: {ihdr['data']['interlace']}\n")
            if invalid_crcs:
                f.write("\nInvalid CRC Chunks:\n")
                for c in chunks:
                    if not c['crc_valid']:
                        f.write(f"  {c['type']} at offset 0x{c['offset']:x}\n")
            if non_standard:
                f.write("\nNon-Standard Chunks:\n")
                for c in chunks:
                    if not c['is_standard']:
                        f.write(f"  {c['type']} at offset 0x{c['offset']:x}\n")
            f.write("-" * 50 + "\n")
        print(f"[*] Summary report saved to {summary_file}")
    except Exception as e:
        print(f"[!] Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="PNGProbe: Analyze PNG files for metadata and structure.")
    parser.add_argument('-f', '--file', required=True, help="Input PNG file to parse.")
    parser.add_argument('-o', '--output', default='pngprobe_output', help="Output directory for results (default: pngprobe_output).")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print detailed chunk information.")
    args = parser.parse_args()

    # Validate input
    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"[!] Input file {args.file} does not exist.")
        sys.exit(1)
    if not args.file.lower().endswith('.png'):
        print(f"[!] Input file {args.file} is not a PNG.")
        sys.exit(1)

    print(f"[*] Starting analysis of {args.file}...")
    data = read_png(args.file)
    
    # Parse chunks
    chunks = parse_chunks(data)
    if not chunks:
        print("[!] No chunks found in PNG.")
        sys.exit(0)

    # Print verbose output
    if args.verbose:
        for chunk in chunks:
            print(f"\nChunk: {chunk['type']}")
            print(f"  Offset: 0x{chunk['offset']:x}")
            print(f"  Length: {chunk['length']}")
            print(f"  CRC Valid: {chunk['crc_valid']}")
            print(f"  Standard: {chunk['is_standard']}")
            print(f"  Data: {str(chunk['data'])[:100]}...")

    # Save results and summary
    save_results(chunks, args.output, args.file)
    generate_summary(chunks, args.output)
    print(f"[*] Analysis complete. Total chunks: {len(chunks)}")

if __name__ == "__main__":
    main()