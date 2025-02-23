#!/bin/bash
# Install script for Metadata Cleaner using Poetry.
# This script sets up the environment and installs Metadata Cleaner using Poetry.
# It requires that Poetry is installed on the system.
echo "🚀 Starting Metadata Cleaner Installation using Poetry..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null
then
    echo "❌ Poetry is not installed. Please install Poetry first: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Update system packages (optional)
echo "🔄 Updating system packages..."
sudo apt-get update

read -p "Do you want to upgrade all packages? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get upgrade -y
fi

# Install project dependencies using Poetry
echo "📦 Installing dependencies using Poetry..."
poetry install

echo "✅ Installation Complete!"
echo "You can now run Metadata Cleaner using: poetry run metadata-cleaner --help"
