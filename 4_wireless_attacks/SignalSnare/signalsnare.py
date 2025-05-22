#!/usr/bin/env python3

import argparse
import logging
import sys
import time
import json
import os
import subprocess
import sqlite3
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading
import scipy.signal as signal
import sounddevice as sd
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('signalsnare.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SignalSnare:
    def __init__(self, input_file: str = None, frequency: float = None, sample_rate: int = 22050,
                 demodulators: list = None, quiet: bool = False, threads: int = 5):
        self.input_file = input_file
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.demodulators = demodulators or ['POCSAG512', 'POCSAG1200', 'POCSAG2400', 'DTMF']
        self.quiet = quiet
        self.threads = threads
        self.output_dir = 'signalsnare-output'
        self.output_file = os.path.join(self.output_dir, 
            f"snare_{time.strftime('%Y%m%d_%H%M%S')}.txt")
        self.json_file = os.path.join(self.output_dir, 
            f"snare_{time.strftime('%Y%m%d_%H%M%S')}.json")
        self.db_file = os.path.join(self.output_dir, 'signalsnare.db')
        os.makedirs(self.output_dir, exist_ok=True)
        self.messages = []
        self.running = True
        self.init_db()
        if quiet:
            logging.getLogger().handlers = [logging.FileHandler('signalsnare.log')]

    def init_db(self):
        """Initialize SQLite database for storing decoded messages."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol TEXT,
                    message TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def store_message(self, protocol: str, message: str):
        """Store decoded message in database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO messages (protocol, message, timestamp) VALUES (?, ?, ?)',
                (protocol, message, timestamp)
            )
            conn.commit()
        self.messages.append({
            'protocol': protocol,
            'message': message,
            'timestamp': timestamp
        })

    def setup_rtl_fm(self):
        """Set up rtl_fm for real-time SDR input."""
        if not self.frequency:
            logger.error("Frequency required for SDR input")
            sys.exit(1)
        logger.info(f"Setting up rtl_fm at {self.frequency} MHz")
        cmd = [
            'rtl_fm', '-M', 'fm', '-f', f'{self.frequency}M', '-s', str(self.sample_rate),
            '-g', '38', '-l', '310'
        ]
        try:
            return subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start rtl_fm: {e}")
            sys.exit(1)

    def read_audio(self):
        """Read audio from file or SDR."""
        if self.input_file:
            logger.info(f"Reading from file: {self.input_file}")
            cmd = ['sox', self.input_file, '-t', 'raw', '-e', 'signed-integer', 
                   '-b', '16', '-r', str(self.sample_rate), '-']
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            return proc.stdout
        else:
            proc = self.setup_rtl_fm()
            return proc.stdout

    def dtmf_decoder(self, audio_chunk: np.ndarray):
        """Decode DTMF tones from audio chunk."""
        dtmf_freqs = {
            '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
            '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
            '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
            '*': (941, 1209), '0': (941, 1336), '#': (941, 1477)
        }
        chunk_len = len(audio_chunk)
        freqs = np.fft.fftfreq(chunk_len, 1/self.sample_rate)
        spectrum = np.abs(np.fft.fft(audio_chunk))
        
        detected = []
        for char, (low, high) in dtmf_freqs.items():
            low_idx = np.argmin(np.abs(freqs - low))
            high_idx = np.argmin(np.abs(freqs - high))
            if (spectrum[low_idx] > 1e5 and spectrum[high_idx] > 1e5):
                detected.append(char)
        
        if detected:
            message = ''.join(detected)
            logger.info(f"DTMF: {message}")
            self.store_message('DTMF', message)

    def pocsag_decoder(self, audio_chunk: np.ndarray, baud_rate: int):
        """Decode POCSAG signals at specified baud rate."""
        # FM demodulation
        analytic_signal = signal.hilbert(audio_chunk)
        fm_signal = np.angle(analytic_signal[1:] * np.conj(analytic_signal[:-1]))
        
        # Resample to match baud rate
        samples_per_symbol = self.sample_rate / baud_rate
        num_symbols = int(len(fm_signal) / samples_per_symbol)
        resampled = signal.resample(fm_signal, num_symbols)
        
        # Binarize signal
        bits = (resampled > 0).astype(int)
        
        # Simple POCSAG frame detection (simplified for demo)
        message = ''
        for i in range(0, len(bits) - 32, 32):
            frame = bits[i:i+32]
            if sum(frame) > 8:  # Arbitrary threshold for valid frame
                address = int(''.join(map(str, frame[:21])), 2)
                message += f"Address: {address} "
        
        if message:
            protocol = f"POCSAG{baud_rate}"
            logger.info(f"{protocol}: {message}")
            self.store_message(protocol, message)

    def process_chunk(self, chunk: np.ndarray):
        """Process audio chunk with enabled demodulators."""
        for demod in self.demodulators:
            if demod == 'DTMF':
                self.dtmf_decoder(chunk)
            elif demod in ['POCSAG512', 'POCSAG1200', 'POCSAG2400']:
                baud_rate = int(demod.replace('POCSAG', ''))
                self.pocsag_decoder(chunk, baud_rate)

    def run(self):
        """Run SignalSnare decoding tool."""
        logger.info("Starting SignalSnare")
        audio_stream = self.read_audio()
        
        chunk_size = self.sample_rate // 10  # 100ms chunks
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            try:
                while self.running:
                    chunk = audio_stream.read(chunk_size * 2)  # 16-bit samples
                    if not chunk:
                        break
                    audio_chunk = np.frombuffer(chunk, dtype=np.int16)
                    executor.submit(self.process_chunk, audio_chunk)
            except KeyboardInterrupt:
                logger.info("SignalSnare stopped by user")
                self.running = False
            finally:
                self.save_results()
                audio_stream.close()

    def save_results(self):
        """Save decoded messages to files."""
        with open(self.output_file, 'a') as f:
            f.write("=== SignalSnare Results ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for msg in self.messages:
                f.write(f"[{msg['timestamp']}] {msg['protocol']}: {msg['message']}\n")
        
        with open(self.json_file, 'w') as f:
            json.dump({
                'frequency': self.frequency,
                'sample_rate': self.sample_rate,
                'demodulators': self.demodulators,
                'messages': self.messages,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=4)
        
        logger.info(f"Results saved to {self.output_file} and {self.json_file}")

def main():
    parser = argparse.ArgumentParser(
        description="SignalSnare: Digital radio signal decoder.",
        epilog="Example: ./signalsnare.py -f 148.5565 -d POCSAG1200 -d DTMF -T 5"
    )
    parser.add_argument('-i', '--input-file', help="Input audio file (e.g., WAV)")
    parser.add_argument('-f', '--frequency', type=float, 
                       help="Frequency in MHz for SDR input (e.g., 148.5565)")
    parser.add_argument('-s', '--sample-rate', type=int, default=22050, 
                       help="Sample rate (default: 22050)")
    parser.add_argument('-d', '--demodulator', action='append', 
                       choices=['POCSAG512', 'POCSAG1200', 'POCSAG2400', 'DTMF'],
                       help="Add demodulator (can be specified multiple times)")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads (default: 5)")
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help="Quiet mode (log to file only)")

    args = parser.parse_args()

    print("""
    ==============================
         SignalSnare v1.0
      Digital Signal Decoder
    ==============================
    """)

    if not args.input_file and not args.frequency:
        logger.error("Either input file or frequency must be specified")
        sys.exit(1)

    try:
        signalsnare = SignalSnare(
            input_file=args.input_file,
            frequency=args.frequency,
            sample_rate=args.sample_rate,
            demodulators=args.demodulator,
            quiet=args.quiet,
            threads=args.threads
        )
        signalsnare.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()