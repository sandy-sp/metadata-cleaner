#!/bin/bash

echo "🚀 Starting Metadata Cleaner Installation..."

# 1️⃣ Ensure the script runs with sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ Please run this script as root (using sudo)."
   exit 1
fi

# 2️⃣ Update System Packages
echo "🔄 Updating system packages..."
apt update && apt upgrade -y

# 3️⃣ Install Python and Pip (if not installed)
echo "🐍 Checking for Python & Pip..."
if ! command -v python3 &> /dev/null
then
    echo "📥 Installing Python 3..."
    apt install python3 python3-pip -y
else
    echo "✅ Python 3 is already installed."
fi

# 4️⃣ Install System Dependencies (FFmpeg & MediaInfo)
echo "📥 Installing FFmpeg and MediaInfo..."
apt install -y ffmpeg libmediainfo0v5

# 5️⃣ Install Metadata Cleaner using pip
echo "📥 Installing Metadata Cleaner..."
pip3 install metadata-cleaner

# 6️⃣ Verify Installation
echo "✅ Installation Complete!"
echo "Run 'metadata-cleaner --help' to get started."
