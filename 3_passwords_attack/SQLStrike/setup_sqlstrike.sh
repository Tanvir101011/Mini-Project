#!/bin/bash

# Install dependencies for SQLStrike
echo "Installing SQLStrike dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Python libraries
pip3 install pymysql pyodbc

# Install MSSQL ODBC driver
sudo apt install -y unixodbc unixodbc-dev
if ! dpkg -l | grep -q msodbcsql17; then
    sudo bash -c "curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -"
    sudo bash -c "curl https://packages.microsoft.com/config/ubuntu/24.04/prod.list > /etc/apt/sources.list.d/mssql-release.list"
    sudo apt update
    sudo ACCEPT_EULA=Y apt install -y msodbcsql17
fi

# Install default wordlists (optional, for convenience)
sudo mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/users.txt ]; then
    echo -e "admin\nsa\nroot" | sudo tee /usr/share/wordlists/users.txt >/dev/null
fi
if [ ! -f /usr/share/wordlists/passwords.txt ]; then
    echo -e "password\nadmin123\n" | sudo tee /usr/share/wordlists/passwords.txt >/dev/null
fi

# Verify installations
echo "Verifying installations..."
python3 -c "import pymysql" 2>/dev/null || { echo "pymysql installation failed"; exit 1; }
python3 -c "import pyodbc" 2>/dev/null || { echo "pyodbc installation failed"; exit 1; }
odbcinst -q -d | grep -q "ODBC Driver 17 for SQL Server" || { echo "MSSQL ODBC driver installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 sqlstrike.py --help' for usage."
echo "Default wordlists created at /usr/share/wordlists/users.txt and passwords.txt"