#!/bin/bash

# Install dependencies for SQLBlaze
echo "Installing SQLBlaze dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Python packages
pip3 install requests python-cookiejar

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
python3 -c "import requests" 2>/dev/null || { echo "requests installation failed"; exit 1; }
python3 -c "import http.cookiejar" 2>/dev/null || { echo "python-cookiejar installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 sql_blaze.py --help' for usage."
echo "Ensure target URLs are systems you own or have permission to test."