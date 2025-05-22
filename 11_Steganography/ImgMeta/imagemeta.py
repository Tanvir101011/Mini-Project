import argparse
import csv
import os
from pathlib import Path
import sys
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, IFD
from PIL import PngImagePlugin, TiffImagePlugin
import re

class MetadataHandler:
    """Handle metadata operations for images."""
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = None
        self.exif = None
        self.iptc = None
        self.xmp = None

    def open_image(self):
        """Open image and load metadata."""
        try:
            self.image = Image.open(self.image_path)
            self.exif = self.image.getexif() if hasattr(self.image, 'getexif') else {}
            self.iptc = self.image.info.get('iptc', None)
            self.xmp = self.image.info.get('xmp', None)
            return True
        except Exception as e:
            print(f"[!] Error opening {self.image_path}: {e}")
            return False

    def read_metadata(self, metadata_type='all'):
        """Read specified metadata types."""
        results = []
        if not self.open_image():
            return results

        if metadata_type in ('all', 'exif'):
            for tag_id, value in self.exif.items():
                tag_name = TAGS.get(tag_id, f"Unknown_{tag_id}")
                if tag_id in IFD:
                    tag_name = f"MakerNote_{tag_name}"
                results.append({
                    'type': 'Exif',
                    'key': tag_name,
                    'value': str(value)[:500],  # Limit for safety
                    'file': self.image_path
                })

        if metadata_type in ('all', 'iptc') and self.iptc:
            try:
                from PIL import IptcImagePlugin
                iptc_data = IptcImagePlugin.getiptcinfo(self.image)
                if iptc_data:
                    for (record, dataset), value in iptc_data.items():
                        results.append({
                            'type': 'IPTC',
                            'key': f"{record}:{dataset}",
                            'value': value.decode('utf-8', errors='ignore')[:500],
                            'file': self.image_path
                        })
            except Exception as e:
                print(f"[!] Error reading IPTC: {e}")

        if metadata_type in ('all', 'xmp') and self.xmp:
            try:
                xmp_str = self.xmp.decode('utf-8', errors='ignore')
                for line in xmp_str.split('\n'):
                    if 'rdf:li' in line:
                        match = re.search(r'(\w+)=["\'](.*?)["\']', line)
                        if match:
                            results.append({
                                'type': 'XMP',
                                'key': match.group(1),
                                'value': match.group(2)[:500],
                                'file': self.image_path
                            })
            except Exception as e:
                print(f"[!] Error reading XMP: {e}")

        return results

    def write_metadata(self, metadata_type, key, value, value_type='String'):
        """Write metadata to the image."""
        if not self.open_image():
            return False

        try:
            if metadata_type == 'exif':
                tag_id = next((k for k, v in TAGS.items() if v == key), None)
                if not tag_id:
                    print(f"[!] Unknown Exif tag: {key}")
                    return False
                self.exif[tag_id] = value
                self.image.save(self.image_path, exif=self.exif)

            elif metadata_type == 'iptc':
                from PIL import IptcImagePlugin
                iptc_data = IptcImagePlugin.getiptcinfo(self.image) or {}
                record, dataset = map(int, key.split(':'))
                iptc_data[(record, dataset)] = value.encode('utf-8')
                iptc_bytes = IptcImagePlugin.iptc_to_bytes(iptc_data)
                self.image.info['iptc'] = iptc_bytes
                self.image.save(self.image_path, iptc=iptc_bytes)

            elif metadata_type == 'xmp':
                xmp_data = self.xmp.decode('utf-8', errors='ignore') if self.xmp else '<xmp></xmp>'
                new_tag = f'{key}="{value}"'
                xmp_data = xmp_data.replace('</xmp>', f'<rdf:li {new_tag}/></xmp>')
                self.image.info['xmp'] = xmp_data.encode('utf-8')
                self.image.save(self.image_path, xmp=xmp_data.encode('utf-8'))

            print(f"[*] Wrote {metadata_type} {key}={value} to {self.image_path}")
            return True
        except Exception as e:
            print(f"[!] Error writing metadata: {e}")
            return False

    def delete_metadata(self, metadata_type, key=None):
        """Delete specified metadata or entire section."""
        if not self.open_image():
            return False

        try:
            if metadata_type == 'exif':
                if key:
                    tag_id = next((k for k, v in TAGS.items() if v == key), None)
                    if tag_id and tag_id in self.exif:
                        del self.exif[tag_id]
                else:
                    self.exif.clear()
                self.image.save(self.image_path, exif=self.exif)

            elif metadata_type == 'iptc':
                if key:
                    from PIL import IptcImagePlugin
                    iptc_data = IptcImagePlugin.getiptcinfo(self.image) or {}
                    record, dataset = map(int, key.split(':'))
                    if (record, dataset) in iptc_data:
                        del iptc_data[(record, dataset)]
                        iptc_bytes = IptcImagePlugin.iptc_to_bytes(iptc_data)
                        self.image.info['iptc'] = iptc_bytes
                        self.image.save(self.image_path, iptc=iptc_bytes)
                else:
                    self.image.info['iptc'] = None
                    self.image.save(self.image_path)

            elif metadata_type == 'xmp':
                self.image.info['xmp'] = None
                self.image.save(self.image_path)

            print(f"[*] Deleted {metadata_type} {key or 'all'} from {self.image_path}")
            return True
        except Exception as e:
            print(f"[!] Error deleting metadata: {e}")
            return False

    def convert_metadata(self, from_type, to_type):
        """Convert metadata between types (simplified)."""
        results = self.read_metadata(from_type)
        converted = []
        for item in results:
            new_key = item['key'].replace(from_type, to_type)
            self.write_metadata(to_type.lower(), new_key, item['value'])
            converted.append(f"Converted {from_type} {item['key']} to {to_type} {new_key}")
        return converted

