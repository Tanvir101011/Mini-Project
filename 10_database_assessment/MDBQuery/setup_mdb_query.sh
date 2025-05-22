#!/bin/bash

# Install dependencies for MDBQuery
echo "Installing MDBQuery dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, MDB Tools, and ODBC
sudo apt install -y python3 python3-pip mdbtools unixodbc unixodbc-dev

# Install Python packages
pip3 install pyodbc pandas

# Configure ODBC driver for MDB Tools
echo "[MDBTools]
Description=MDB Tools ODBC Driver
Driver=/usr/lib/x86_64-linux-gnu/odbc/libmdbodbc.so
Setup=/usr/lib/x86_64-linux-gnu/odbc/libmdbodbc.so
FileUsage=1
UsageCount=1" | sudo tee /etc/odbcinst.ini

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v mdb-tables >/dev/null 2>&1 || { echo "mdbtools installation failed"; exit 1; }
python3 -c "import pyodbc" 2>/dev/null || { echo "pyodbc installation failed"; exit 1; }
python3 -c "import pandas" 2>/dev/null || { echo "pandas installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 mdb_query.py --help' for usage."
echo "Ensure MDB files are ones you own or have permission to access."