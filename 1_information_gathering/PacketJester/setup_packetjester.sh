#!/bin/bash

# Script to install dependencies for PacketJester
echo "Installing PacketJester dependencies..."

# Update package lists
sudo apt update

# Install required packages
sudo apt install -y python3 python3-pip

# Install Python libraries
pip3 install scapy netifaces

# Verify installations
echo "Verifying installations..."
python3 -c "import scapy" 2>/dev/null || { echo "scapy not installed"; exit 1; }
python3 -c "import netifaces" 2>/dev/null || { echo "netifaces not installed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 packetjester.py --help' to see usage."