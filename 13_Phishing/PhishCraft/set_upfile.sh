#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Install Postfix for SMTP
if ! command -v postconf &> /dev/null; then
    echo "Installing Postfix..."
    if [ -x "$(command -v apt-get)" ]; then
        sudo apt-get update
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y postfix
    else
        echo "Warning: Please install Postfix manually."
    fi
fi

# Install ngrok
if ! command -v ngrok &> /dev/null; then
    echo "Installing ngrok..."
    if [ -x "$(command -v apt-get)" ]; then
        sudo apt-get install -y snapd
        sudo snap install ngrok
    else
        echo "Warning: Please install ngrok manually from https://ngrok.com/download."
    fi
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install flask requests pyngrok

# Verify Python version
echo "Verifying Python version..."
python --version

# Deactivate virtual environment
deactivate

echo "Setup complete! To use PhishCraft, activate the virtual environment with:"
echo "source venv/bin/activate"
echo "Set your ngrok auth token with: export NGROK_AUTH_TOKEN=your_token"
echo "Ensure Postfix is running: sudo systemctl status postfix"
echo "Then run: python phishcraft.py --help"