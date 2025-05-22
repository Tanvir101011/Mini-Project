#!/bin/bash

# Install dependencies for NetBrute
echo "Installing NetBrute dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, Nmap, and Medusa
sudo apt install -y python3 python3-pip nmap medusa

# Install default wordlists (optional, for convenience)
sudo mkdir -p /usr/share/wordlists
if [ ! -f /usr/share/wordlists/users.txt ]; then
    echo -e "admin\nroot\nuser" | sudo tee /usr/share/wordlists/users.txt >/dev/null
fi
if [ ! -f /usr/share/wordlists/passwords.txt ]; then
    echo -e "cisco\npassword\nadmin123" | sudo tee /usr/share/wordlists/passwords.txt >/dev/null
fi

# Verify installations
echo "Verifying installations..."
command -v nmap >/dev/null 2>&1 || { echo "nmap installation failed"; exit 1; }
command -v medusa >/dev/null 2>&1 || { echo "medusa installation failed"; exit 1; }
python3 -c "import xml.etree.ElementTree" 2>/dev/null || { echo "Python XML module missing"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 netbrute.py --help' for usage."
echo "Default wordlists created at /usr/share/wordlists/users.txt and passwords.txt"