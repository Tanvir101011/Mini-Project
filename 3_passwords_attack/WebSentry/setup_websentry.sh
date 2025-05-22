#!/bin/bash

# Install dependencies for WebSentry
echo "Installing WebSentry dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Python libraries
pip3 install requests beautifulsoup4 lxml

# Verify installations
echo "Verifying installations..."
python3 -c "import requests" 2>/dev/null || { echo "requests installation failed"; exit 1; }
python3 -c "import bs4" 2>/dev/null || { echo "beautifulsoup4 installation failed"; exit 1; }
python3 -c "import lxml" 2>/dev/null || { echo "lxml installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 websentry.py --help' for usage."
echo "Configure browser proxy to 127.0.0.1:8008 (default)."