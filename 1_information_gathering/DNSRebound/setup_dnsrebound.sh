#!/bin/bash

# Script to install dependencies for DNSRebound
echo "Installing DNSRebound dependencies..."

# Update package lists
sudo apt update

# Install required packages
sudo apt install -y python3 python3-pip

# Install Python libraries
pip3 install dnslib aiohttp

# Verify installations
echo "Verifying installations..."
python3 -c "import dnslib" 2>/dev/null || { echo "dnslib not installed"; exit 1; }
python3 -c "import aiohttp" 2>/dev/null || { echo "aiohttp not installed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Create 'malicious.html' and run 'sudo python3 dnsrebound.py --help' to see usage."