def process_files(input_files, action, metadata_type='all', key=None, value=None, value_type='String', output_dir='imagemeta_output'):
    """Process multiple files for the specified action."""
    results = []
    logs = []
    
    for file in input_files:
        handler = MetadataHandler(file)
        
        if action == 'read':
            results.extend(handler.read_metadata(metadata_type))
        elif action == 'write':
            if not key or not value:
                print(f"[!] Key and value required for write action.")
                continue
            if handler.write_metadata(metadata_type, key, value, value_type):
                logs.append(f"Wrote {metadata_type} {key}={value} to {file}")
        elif action == 'delete':
            if handler.delete_metadata(metadata_type, key):
                logs.append(f"Deleted {metadata_type} {key or 'all'} from {file}")
        elif action == 'convert':
            logs.extend(handler.convert_metadata(metadata_type, metadata_type.upper()))

    return results, logs

def save_results(results, output_dir, input_files):
    """Save metadata results to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'imagemeta_results.csv')
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['file', 'type', 'key', 'value']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        print(f"[*] Results saved to {output_file}")
    except Exception as e:
        print(f"[!] Error saving results: {e}")

def generate_summary(logs, output_dir, results):
    """Generate a summary report."""
    summary_file = os.path.join(output_dir, 'summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"ImageMeta Summary Report - {datetime.now().isoformat()}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total Metadata Entries: {len(results)}\n")
            f.write(f"Operations Performed:\n")
            for log in logs:
                f.write(f"  {log}\n")
            f.write("-" * 50 + "\n")
        print(f"[*] Summary report saved to {summary_file}")
    except Exception as e:
        print(f"[!] Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="ImageMeta: Manage image metadata (Exif, IPTC, XMP).")
    parser.add_argument('-f', '--files', required=True, nargs='+', help="Input image files (e.g., image.jpg).")
    parser.add_argument('-a', '--action', choices=['read', 'write', 'delete', 'convert'], required=True, help="Action to perform.")
    parser.add_argument('-t', '--type', choices=['all', 'exif', 'iptc', 'xmp'], default='all', help="Metadata type (default: all).")
    parser.add_argument('-k', '--key', help="Metadata key (e.g., Exif.Image.Artist, 2:5 for IPTC).")
    parser.add_argument('-v', '--value', help="Metadata value for write action.")
    parser.add_argument('--value-type', default='String', help="Value type for write (default: String).")
    parser.add_argument('-o', '--output', default='imagemeta_output', help="Output directory (default: imagemeta_output).")
    parser.add_argument('--verbose', action='store_true', help="Print detailed metadata information.")
    args = parser.parse_args()

    # Validate input files
    input_files = []
    for file in args.files:
        input_path = Path(file)
        if not input_path.is_file():
            print(f"[!] Input file {file} does not exist.")
            continue
        if not file.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png', '.webp')):
            print(f"[!] Input file {file} is not a supported format.")
            continue
        input_files.append(file)

    if not input_files:
        print("[!] No valid input files provided.")
        sys.exit(1)

    print(f"[*] Starting {args.action} operation on {len(input_files)} file(s)...")
    
    # Process files
    results, logs = process_files(input_files, args.action, args.type, args.key, args.value, args.value_type, args.output)

    # Print verbose output
    if args.verbose and results:
        for result in results:
            print(f"\nFile: {result['file']}")
            print(f"Type: {result['type']}")
            print(f"Key: {result['key']}")
            print(f"Value: {result['value'][:100]}...")

    # Save results and summary
    if results:
        save_results(results, args.output, input_files)
    generate_summary(logs, args.output, results)
    print(f"[*] Operation complete. Total metadata entries: {len(results)}")

if __name__ == "__main__":
    main()