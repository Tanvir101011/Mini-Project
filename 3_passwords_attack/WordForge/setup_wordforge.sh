#!/bin/bash

# Install dependencies for WordForge
echo "Installing WordForge dependencies..."

# Update package lists
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install default wordlists (optional, for testing)
sudo mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/users.txt ]; then
    echo -e "admin\nuser\nroot" | sudo tee /usr/share/wordlists/users.txt >/dev/null
fi
if [ ! -f /usr/share/wordlists/passwords.txt ]; then
    echo -e "password\nadmin123\n1234" | sudo tee /usr/share/wordlists/passwords.txt >/dev/null
fi

# Verify installations
echo "Verifying installations..."
python3 -c "import itertools" 2>/dev/null || { echo "Python itertools module missing"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 wordforge.py --help' for usage."
echo "Default wordlists created at /usr/share/wordlists/users.txt and passwords.txt"