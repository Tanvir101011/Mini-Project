#!/bin/bash

# Install dependencies for NetSentry
echo "Installing NetSentry dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and required tools
sudo apt install -y python3 python3-pip aircrack-ng

# Install Python libraries
pip3 install scapy

# Verify installations
echo "Verifying installations..."
command -v airodump-ng >/dev/null 2>&1 || { echo "aircrack-ng installation failed"; exit 1; }
python3 -c "import scapy.all" 2>/dev/null || { echo "scapy installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 netsentry.py --help' for usage."
echo "Ensure wireless adapter supports monitor mode."