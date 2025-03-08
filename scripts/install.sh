#!/bin/bash
echo "🚀 Starting Metadata Cleaner Installation..."

# Check for required system dependencies
echo "🔍 Checking for required system packages..."

MISSING_DEPENDENCIES=()

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    MISSING_DEPENDENCIES+=("ffmpeg")
fi

# Check for ExifTool
if ! command -v exiftool &> /dev/null; then
    MISSING_DEPENDENCIES+=("exiftool")
fi

# Install missing dependencies
if [ ${#MISSING_DEPENDENCIES[@]} -gt 0 ]; then
    echo "❌ Missing system dependencies: ${MISSING_DEPENDENCIES[*]}"
    read -p "Do you want to install them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt update
        sudo apt install -y "${MISSING_DEPENDENCIES[@]}"
    else
        echo "⚠️ Installation aborted. Required dependencies are missing."
        exit 1
    fi
fi

# Install Python dependencies with Poetry
echo "📦 Installing dependencies using Poetry..."
poetry install

echo "✅ Installation Complete!"
echo "Run 'poetry run metadata-cleaner --help' to verify the installation."
