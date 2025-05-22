# BinScan

## Overview
BinScan is a command-line tool for reverse engineers and penetration testers to analyze binary files (e.g., firmware, executables) and extract embedded files, designed for Kali Linux. It identifies file signatures (e.g., ZIP, PNG, ELF) and extracts embedded data, making it suitable for reverse engineering and forensic analysis. BinScan is a simplified alternative to `binwalk`, focusing on core signature scanning and file carving.

## Features
- Identifies common file signatures (ZIP, PNG, ELF, PE, tar, JPEG, GZIP).
- Extracts embedded files to an output directory.
- Supports recursive extraction for nested archives.
- Outputs results to a CSV file with metadata (input file, type, offset, extension).
- Generates a summary report with counts of detected signatures.
- Handles large files efficiently with chunked reading.
- Lightweight and optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- `file` command (for magic checks, pre-installed on Kali)
- No external Python libraries required (uses standard libraries)
- Input binary file (e.g., firmware image, executable)

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to create a virtual environment:
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
python binscan.py -f <file> [-o <output>] [-e] [-c <chunk_size>]
```

- **-f, --file**: Input binary file to scan (e.g., `firmware.bin`).
- **-o, --output**: Output directory for results and extracted files (default: `binscan_output`).
- **-e, --extract**: Extract detected files.
- **-c, --chunk-size**: Chunk size for reading files (default: 8192).

### Examples
1. **Scan a firmware image**:
   ```bash
   python binscan.py -f firmware.bin -o results
   ```
   Output:
   ```
   [*] Starting analysis of firmware.bin...
   [+] Found ZIP at offset 0x1000
   [+] Found ELF at offset 0x5000
   [*] Results saved to results/binscan_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total signatures found: 2
   ```

2. **Scan and extract files**:
   ```bash
   python binscan.py -f firmware.bin -o results -e -c 16384
   ```
   Output:
   ```
   [*] Starting analysis of firmware.bin...
   [+] Found ZIP at offset 0x1000
   [*] Extracted ZIP to results/ZIP_4096.zip
   [+] Found ELF at offset 0x5000
   [*] Extracted ELF to results/ELF_20480.elf
   [*] Results saved to results/binscan_results.csv
   [*] Summary report saved to results/summary.txt
   ```

### Output Files
- **CSV file** (`binscan_results.csv`):
  ```csv
  input_file,type,offset,extension
  firmware.bin,ZIP,4096,.zip
  firmware.bin,ELF,20480,.elf
  ```
- **Summary report** (`summary.txt`):
  ```
  BinScan Summary Report - 2025-05-15T15:35:00
  --------------------------------------------------
  ZIP: 1
  ELF: 1
  --------------------------------------------------
  Total signatures found: 2
  ```
- **Extracted files** (if `-e` is used):
  ```
  results/ZIP_4096.zip
  results/ELF_20480.elf
  ```

## Limitations
- Simplified compared to `binwalk`; lacks advanced features like entropy analysis, opcode scanning, or support for complex filesystems (e.g., SquashFS, UBI).
- Limited to predefined signatures; custom signatures require code modification.
- Basic extraction (up to 1MB per file); may miss large or fragmented files.
- No support for compressed or encrypted data without external tools.
- Relies on `file` command for verification, which may not catch all false positives.

## License
MIT License

## Warning
BinScan is for ethical reverse engineering and authorized security assessments only. Unauthorized use against systems or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before analyzing binaries. The author is not responsible for misuse.