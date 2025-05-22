#!/bin/bash

# Install dependencies for CredSnare
echo "Installing CredSnare dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and required tools
sudo apt install -y python3 python3-pip hostapd dnsmasq aircrack-ng

# Install Python libraries
pip3 install flask dnspython

# Verify installations
echo "Verifying installations..."
command -v hostapd >/dev/null 2>&1 || { echo "hostapd installation failed"; exit 1; }
command -v dnsmasq >/dev/null 2>&1 || { echo "dnsmasq installation failed"; exit 1; }
command -v airodump-ng >/dev/null 2>&1 || { echo "aircrack-ng installation failed"; exit 1; }
python3 -c "import flask" 2>/dev/null || { echo "flask installation failed"; exit 1; }
python3 -c "import dns.resolver" 2>/dev/null || { echo "dnspython installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 credsnare.py --help' for usage."
echo "Create a phishing template (e.g., login.html) before running."
echo "Ensure wireless adapter supports monitor mode."