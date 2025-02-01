#!/bin/bash

echo "🚀 Starting Metadata Cleaner Installation..."

# 1️⃣ Ensure the script runs with sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ Please run this script as root (using sudo)."
   exit 1
fi

# 2️⃣ Update System Packages
echo "🔄 Updating system packages..."
apt-get update

read -p "Do you want to upgrade all packages? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    apt-get upgrade
fi
# 3️⃣ Install Python and Pip (if not installed)
echo "🐍 Checking for Python & Pip..."
if ! command -v python3 &> /dev/null
then
    echo "📥 Installing Python 3..."
    apt install python3 -y
else
    echo "✅ Python 3 is already installed."
fi

if ! command -v pip3 &> /dev/null
then
    echo "📥 Installing Pip 3..."
    apt install python3-pip -y
else
    echo "✅ Pip 3 is already installed."
fi

# 4️⃣ Install System Dependencies (FFmpeg & MediaInfo)
echo "📥 Installing FFmpeg and MediaInfo..."
apt install -y ffmpeg libmediainfo0v5

# 5️⃣ Create and activate a virtual environment
echo "🐍 Creating a virtual environment..."
pip3 install --user metadata-cleaner
source venv/bin/activate

# 6️⃣ Install Metadata Cleaner using pip
echo "📥 Installing Metadata Cleaner..."
pip install metadata-cleaner

# 6️⃣ Verify Installation
echo "✅ Installation Complete!"
echo "Run 'metadata-cleaner --help' to get started."
echo "To clean metadata from a file, use: 'metadata-cleaner <file_path>'"
echo "For example: 'metadata-cleaner /path/to/your/file'"
