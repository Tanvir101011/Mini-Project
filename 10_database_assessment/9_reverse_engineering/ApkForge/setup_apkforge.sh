#!/bin/bash

# Install dependencies for APKForge
echo "Installing APKForge dependencies..."

# Update package lists
sudo apt update

# Install Python, pip, and Android SDK tools
sudo apt install -y python3 python3-pip android-sdk openjdk-11-jdk

# Set up Android SDK tools
SDK_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip"
SDK_DIR="/opt/android-sdk"
sudo mkdir -p $SDK_DIR
wget $SDK_TOOLS_URL -O /tmp/sdk-tools.zip
sudo unzip /tmp/sdk-tools.zip -d $SDK_DIR
rm /tmp/sdk-tools.zip

# Install required SDK packages
yes | $SDK_DIR/cmdline-tools/bin/sdkmanager --sdk_root=$SDK_DIR "build-tools;33.0.0"

# Add tools to PATH
echo "export PATH=\$PATH:$SDK_DIR/build-tools/33.0.0" >> ~/.bashrc
export PATH=$PATH:$SDK_DIR/build-tools/33.0.0

# Generate debug keystore if not exists
if [ ! -f /tmp/debug.keystore ]; then
    keytool -genkey -v -keystore /tmp/debug.keystore -storepass android \
        -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 \
        -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
fi

# Verify installations
echo "Verifying installations..."
command -v python3 >/dev/null 2>&1 || { echo "python3 installation failed"; exit 1; }
command -v aapt >/dev/null 2>&1 || { echo "aapt installation failed"; exit 1; }
command -v zipalign >/dev/null 2>&1 || { echo "zipalign installation failed"; exit 1; }
command -v apksigner >/dev/null 2>&1 || { echo "apksigner installation failed"; exit 1; }
[ -f /tmp/debug.keystore ] || { echo "Debug keystore generation failed"; exit 1; }

echo "Dependencies installed successfully!"
echo "Run 'python3 apkforge.py --help' for usage."
echo "Ensure APK files are accessible and Android emulator/device is available for testing."