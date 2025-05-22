#!/bin/bash

# Install dependencies for SignalSnare
echo "Installing SignalSnare dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and required tools
sudo apt install -y python3 python3-pip rtl-sdr sox libpulse-dev

# Install Python libraries
pip3 install numpy scipy sounddevice

# Verify installations
echo "Verifying installations..."
command -v rtl_fm >/dev/null 2>&1 || { echo "rtl-sdr installation failed"; exit 1; }
command -v sox >/dev/null 2>&1 || { echo "sox installation failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || { echo "numpy installation failed"; exit 1; }
python3 -c "import scipy" 2>/dev/null || { echo "scipy installation failed"; exit 1; }
python3 -c "import sounddevice" 2>/dev/null || { echo "sounddevice installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 signalsnare.py --help' for usage."
echo "Ensure RTL-SDR is connected for real-time input or prepare WAV files."