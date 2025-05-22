import argparse
import csv
import os
from pathlib import Path
import sys
from datetime import datetime
import numpy as np
from PIL import Image
import logging

class StegoVision:
    """Handle steganography analysis for images."""
    def __init__(self, image_path, output_dir='stegovision_output'):
        self.image_path = image_path
        self.output_dir = output_dir
        self.image = None
        self.pixels = None
        self.logger = logging.getLogger(__name__)

    def open_image(self):
        """Open and validate image."""
        try:
            self.image = Image.open(self.image_path)
            if self.image.mode != 'RGB':
                self.image = self.image.convert('RGB')
            self.pixels = np.array(self.image)
            return True
        except Exception as e:
            self.logger.error(f"Error opening {self.image_path}: {e}")
            return False

    def extract_lsb(self, bit_plane=0, channel='all'):
        """Extract LSB data from specified bit plane and channel."""
        if not self.open_image():
            return None
        channels = {'r': 0, 'g': 1, 'b': 2}
        results = []
        bits = ''
        height, width, _ = self.pixels.shape
        for y in range(height):
            for x in range(width):
                pixel = self.pixels[y, x]
                if channel == 'all':
                    for ch in range(3):
                        bit = (pixel[ch] >> bit_plane) & 1
                        bits += str(bit)
                        results.append({
                            'x': x,
                            'y': y,
                            'channel': ['R', 'G', 'B'][ch],
                            'bit_plane': bit_plane,
                            'bit': bit
                        })
                else:
                    ch = channels[channel.lower()]
                    bit = (pixel[ch] >> bit_plane) & 1
                    bits += str(bit)
                    results.append({
                        'x': x,
                        'y': y,
                        'channel': channel.upper(),
                        'bit_plane': bit_plane,
                        'bit': bit
                    })
        # Convert bits to bytes (if possible)
        try:
            bytes_data = bytearray()
            for i in range(0, len(bits) - 7, 8):
                byte = bits[i:i+8]
                if len(byte) == 8:
                    bytes_data.append(int(byte, 2))
            text_data = bytes_data.decode('utf-8', errors='ignore').strip()
        except Exception:
            text_data = "Non-text data"
        return results, text_data

    def generate_bit_plane_image(self, bit_plane=0, channel='r'):
        """Generate grayscale image for a specific bit plane."""
        if not self.open_image():
            return False
        ch = {'r': 0, 'g': 1, 'b': 2}[channel.lower()]
        bit_plane_data = np.zeros((self.pixels.shape[0], self.pixels.shape[1]), dtype=np.uint8)
        for y in range(self.pixels.shape[0]):
            for x in range(self.pixels.shape[1]):
                bit = (self.pixels[y, x, ch] >> bit_plane) & 1
                bit_plane_data[y, x] = bit * 255  # Scale to 0 or 255
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, f"bitplane_{bit_plane}_{channel}.png")
            Image.fromarray(bit_plane_data, mode='L').save(output_path)
            self.logger.info(f"Bit plane image saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving bit plane image: {e}")
            return False

    def extract_channel(self, channel='r'):
        """Extract a single color channel as an image."""
        if not self.open_image():
            return False
        ch = {'r': 0, 'g': 1, 'b': 2}[channel.lower()]
        channel_data = np.zeros_like(self.pixels)
        channel_data[:, :, ch] = self.pixels[:, :, ch]
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, f"channel_{channel}.png")
            Image.fromarray(channel_data, mode='RGB').save(output_path)
            self.logger.info(f"Channel image saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving channel image: {e}")
            return False

    def histogram_analysis(self):
        """Perform histogram analysis for steganography detection."""
        if not self.open_image():
            return None
        histograms = []
        for ch in range(3):
            hist, _ = np.histogram(self.pixels[:, :, ch], bins=256, range=(0, 256))
            histograms.append(hist)
        # Simplified anomaly detection: check for unusual uniformity
        anomaly_score = 0
        for hist in histograms:
            variance = np.var(hist)
            if variance < 100:  # Arbitrary threshold for uniformity
                anomaly_score += 1
        return {
            'r_histogram': histograms[0].tolist(),
            'g_histogram': histograms[1].tolist(),
            'b_histogram': histograms[2].tolist(),
            'anomaly_score': anomaly_score
        }

    def estimate_capacity(self):
        """Estimate embedding capacity."""
        if not self.open_image():
            return 0
        height, width, _ = self.pixels.shape
        return (height * width * 3 * 8) // 8  # Bytes (3 channels, 8 bits per pixel)

    def save_results(self, results, action, bit_plane, channel):
        """Save analysis results to CSV."""
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, f"{action}_results.csv")
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['x', 'y', 'channel', 'bit_plane', 'bit']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for result in results:
                    writer.writerow(result)
            self.logger.info(f"Results saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

    def generate_summary(self, results, text_data, histogram_data, capacity):
        """Generate a summary report."""
        summary_file = os.path.join(self.output_dir, 'summary.txt')
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"StegoVision Summary Report - {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Image: {self.image_path}\n")
                f.write(f"Estimated Capacity: {capacity} bytes\n")
                f.write(f"LSB Entries: {len(results)}\n")
                f.write(f"Extracted Text: {text_data[:100]}{'...' if len(text_data) > 100 else ''}\n")
                f.write(f"Histogram Anomaly Score: {histogram_data['anomaly_score'] if histogram_data else 'N/A'}\n")
                if histogram_data and histogram_data['anomaly_score'] > 0:
                    f.write("Warning: Potential steganography detected (uniform histogram).\n")
                f.write("-" * 50 + "\n")
            self.logger.info(f"Summary report saved to {summary_file}")
        except Exception as e:
            self.logger.error(f"Error saving summary: {e}")

