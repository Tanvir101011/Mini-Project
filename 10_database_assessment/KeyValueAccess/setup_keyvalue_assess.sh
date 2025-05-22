#!/bin/bash

# Install dependencies for KeyValueAssess
echo "Installing KeyValueAssess dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and libmemcached-dev
sudo apt install -y python3 python3-pip libmemcached-dev

# Install Python packages
pip3 install redis pylibmc etcd3

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
python3 -c "import redis" 2>/dev/null || { echo "redis installation failed"; exit 1; }
python3 -c "import pylibmc" 2>/dev/null || { echo "pylibmc installation failed"; exit 1; }
python3 -c "import etcd3" 2>/dev/null || { echo "etcd3 installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 keyvalue_assess.py --help' for usage."
echo "Ensure databases are ones you own or have permission to assess."