#!/bin/bash

# TerraCost VSCode Extension Installation Script

echo "🏗️  Installing TerraCost VSCode Extension..."
echo "================================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) and npm $(npm -v) are installed"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Compile the extension
echo "🔨 Compiling the extension..."
npm run compile

if [ $? -ne 0 ]; then
    echo "❌ Failed to compile the extension"
    exit 1
fi

echo "✅ Extension compiled successfully!"

# Check if TerraCost Python package is available
echo "🐍 Checking TerraCost Python package..."
if python -c "import terracost" 2>/dev/null; then
    echo "✅ TerraCost Python package is available"
elif python3 -c "import terracost" 2>/dev/null; then
    echo "✅ TerraCost Python package is available (python3)"
else
    echo "⚠️  TerraCost Python package not found"
    echo "   Please install it first:"
    echo "   cd /path/to/terracost"
    echo "   pip install -e ."
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "To use the extension:"
echo "1. Press F5 in VSCode to run in development mode"
echo "2. Or package it: npm run vscode:prepublish"
echo "3. Install the generated .vsix file"
echo ""
echo "For more information, see README.md"
