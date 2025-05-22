#!/bin/bash

# Script to install dependencies for WiFiLure
echo "Installing WiFiLure dependencies..."

# Update package lists
sudo apt update

# Install required packages
sudo apt install -y python3 python3-pip hostapd dnsmasq wireless-tools iw

# Install Scapy
pip3 install scapy

# Verify installations
echo "Verifying installations..."
command -v hostapd >/dev/null 2>&1 || { echo "hostapd not installed"; exit 1; }
command -v dnsmasq >/dev/null 2>&1 || { echo "dnsmasq not installed"; exit 1; }
command -v iw >/dev/null 2>&1 || { echo "iw not installed"; exit 1; }
python3 -c "import scapy" 2>/dev/null || { echo "Scapy not installed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 wifilure.py --help' to see usage."