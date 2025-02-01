#!/bin/bash

echo "🚀 Setting up the Metadata Cleaner Development Environment..."

# 1️⃣ Check if Python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# 2️⃣ Create a Virtual Environment
echo "🛠 Creating a virtual environment..."
python3 -m venv venv

# 3️⃣ Activate the Virtual Environment
echo "🔄 Activating the virtual environment..."
if [[ "$OSTYPE" == "msys" ]]; then
    venv\Scripts\activate
else
    source venv/bin/activate
echo "🔍 Checking if pip is up-to-date..."
pip list --outdated | grep -q 'pip' && pip install --upgrade pip || echo "pip is already up-to-date."
# 4️⃣ Install Dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found. Please ensure the file exists in the current directory."
    deactivate
    exit 1
fi
pip install -r requirements.txt

echo "✅ Setup Complete! Virtual environment is now ready."
echo "Run 'source venv/bin/activate' to activate the environment."
