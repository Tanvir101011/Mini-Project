# PNGProbe

## Overview
PNGProbe is a command-line tool for forensic analysts and security researchers to parse PNG image files, extract metadata, chunk details, and detect structural anomalies, designed for Kali Linux. It is a simplified alternative to `pnginfo`, suitable for digital forensics and security analysis.

## Features
- Parses PNG file structure, including signature and chunks (IHDR, PLTE, IDAT, tEXt, zTXt, etc.).
- Extracts metadata (e.g., image dimensions, color type, compression method, text comments).
- Validates chunk CRCs to detect tampering or corruption.
- Identifies non-standard or suspicious chunks.
- Outputs chunk details and metadata to CSV files.
- Generates a summary report with file statistics and anomaly alerts.
- Handles malformed PNGs gracefully with error reporting.
- Lightweight and optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- No external Python libraries required (uses standard libraries)
- Input PNG file

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
python pngprobe.py -f <file> [-o <output>] [-v]
```

- **-f, --file**: Input PNG file to parse (e.g., `sample.png`).
- **-o, --output**: Output directory for results (default: `pngprobe_output`).
- **-v, --verbose**: Print detailed chunk information.

### Examples
1. **Parse a PNG file**:
   ```bash
   python pngprobe.py -f sample.png -o results
   ```
   Output:
   ```
   [*] Starting analysis of sample.png...
   [*] Results saved to results/pngprobe_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total chunks: 8
   ```

2. **Parse with verbose output**:
   ```bash
   python pngprobe.py -f sample.png -o results -v
   ```
   Output:
   ```
   [*] Starting analysis of sample.png...
   Chunk: IHDR
     Offset: 0x8
     Length: 13
     CRC Valid: True
     Standard: True
     Data: {'width': 800, 'height': 600, 'bit_depth': 8, 'color_type': 2, ...}...
   Chunk: tEXt
     Offset: 0x25
     Length: 40
     CRC Valid: True
     Standard: True
     Data: {'keyword': 'Comment', 'value': 'Created with GIMP'}...
   [*] Results saved to results/pngprobe_results.csv
   [*] Summary report saved to results/summary.txt
   [*] Analysis complete. Total chunks: 8
   ```

### Output Files
- **Results CSV** (`pngprobe_results.csv`):
  ```csv
  input_file,chunk_type,offset,length,crc_valid,is_standard,data
  sample.png,IHDR,8,13,True,True,"{'width': 800, 'height': 600, 'bit_depth': 8, ...}"
  sample.png,tEXt,37,40,True,True,"{'keyword': 'Comment', 'value': 'Created with GIMP'}"
  ```
- **Summary report** (`summary.txt`):
  ```
  PNGProbe Summary Report - 2025-05-15T17:52:00
  --------------------------------------------------
  Total Chunks: 8
  Invalid CRCs: 0
  Non-Standard Chunks: 0
  IHDR Details:
    Width: 800
    Height: 600
    Bit Depth: 8
    Color Type: 2
    Compression: 0
    Filter Method: 0
    Interlace: 0
  --------------------------------------------------
  ```

## Limitations
- Simplified compared to `pnginfo`; lacks advanced features like pixel data analysis or full chunk data decoding (e.g., IDAT decompression).
- Limited to standard and common ancillary chunks; may not handle rare or proprietary chunks.
- Basic anomaly detection (CRC validation, non-standard chunks); may miss subtle tampering.
- Assumes well-formed PNGs; malformed files may cause partial parsing.
- No support for embedded ICC profiles or complex text encodings without modification.

## License
MIT License

## Warning
PNGProbe is for ethical forensic analysis and authorized security assessments only. Unauthorized use against files or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before analyzing PNG files. The author is not responsible for misuse.