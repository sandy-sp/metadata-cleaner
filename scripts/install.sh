#!/bin/bash

# Metadata Cleaner Installation Script

echo "🚀 Starting Metadata Cleaner Installation..."

# Check for required system dependencies
echo "🔍 Checking for required system packages..."

MISSING_DEPENDENCIES=()

dependencies=("ffmpeg" "exiftool" "python3" "python3-pip")

# Check if each dependency is installed
for dep in "${dependencies[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
        MISSING_DEPENDENCIES+=("$dep")
    fi
done

# Install missing dependencies if confirmed by user
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
else
    echo "✅ All system dependencies are installed."
fi

# Install Python dependencies
echo "📦 Installing dependencies using Poetry..."
if command -v poetry &> /dev/null; then
    poetry install
else
    echo "⚠️ Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    poetry install
fi

echo "✅ Installation Complete!"
echo "Run 'poetry run metadata-cleaner --help' to verify the installation."
