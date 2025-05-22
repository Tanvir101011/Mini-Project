#!/bin/bash

# Install dependencies for SlowStrike
echo "Installing SlowStrike dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "pip3 installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 slowstrike.py --help' for usage."
echo "Ensure network access to target web server."