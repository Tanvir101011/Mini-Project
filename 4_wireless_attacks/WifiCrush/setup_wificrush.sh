#!/bin/bash

# Install dependencies for WiFiCrush
echo "Installing WiFiCrush dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and aircrack-ng
sudo apt install -y python3 python3-pip aircrack-ng

# Install Python libraries
pip3 install scapy

# Install default wordlist (optional, for convenience)
sudo mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/passwords.txt ]; then
    echo -e "password\nmysecretpass\n12345678" | sudo tee /usr/share/wordlists/passwords.txt >/dev/null
fi

# Verify installations
echo "Verifying installations..."
command -v airodump-ng >/dev/null 2>&1 || { echo "aircrack-ng installation failed"; exit 1; }
python3 -c "import scapy.all" 2>/dev/null || { echo "scapy installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 wificrush.py --help' for usage."
echo "Default wordlist created at /usr/share/wordlists/passwords.txt"
echo "Ensure wireless adapter supports monitor mode."