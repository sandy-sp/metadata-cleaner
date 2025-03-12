#!/bin/bash

# Dependency Check Script for Metadata Cleaner
# Ensures required system dependencies are installed before running the application.

echo "🔍 Checking for required dependencies..."

# List of required dependencies
dependencies=("ffmpeg" "exiftool" "pip-audit" "safety")

# Track missing dependencies
missing=()

# Check for each dependency
for dep in "${dependencies[@]}"; do
    if ! command -v "$dep" &> /dev/null; then
        missing+=("$dep")
    fi
done

# Handle missing dependencies
if [ ${#missing[@]} -gt 0 ]; then
    echo "❌ The following dependencies are missing: ${missing[*]}"
    read -p "Would you like to install them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing missing dependencies..."
        sudo apt update
        sudo apt install -y "${missing[@]}"
        echo "✅ Dependencies installed successfully!"
    else
        echo "⚠️ Installation aborted. Required dependencies are missing."
        exit 1
    fi
else
    echo "✅ All dependencies are installed."
fi

# Check security vulnerabilities
echo "🔍 Running security checks on dependencies..."
if command -v pip-audit &> /dev/null; then
    echo "🚀 Checking dependencies for vulnerabilities..."
    pip-audit
else
    echo "⚠️ pip-audit not found. Install it using: pip install pip-audit"
fi

if command -v safety &> /dev/null; then
    echo "⚠️ Running safety security check..."
    safety check || safety scan
else
    echo "⚠️ safety not found. Install it using: pip install safety"
fi

echo "✅ Dependency audit complete!"