def main():
    parser = argparse.ArgumentParser(description="StegoVision: Analyze images for hidden steganography data.")
    parser.add_argument('-i', '--input', required=True, help="Input image file (BMP, PNG, JPEG, GIF).")
    parser.add_argument('-a', '--action', choices=['lsb', 'bitplane', 'channel', 'histogram'], required=True, help="Analysis action.")
    parser.add_argument('-b', '--bit-plane', type=int, default=0, choices=range(8), help="Bit plane to analyze (0-7, default: 0).")
    parser.add_argument('-c', '--channel', choices=['r', 'g', 'b', 'all'], default='all', help="Color channel (r, g, b, all; default: all).")
    parser.add_argument('-o', '--output-dir', default='stegovision_output', help="Output directory (default: stegovision_output).")
    parser.add_argument('--verbose', action='store_true', help="Print detailed results.")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Validate input
    input_path = Path(args.input)
    if not input_path.is_file() or not args.input.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg', '.gif')):
        logger.error(f"Input {args.input} is not a valid image file.")
        sys.exit(1)

    stego = StegoVision(args.input, args.output_dir)
    results = []
    text_data = ""
    histogram_data = None

    if args.action == 'lsb':
        results, text_data = stego.extract_lsb(args.bit_plane, args.channel)
        if results:
            stego.save_results(results, args.action, args.bit_plane, args.channel)
    elif args.action == 'bitplane':
        if not stego.generate_bit_plane_image(args.bit_plane, args.channel):
            sys.exit(1)
    elif args.action == 'channel':
        if not stego.extract_channel(args.channel):
            sys.exit(1)
    elif args.action == 'histogram':
        histogram_data = stego.histogram_analysis()
        if not histogram_data:
            sys.exit(1)

    # Print verbose output
    if args.verbose and results:
        for result in results[:10]:  # Limit to first 10 for brevity
            logger.info(f"X: {result['x']}, Y: {result['y']}, Channel: {result['channel']}, Bit Plane: {result['bit_plane']}, Bit: {result['bit']}")
        if len(results) > 10:
            logger.info(f"... {len(results) - 10} more entries ...")

    # Generate summary
    capacity = stego.estimate_capacity()
    stego.generate_summary(results, text_data, histogram_data, capacity)
    logger.info(f"Analysis complete. Results in {args.output_dir}")

if __name__ == "__main__":
    main()