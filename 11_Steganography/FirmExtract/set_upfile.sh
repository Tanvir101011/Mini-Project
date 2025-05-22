#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Install system dependencies (libmagic, tar, xz-utils)
echo "Installing system dependencies..."
if [ -x "$(command -v apt-get)" ]; then
    sudo apt-get update
    sudo apt-get install -y libmagic-dev tar xz-utils
elif [ -x "$(command -v yum)" ]; then
    sudo yum install -y file-libs tar xz
else
    echo "Warning: Package manager not supported. Please install libmagic-dev, tar, and xz-utils manually."
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install python-magic numpy matplotlib

# Verify Python version
echo "Verifying Python version..."
python --version

# Deactivate virtual environment
deactivate

echo "Setup complete! To use FirmExtract, activate the virtual environment with:"
echo "source venv/bin/activate"
echo "Then run: python firmextract.py --help"