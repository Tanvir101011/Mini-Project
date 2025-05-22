# FirmExtract

## Overview
FirmExtract is a command-line tool for cybersecurity researchers and forensic analysts to analyze firmware images, identifying and extracting embedded files, file systems, and executable code, designed for Kali Linux. It uses signature-based scanning, entropy analysis, and file extraction to support reverse engineering and security vulnerability assessment, suitable for IoT and embedded device analysis.

## Features
- Scans firmware for file signatures (e.g., ELF, gzip, SquashFS, JFFS2) using `python-magic`.
- Extracts identified files and file systems to a specified directory.
- Performs entropy analysis to detect compressed or encrypted regions, with optional PNG visualization.
- Supports recursive extraction for nested archives or file systems.
- Estimates file system and code offsets, with simplified CPU architecture detection.
- Outputs scan results to CSV, logs to console/file, and entropy plots to PNG.
- Handles common firmware formats (e.g., raw binaries, TRX, U-Boot images).
- Generates a summary report with analysis statistics and security indicators.
- Optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- Python libraries: `python-magic`, `numpy`, `matplotlib` (installed via setup script)
- System dependencies: `libmagic-dev`, `tar`, `xz-utils` (installed via setup script)
- Input firmware image (e.g., `.bin` file)

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to install system dependencies, create a virtual environment, and install Python dependencies:
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
python firmextract.py -i <input> -a <action> [-o <output-dir>] [--recursive] [--plot] [--verbose]
```

- **-i, --input**: Input firmware image file (e.g., `firmware.bin`).
- **-a, --action**: Analysis action (`scan`, `extract`, `entropy`).
- **-o, --output-dir**: Output directory (default: `firmextract_output`).
- **--recursive**: Enable recursive extraction (for `extract` action).
- **--plot**: Generate entropy plot (for `entropy` action).
- **--verbose**: Print detailed results.

### Examples
1. **Scan firmware for embedded files**:
   ```bash
   python firmextract.py -i firmware.bin -a scan -o results --verbose
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Offset: 0, Type: TRX firmware header, Size: 1048576 bytes
   2025-05-15 18:30:00 - INFO - Offset: 2097152, Type: SquashFS filesystem, Size: 1048576 bytes
   2025-05-15 18:30:00 - INFO - Results saved to results/scan_results.csv
   2025-05-15 18:30:00 - INFO - Summary report saved to results/summary.txt
   2025-05-15 18:30:00 - INFO - Analysis complete. Results in results
   ```

2. **Extract embedded files**:
   ```bash
   python firmextract.py -i firmware.bin -a extract -o results --recursive
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Extracted TRX firmware header to results/offset_0_x-trx
   2025-05-15 18:30:00 - INFO - Extracted SquashFS filesystem to results/offset_2097152_x-squashfs
   2025-05-15 18:30:00 - INFO - Recursively extracted results/offset_2097152_x-squashfs to results/temp_recursive
   2025-05-15 18:30:00 - INFO - Summary report saved to results/summary.txt
   2025-05-15 18:30:00 - INFO - Analysis complete. Results in results
   ```

3. **Perform entropy analysis with plot**:
   ```bash
   python firmextract.py -i firmware.bin -a entropy -o results --plot
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Entropy plot saved to results/entropy_plot.png
   2025-05-15 18:30:00 - INFO - Summary report saved to results/summary.txt
   2025-05-15 18:30:00 - INFO - Analysis complete. Results in results
   ```

### Output Files
- **Scan Results CSV** (`scan_results.csv`):
  ```csv
  offset,type,description,size
  0,application/x-trx,TRX firmware header,1048576
  2097152,application/x-squashfs,SquashFS filesystem,1048576
  ```
- **Extracted Files** (e.g., `offset_0_x-trx`): Binary files extracted at detected offsets.
- **Entropy Plot** (`entropy_plot.png`): Visualization of entropy across firmware blocks.
- **Summary Report** (`summary.txt`):
  ```
  FirmExtract Summary Report - 2025-05-15T18:30:00
  --------------------------------------------------
  Firmware: firmware.bin
  File Size: 4194304 bytes
  Signatures Found: 2
  Offset: 0, Type: TRX firmware header, Size: 1048576 bytes
  Offset: 2097152, Type: SquashFS filesystem, Size: 1048576 bytes
  Average Entropy: 7.80
  Warning: High entropy suggests compressed or encrypted data.
  --------------------------------------------------
  ```

## Limitations
- Signature-based scanning may miss proprietary or obfuscated formats.
- Simplified size estimation; real-world parsing requires format-specific logic (e.g., ELF headers).
- Recursive extraction supports only gzip, tar, and xz; additional formats require custom extractors.
- Entropy analysis is block-based; may not detect small encrypted regions.
- No support for direct CPU architecture identification or opcode scanning (use complementary tools like `radare2`).
- Assumes well-formed firmware images; corrupted files may cause errors.

## License
MIT License

## Warning
FirmExtract is for ethical forensic analysis and authorized security research only. Unauthorized use against firmware or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before analyzing firmware images. The author is not responsible for misuse.