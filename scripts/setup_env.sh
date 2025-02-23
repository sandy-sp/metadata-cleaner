#!/bin/bash
# Setup script for Metadata Cleaner Development Environment using Poetry.
# This script checks for Poetry, installs dependencies, and optionally activates the virtual environment.

echo "🚀 Setting up the Metadata Cleaner Development Environment using Poetry..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Install project dependencies using Poetry
echo "📥 Installing dependencies via Poetry..."
poetry install

# Optionally, activate the Poetry virtual environment
read -p "Do you want to activate the virtual environment now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Activating Poetry shell..."
    poetry shell
else
    echo "✅ Setup Complete! You can activate the environment later using 'poetry shell'."
fi
