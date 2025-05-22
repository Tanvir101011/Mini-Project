#!/bin/bash

# Install dependencies for NoSQLAssess
echo "Installing NoSQLAssess dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Python packages
pip3 install pymongo redis cassandra-driver

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
python3 -c "import pymongo" 2>/dev/null || { echo "pymongo installation failed"; exit 1; }
python3 -c "import redis" 2>/dev/null || { echo "redis installation failed"; exit 1; }
python3 -c "import cassandra.cluster" 2>/dev/null || { echo "cassandra-driver installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 nosql_assess.py --help' for usage."
echo "Ensure databases are ones you own or have permission to assess."