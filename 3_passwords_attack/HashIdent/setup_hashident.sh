#!/bin/bash

# Install dependencies for HashIDent
echo "Installing HashIDent dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Create sample hash file for testing
sudo mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/hashes.txt ]; then
    echo -e "098f6bcd4621d373cade4e832627b4f6\na94a8fe5ccb19ba61c4c0873d391e987982fbbd3" | sudo tee /usr/share/wordlists/hashes.txt >/dev/null
fi

# Verify installations
echo "Verifying installations..."
python3 -c "import re" 2>/dev/null || { echo "Python re module missing"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 hashident.py --help' for usage."
echo "Sample hash file created at /usr/share/wordlists/hashes.txt"