#!/bin/bash

# Install dependencies for IAXStorm
echo "Installing IAXStorm dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and required tools
sudo apt install -y python3 python3-pip

# Install Python libraries
pip3 install scapy

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "pip3 installation failed"; exit 1; }
python3 -c "import scapy" 2>/dev/null || { echo "scapy installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 iaxstorm.py --help' for usage."
echo "Ensure network access to target IAX2 server (e.g., Asterisk)."