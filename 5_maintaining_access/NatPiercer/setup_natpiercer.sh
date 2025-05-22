#!/bin/bash

# Install dependencies for NatPiercer
echo "Installing NatPiercer dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "pip3 installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'sudo python3 natpiercer.py --help' for usage."
echo "Ensure network has basic NAT (RFC 1631) for compatibility."