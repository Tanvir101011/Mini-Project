# ImageMeta

## Overview
ImageMeta is a command-line tool for forensic analysts, photographers, and developers to read, write, delete, and convert Exif, IPTC, and XMP metadata in image files (JPEG, TIFF, PNG, WebP), designed for Kali Linux. It supports digital forensics, photography workflows, and metadata management. Always back up images before modifying metadata, as changes are permanent.

## Features
- Reads metadata (Exif, IPTC, XMP) from JPEG, TIFF, PNG, and WebP images.
- Writes or modifies metadata (e.g., add copyright, adjust timestamps, set geotags).
- Deletes specified metadata tags or entire metadata sections.
- Converts between Exif, IPTC, and XMP (simplified implementation).
- Supports MakerNote tags for common camera vendors (e.g., Canon, Nikon).
- Outputs metadata to CSV files with detailed tag information.
- Generates a summary report with metadata statistics and modification logs.
- Handles batch processing for multiple files.
- Validates metadata integrity to detect inconsistencies.
- Lightweight and optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- Python library: `Pillow` (installed via setup script)
- Input image files (JPEG, TIFF, PNG, WebP)

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   chmod +x set_upfile.sh
   ./set_upfile.sh
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Usage
Run the tool with:
```bash
python imagemeta.py -f <file(s)> -a <action> [-t <type>] [-k <key>] [-v <value>] [--value-type <type>] [-o <output>] [--verbose]
```

- **-f, --files**: Input image files (e.g., `image.jpg`, multiple files supported).
- **-a, --action**: Action to perform (`read`, `write`, `delete`, `convert`).
- **-t, --type**: Metadata type (`all`, `exif`, `iptc`, `xmp`; default: `all`).
- **-k, --key**: Metadata key (e.g., `Exif.Image.Artist`, `2:5` for IPTC).
- **-v, --value**: Metadata value for write action.
- **--value-type**: Value type for write (default: `String`).
- **-o, --output**: Output directory (default: `imagemeta_output`).
- **--verbose**: Print detailed metadata information.

### Examples
1. **Read all metadata from an image**:
   ```bash
   python imagemeta.py -f image.jpg -a read -o results
   ```
   Output:
   ```
   [*] Starting read operation on 1 file(s)...
   [*] Results saved to results/imagemeta_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Operation complete. Total metadata entries: 15
   ```

2. **Read with verbose output**:
   ```bash
   python imagemeta.py -f image.jpg -a read --verbose
   ```
   Output:
   ```
   [*] Starting read operation on 1 file(s)...
   File: image.jpg
   Type: Exif
   Key: Exif.Image.Artist
   Value: John Doe...
   File: image.jpg
   Type: IPTC
   Key: 2:5
   Value: Copyright 2025...
   [*] Results saved to results/imagemeta_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Operation complete. Total metadata entries: 15
   ```

3. **Write a metadata tag**:
   ```bash
   python imagemeta.py -f image.jpg -a write -t exif -k Exif.Image.Artist -v "Jane Smith" -o results
   ```
   Output:
   ```
   [*] Starting write operation on 1 file(s)...
   [*] Wrote exif Exif.Image.Artist=Jane Smith to image.jpg
   [*] Summary report saved to results/summary.txt
   [*] Operation complete. Total metadata entries: 0
   ```

4. **Delete all Exif metadata**:
   ```bash
   python imagemeta.py -f image.jpg -a delete -t exif -o results
   ```
   Output:
   ```
   [*] Starting delete operation on 1 file(s)...
   [*] Deleted exif all from image.jpg
   [*] Summary report saved to results/summary.txt
   [*] Operation complete. Total metadata entries: 0
   ```

5. **Convert Exif to XMP**:
   ```bash
   python imagemeta.py -f image.jpg -a convert -t exif -o results
   ```
   Output:
   ```
   [*] Starting convert operation on 1 file(s)...
   [*] Summary report saved to results/summary.txt
   [*] Operation complete. Total metadata entries: 0
   ```

### Output Files
- **Results CSV** (`imagemeta_results.csv`):
  ```csv
  file,type,key,value
  image.jpg,Exif,Exif.Image.Artist,John Doe
  image.jpg,IPTC,2:5,Copyright 2025
  image.jpg,XMP,dc:creator,LinuxReviews.org
  ```
- **Summary report** (`summary.txt`):
  ```
  ImageMeta Summary Report - 2025-05-15T18:30:00
  --------------------------------------------------
  Total Metadata Entries: 15
  Operations Performed:
    Wrote exif Exif.Image.Artist=Jane Smith to image.jpg
    Deleted exif all from image.jpg
  --------------------------------------------------
  ```

## Limitations
- Supports fewer image formats (JPEG, TIFF, PNG, WebP) and metadata types (no ICC profiles, limited MakerNote support).
- Conversion between metadata types is basic (e.g., key renaming) and may not fully comply with standards.
- Limited validation of metadata standards; non-standard tags may be written.
- No support for extracting thumbnails or sidecar files.
- Assumes well-formed images; malformed files may cause errors.
- No command file support for batch modifications.

## License
MIT License

## Warning
ImageMeta is for ethical forensic analysis and authorized metadata management only. Unauthorized use against images or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before modifying metadata, and back up images before making changes. The author is not responsible for misuse.