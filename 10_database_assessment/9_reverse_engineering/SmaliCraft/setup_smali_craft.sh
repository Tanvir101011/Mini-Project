#!/bin/bash

# Install dependencies for SmaliCraft
echo "Installing SmaliCraft dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and Java (required for smali/baksmali)
sudo apt install -y python3 python3-pip openjdk-11-jdk

# Install smali/baksmali
SMALI_VERSION="2.5.2"
SMALI_URL="https://bitbucket.org/JesusFreke/smali/downloads/smali-${SMALI_VERSION}.jar"
BAKSMALI_URL="https://bitbucket.org/JesusFreke/smali/downloads/baksmali-${SMALI_VERSION}.jar"
sudo mkdir -p /opt/smali
wget $SMALI_URL -O /opt/smali/smali.jar
wget $BAKSMALI_URL -O /opt/smali/baksmali.jar

# Create wrapper scripts for smali and baksmali
echo '#!/bin/bash' | sudo tee /usr/local/bin/smali > /dev/null
echo 'java -jar /opt/smali/smali.jar "$@"' | sudo tee -a /usr/local/bin/smali > /dev/null
echo '#!/bin/bash' | sudo tee /usr/local/bin/baksmali > /dev/null
echo 'java -jar /opt/smali/baksmali.jar "$@"' | sudo tee -a /usr/local/bin/baksmali > /dev/null
sudo chmod +x /usr/local/bin/smali /usr/local/bin/baksmali

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v smali >/dev/null 2>&1 || { echo "smali installation failed"; exit 1; }
command -v baksmali >/dev/null 2>&1 || { echo "baksmali installation failed"; exit 1; }
command -v java >/dev/null 2>&1 || { echo "Java installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 smali_craft.py --help' for usage."
echo "Ensure .dex or .apk files are accessible for processing."