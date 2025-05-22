#!/bin/bash

# Install dependencies for PassCrack
echo "Installing PassCrack dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Create sample wordlist and hash file for testing
sudo mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/wordlist.txt ]; then
    echo -e "test\npassword\nadmin" | sudo tee /usr/share/wordlists/wordlist.txt >/dev/null
fi
if [ ! -f /usr/share/wordlists/hashes.txt ]; then
    echo -e "098f6bcd4621d373cade4e832627b4f6" | sudo tee /usr/share/wordlists/hashes.txt >/dev/null
fi

# Verify installations
echo "Verifying installations..."
python3 -c "import hashlib" 2>/dev/null || { echo "Python hashlib module missing"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 passcrack.py --help' for usage."
echo "Sample wordlist and hash file created at /usr/share/wordlists/"