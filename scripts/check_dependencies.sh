#!/bin/bash
echo "🔍 Running security checks on dependencies..."

# Check for outdated dependencies
poetry show --outdated || echo "⚠️ Poetry dependencies could not be checked."

# Check if pip-audit is installed
if command -v pip-audit &> /dev/null; then
    echo "🚀 Checking dependencies for vulnerabilities..."
    pip-audit
else
    echo "⚠️ pip-audit not found. Install it using: pip install pip-audit"
fi

# Check if safety is installed
if command -v safety &> /dev/null; then
    echo "⚠️ Running safety security check..."
    if safety --help | grep -q "scan"; then
        safety scan
    else
        safety check
    fi
else
    echo "⚠️ safety not found. Install it using: pip install safety"
fi

echo "✅ Dependency audit complete!"
