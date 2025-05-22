# StegoVision

## Overview
StegoVision is a command-line tool for cybersecurity researchers and forensic analysts to analyze images (BMP, PNG, JPEG, GIF) for hidden data using steganography techniques, designed for Kali Linux. It supports LSB extraction, bit plane analysis, color channel manipulation, and histogram analysis to detect and extract hidden data, suitable for forensic investigations and security research.

## Features
- Extracts LSB data from specified bit planes (0–7) across color channels (R, G, B).
- Performs bit plane analysis to visualize individual bit planes as grayscale images.
- Supports color channel extraction and manipulation (e.g., isolate R, G, B channels).
- Conducts histogram analysis to detect statistical anomalies indicative of steganography.
- Estimates embedding capacity based on image size and bit planes.
- Outputs extracted data to CSV files and saves manipulated images (bit planes, channels).
- Generates a summary report with analysis statistics and steganography indicators.
- Handles multiple image formats (BMP, PNG, JPEG, GIF).
- Optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- Python libraries: `Pillow`, `numpy` (installed via setup script)
- Input image file (BMP, PNG, JPEG, GIF)

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
python stegovision.py -i <input> -a <action> [-b <bit-plane>] [-c <channel>] [-o <output-dir>] [--verbose]
```

- **-i, --input**: Input image file (e.g., `image.png`).
- **-a, --action**: Analysis action (`lsb`, `bitplane`, `channel`, `histogram`).
- **-b, --bit-plane**: Bit plane to analyze (0–7; default: 0).
- **-c, --channel**: Color channel (`r`, `g`, `b`, `all`; default: `all`).
- **-o, --output-dir**: Output directory (default: `stegovision_output`).
- **--verbose**: Print detailed results.

### Examples
1. **Extract LSB data from bit plane 0 (all channels)**:
   ```bash
   python stegovision.py -i image.png -a lsb -b 0 -c all -o results
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Results saved to results/lsb_results.csv
   2025-05-15 18:30:00 - INFO - Summary report saved to results/summary.txt
   2025-05-15 18:30:00 - INFO - Analysis complete. Results in results
   ```

2. **Generate bit plane image for bit plane 1 (red channel)**:
   ```bash
   python stegovision.py -i image.png -a bitplane -b 1 -c r -o results
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Bit plane image saved to results/bitplane_1_r.png
   2025-05-15 18:30:00 - INFO - Summary report saved to results/summary.txt
   2025-05-15 18:30:00 - INFO - Analysis complete. Results in results
   ```

3. **Extract green channel**:
   ```bash
   python stegovision.py -i image.png -a channel -c g -o results
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Channel image saved to results/channel_g.png
   2025-05-15 18:30:00 - INFO - Summary report saved to results/summary.txt
   2025-05-15 18:30:00 - INFO - Analysis complete. Results in results
   ```

4. **Perform histogram analysis**:
   ```bash
   python stegovision.py -i image.png -a histogram -o results --verbose
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Summary report saved to results/summary.txt
   2025-05-15 18:30:00 - INFO - Analysis complete. Results in results
   ```

### Output Files
- **LSB Results CSV** (`lsb_results.csv`):
  ```csv
  x,y,channel,bit_plane,bit
  0,0,R,0,1
  0,0,G,0,0
  0,0,B,0,1
  ```
- **Bit Plane Images** (e.g., `bitplane_0_r.png`): Grayscale images showing specified bit plane.
- **Channel Images** (e.g., `channel_g.png`): Images isolating a single color channel.
- **Summary Report** (`summary.txt`):
  ```
  StegoVision Summary Report - 2025-05-15T18:30:00
  --------------------------------------------------
  Image: image.png
  Estimated Capacity: 307200 bytes
  LSB Entries: 921600
  Extracted Text: Non-text data
  Histogram Anomaly Score: 0
  --------------------------------------------------
  ```

## Limitations
- Limited to RGB images; grayscale or indexed images are converted to RGB.
- Simplified histogram analysis; may not detect advanced steganography techniques (e.g., F5, adaptive methods).
- No support for audio or video steganography.
- LSB extraction assumes text data; binary data may require manual inspection.
- No GUI; command-line only for simplicity.
- Assumes well-formed images; malformed files may cause errors.

## License
MIT License

## Warning
StegoVision is for ethical forensic analysis and authorized security research only. Unauthorized use against images or data you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before analyzing images. The author is not responsible for misuse.