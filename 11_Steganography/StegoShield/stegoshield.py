import argparse
import os
from pathlib import Path
import sys
from datetime import datetime
import numpy as np
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import struct
import logging

class StegoShield:
    """Handle steganography operations for JPEG images."""
    def __init__(self, image_path, key, output_dir='stegoshield_output'):
        self.image_path = image_path
        self.key = key.encode('utf-8')[:32].ljust(32, b'\x00')  # AES-256 key
        self.output_dir = output_dir
        self.image = None
        self.dct_coeffs = None
        self.logger = logging.getLogger(__name__)

    def open_image(self):
        """Open and validate JPEG image."""
        try:
            self.image = Image.open(self.image_path)
            if self.image.format != 'JPEG':
                self.logger.error(f"{self.image_path} is not a JPEG image.")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error opening {self.image_path}: {e}")
            return False

    def get_dct_coefficients(self):
        """Simulate DCT coefficient access (simplified)."""
        # In a real implementation, use a library like libjpeg to access DCT coefficients
        # Here, we simulate by converting image to YCbCr and using pixel values
        try:
            ycbcr = self.image.convert('YCbCr')
            self.dct_coeffs = np.array(ycbcr).flatten()
            return True
        except Exception as e:
            self.logger.error(f"Error accessing DCT coefficients: {e}")
            return False

    def encrypt_data(self, data):
        """Encrypt data with AES-256."""
        try:
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            # Pad data to multiple of 16 bytes
            padded_data = data + b'\x00' * (16 - len(data) % 16)
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            return iv + encrypted
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            return None

    def decrypt_data(self, encrypted_data):
        """Decrypt data with AES-256."""
        try:
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(ciphertext) + decryptor.finalize()
            # Remove padding
            return decrypted.rstrip(b'\x00')
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            return None

    def estimate_capacity(self):
        """Estimate embedding capacity (simplified)."""
        if not self.dct_coeffs:
            return 0
        # Assume 1 bit per non-zero coefficient, excluding zeros and ones
        usable_coeffs = len([c for c in self.dct_coeffs if c not in (0, 1)])
        return usable_coeffs // 8  # Bytes

    def embed_data(self, data, output_path):
        """Embed data into JPEG image."""
        if not self.open_image() or not self.get_dct_coefficients():
            return False

        # Encrypt data
        data = struct.pack('>I', len(data)) + data  # Prepend length
        encrypted_data = self.encrypt_data(data)
        if not encrypted_data:
            return False

        # Check capacity
        capacity = self.estimate_capacity()
        if len(encrypted_data) > capacity:
            self.logger.error(f"Data too large ({len(encrypted_data)} bytes) for image capacity ({capacity} bytes).")
            return False

        # Convert data to bits
        bits = ''.join(format(byte, '08b') for byte in encrypted_data)
        bit_idx = 0
        new_coeffs = self.dct_coeffs.copy()

        # Embed bits into LSBs of non-zero, non-one coefficients
        for i, coeff in enumerate(new_coeffs):
            if coeff not in (0, 1) and bit_idx < len(bits):
                new_coeffs[i] = (coeff & ~1) | int(bits[bit_idx])
                bit_idx += 1
            if bit_idx >= len(bits):
                break

        if bit_idx < len(bits):
            self.logger.error("Insufficient coefficients to embed all data.")
            return False

        # Save modified image (simplified, real DCT manipulation requires libjpeg)
        try:
            modified_image = Image.fromarray(new_coeffs.reshape(self.image.size[1], self.image.size[0], 3).astype(np.uint8), 'YCbCr')
            modified_image = modified_image.convert('RGB')
            os.makedirs(self.output_dir, exist_ok=True)
            modified_image.save(output_path, quality=90)
            self.logger.info(f"Stego image saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving stego image: {e}")
            return False

    def extract_data(self):
        """Extract data from stego image."""
        if not self.open_image() or not self.get_dct_coefficients():
            return None

        # Extract bits from LSBs
        bits = ''
        for coeff in self.dct_coeffs:
            if coeff not in (0, 1):
                bits += str(coeff & 1)
                if len(bits) >= 8 * 1024:  # Limit to avoid infinite loops
                    break

        # Convert bits to bytes
        try:
            bytes_data = bytearray()
            for i in range(0, len(bits) - 7, 8):
                byte = bits[i:i+8]
                if len(byte) == 8:
                    bytes_data.append(int(byte, 2))
            encrypted_data = bytes_data

            # Decrypt data
            decrypted_data = self.decrypt_data(encrypted_data)
            if not decrypted_data:
                return None

            # Extract length and data
            if len(decrypted_data) < 4:
                self.logger.error("Invalid decrypted data length.")
                return None
            data_length = struct.unpack('>I', decrypted_data[:4])[0]
            if len(decrypted_data[4:]) < data_length:
                self.logger.error("Incomplete data extracted.")
                return None
            return decrypted_data[4:4+data_length]
        except Exception as e:
            self.logger.error(f"Error extracting data: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="StegoShield: Embed and extract hidden data in JPEG images.")
    parser.add_argument('-a', '--action', choices=['embed', 'extract'], required=True, help="Action to perform.")
    parser.add_argument('-i', '--input', required=True, help="Input JPEG image.")
    parser.add_argument('-d', '--data', help="Data file or text to embed (for embed action).")
    parser.add_argument('-o', '--output', default='stego.jpg', help="Output stego image (for embed) or data file (for extract).")
    parser.add_argument('-k', '--key', required=True, help="Encryption key.")
    parser.add_argument('--output-dir', default='stegoshield_output', help="Output directory (default: stegoshield_output).")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Validate input
    input_path = Path(args.input)
    if not input_path.is_file() or not args.input.lower().endswith('.jpg') and not args.input.lower().endswith('.jpeg'):
        logger.error(f"Input {args.input} is not a valid JPEG file.")
        sys.exit(1)

    stego = StegoShield(args.input, args.key, args.output_dir)

    if args.action == 'embed':
        if not args.data:
            logger.error("Data file or text required for embed action.")
            sys.exit(1)
        # Read data
        if Path(args.data).is_file():
            with open(args.data, 'rb') as f:
                data = f.read()
        else:
            data = args.data.encode('utf-8')
        
        if stego.embed_data(data, args.output):
            logger.info("Embedding complete.")
        else:
            logger.error("Embedding failed.")
            sys.exit(1)

    elif args.action == 'extract':
        data = stego.extract_data()
        if data:
            os.makedirs(args.output_dir, exist_ok=True)
            output_path = Path(args.output_dir) / args.output
            if output_path.suffix:
                with open(output_path, 'wb') as f:
                    f.write(data)
            else:
                logger.info(f"Extracted data: {data.decode('utf-8', errors='ignore')}")
            logger.info(f"Extraction complete. Data saved to {output_path}")
        else:
            logger.error("Extraction failed.")
            sys.exit(1)

if __name__ == "__main__":
    main()