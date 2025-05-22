#!/bin/bash

# Install dependencies for Dex2Java
echo "Installing Dex2Java dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and JDK
sudo apt install -y python3 python3-pip openjdk-11-jdk

# Install dex2jar
DEX2JAR_VERSION="2.0"
DEX2JAR_URL="https://github.com/pxb1988/dex2jar/releases/download/2.0/dex2jar-2.0.zip"
wget $DEX2JAR_URL -O /tmp/dex2jar.zip
sudo mkdir -p /opt/dex2jar
sudo unzip /tmp/dex2jar.zip -d /opt/dex2jar
rm /tmp/dex2jar.zip
sudo chmod +x /opt/dex2jar/dex2jar-2.0/*.sh
sudo ln -sf /opt/dex2jar/dex2jar-2.0/d2j-dex2jar.sh /usr/local/bin/d2j-dex2jar

# Add JDK to PATH
echo "export PATH=\$PATH:/usr/lib/jvm/java-11-openjdk-amd64/bin" >> ~/.bashrc
export PATH=$PATH:/usr/lib/jvm/java-11-openjdk-amd64/bin

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v d2j-dex2jar >/dev/null 2>&1 || { echo "dex2jar installation failed"; exit 1; }
command -v jar >/dev/null 2>&1 || { echo "JDK (jar) installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 dex2java.py --help' for usage."
echo "Ensure .dex or .apk files are accessible for conversion."