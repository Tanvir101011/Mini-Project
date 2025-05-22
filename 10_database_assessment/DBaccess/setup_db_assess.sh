#!/bin/bash

# Install dependencies for DBAssess
echo "Installing DBAssess dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Python packages
pip3 install mysql-connector-python psycopg2-binary

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
python3 -c "import mysql.connector" 2>/dev/null || { echo "mysql-connector-python installation failed"; exit 1; }
python3 -c "import psycopg2" 2>/dev/null || { echo "psycopg2-binary installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 db_assess.py --help' for usage."
echo "Ensure databases are ones you own or have permission to assess."