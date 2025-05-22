#!/bin/bash

# Install dependencies for CodeSentry
echo "Installing CodeSentry dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, Android SDK tools, OpenJDK, and smali/baksmali
sudo apt install -y python3 python3-pip android-sdk openjdk-11-jdk

# Install smali/baksmali
SMALI_VERSION="2.5.2"
SMALI_URL="https://bitbucket.org/JesusFreke/smali/downloads/smali-${SMALI_VERSION}.jar"
BAKSMALI_URL="https://bitbucket.org/JesusFreke/smali/downloads/baksmali-${SMALI_VERSION}.jar"
sudo mkdir -p /opt/smali
wget $SMALI_URL -O /opt/smali/smali.jar
wget $BAKSMALI_URL -O /opt/smali/baksmali.jar
echo '#!/bin/bash' | sudo tee /usr/local/bin/smali > /dev/null
echo 'java -jar /opt/smali/smali.jar "$@"' | sudo tee -a /usr/local/bin/smali > /dev/null
echo '#!/bin/bash' | sudo tee /usr/local/bin/baksmali > /dev/null
echo 'java -jar /opt/smali/baksmali.jar "$@"' | sudo tee -a /usr/local/bin/baksmali > /dev/null
sudo chmod +x /usr/local/bin/smali /usr/local/bin/baksmali

# Install jadx
JADX_VERSION="1.4.7"
JADX_URL="https://github.com/skylot/jadx/releases/download/v${JADX_VERSION}/jadx-${JADX_VERSION}.zip"
wget $JADX_URL -O /tmp/jadx.zip
sudo mkdir -p /opt/jadx
sudo unzip /tmp/jadx.zip -d /opt/jadx
rm /tmp/jadx.zip
sudo ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx

# Set up Android SDK tools
SDK_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip"
SDK_DIR="/opt/android-sdk"
sudo mkdir -p $SDK_DIR
wget $SDK_TOOLS_URL -O /tmp/sdk-tools.zip
sudo unzip /tmp/sdk-tools.zip -d $SDK_DIR
rm /tmp/sdk-tools.zip
yes | $SDK_DIR/cmdline-tools/bin/sdkmanager --sdk_root=$SDK_DIR "build-tools;33.0.0"
echo "export PATH=\$PATH:$SDK_DIR/build-tools/33.0.0" >> ~/.bashrc
export PATH=$PATH:$SDK_DIR/build-tools/33.0.0

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v jadx >/dev/null 2>&1 || { echo "jadx installation failed"; exit 1; }
command -v smali >/dev/null 2>&1 || { echo "smali installation failed"; exit 1; }
command -v baksmali >/dev/null 2>&1 || { echo "baksmali installation failed"; exit 1; }
command -v aapt >/dev/null 2>&1 || { echo "aapt installation failed"; exit 1; }
command -v javap >/dev/null 2>&1 || { echo "javap installation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 code_sentry.py --help' for usage."
echo "Ensure .dex, .apk, .class, or .jar files are accessible for analysis."