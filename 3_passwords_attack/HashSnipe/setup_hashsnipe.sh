#!/bin/bash

# Install dependencies for HashSnipe
echo "Installing HashSnipe dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Python libraries
pip3 install requests

# Create sample hash file for testing
sudo mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/hashes.txt ]; then
    echo -e "098f6bcd4621d373cade4e832627b4f6" | sudo tee /usr/share/wordlists/hashes.txt >/dev/null
fi

# Verify installations
echo "Verifying installations..."
python3 -c "import requests" 2>/dev/null || { echo "requests installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 hashsnipe.py --help' for usage."
echo "Sample hash file created at /usr/share/wordlists/hashes.txt"