import argparse
import logging
import os
import sys
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from PIL import IptcImagePlugin
import glob

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('metaextract.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class MetaExtract:
    def __init__(self, files, output_file=None, quiet=False):
        self.files = files
        self.output_file = output_file or f"metaextract_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.quiet = quiet
        self.results = []

    def get_exif(self, img):
        """Extract EXIF metadata from an image."""
        try:
            exif_data = img._getexif()
            if not exif_data:
                return {}
            return {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
        except Exception as e:
            logging.error(f"Error extracting EXIF: {str(e)}")
            return {}

    def get_iptc(self, img):
        """Extract IPTC metadata from an image."""
        try:
            iptc_data = IptcImagePlugin.getiptcinfo(img)
            if not iptc_data:
                return {}
            iptc_dict = {}
            for key, value in iptc_data.items():
                iptc_dict[f"IPTC_{key}"] = value.decode('utf-8', errors='ignore')
            return iptc_dict
        except Exception as e:
            logging.error(f"Error extracting IPTC: {str(e)}")
            return {}

    def extract_metadata(self, file_path):
        """Extract metadata from a single file."""
        try:
            with Image.open(file_path) as img:
                metadata = {'file': file_path, 'exif': self.get_exif(img), 'iptc': self.get_iptc(img)}
                self.results.append(metadata)
                logging.info(f"Extracted metadata from {file_path}: {len(metadata['exif'])} EXIF, {len(metadata['iptc'])} IPTC tags")
                return metadata
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            return None

    def modify_metadata(self, file_path, tag, value):
        """Modify a specific metadata tag."""
        try:
            with Image.open(file_path) as img:
                exif = img._getexif() or {}
                # Simple EXIF modification (e.g., Artist, XPComment)
                tag_id = next((k for k, v in TAGS.items() if v == tag), None)
                if tag_id:
                    exif[tag_id] = value
                    img.save(file_path, exif=exif)
                    logging.info(f"Modified {tag} to '{value}' in {file_path}")
                else:
                    logging.error(f"Tag {tag} not supported for modification")
        except Exception as e:
            logging.error(f"Error modifying {file_path}: {str(e)}")

    def remove_metadata(self, file_path):
        """Remove all metadata from a file."""
        try:
            with Image.open(file_path) as img:
                img.save(file_path, exif=None, iptc=None)
                logging.info(f"Removed metadata from {file_path}")
        except Exception as e:
            logging.error(f"Error removing metadata from {file_path}: {str(e)}")

    def save_results(self):
        """Save extracted metadata to a file."""
        with open(self.output_file, 'w') as f:
            for result in self.results:
                f.write(f"File: {result['file']}\n")
                f.write("EXIF Metadata:\n")
                for key, value in result['exif'].items():
                    f.write(f"  {key}: {value}\n")
                f.write("IPTC Metadata:\n")
                for key, value in result['iptc'].items():
                    f.write(f"  {key}: {value}\n")
                f.write(f"{'-'*50}\n")
        logging.info(f"Results saved to {self.output_file}")

    def process_files(self, modify=None, remove=False):
        """Process all input files."""
        logging.info(f"Starting MetaExtract: Files={len(self.files)}")
        for file_path in self.files:
            if not os.path.exists(file_path):
                logging.error(f"File not found: {file_path}")
                continue
            if remove:
                self.remove_metadata(file_path)
            elif modify:
                tag, value = modify
                self.modify_metadata(file_path, tag, value)
            else:
                self.extract_metadata(file_path)
        if not remove and not modify:
            self.save_results()

def main():
    parser = argparse.ArgumentParser(description="MetaExtract - A tool to explore image metadata for learning.")
    parser.add_argument('files', nargs='+', help='Image files or glob pattern (e.g., *.jpg)')
    parser.add_argument('-o', '--output', help='Output file for metadata (default: auto-generated)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')
    parser.add_argument('-m', '--modify', nargs=2, metavar=('TAG', 'VALUE'), help='Modify a metadata tag (e.g., Artist "John Doe")')
    parser.add_argument('-r', '--remove', action='store_true', help='Remove all metadata')

    args = parser.parse_args()

    # Expand glob patterns
    files = []
    for pattern in args.files:
        files.extend(glob.glob(pattern))

    if not files:
        logging.error("No files found matching the input pattern")
        sys.exit(1)

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('metaextract.log')]

    extractor = MetaExtract(files=files, output_file=args.output, quiet=args.quiet)
    extractor.process_files(modify=args.modify, remove=args.remove)

if __name__ == "__main__":
    main()