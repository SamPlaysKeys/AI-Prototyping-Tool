#!/bin/bash

# AI Prototyping Tool - Web Application Startup Script

set -e

echo "🚀 Starting AI Prototyping Tool Web Application..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or later."
    exit 1
fi

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not running in a virtual environment."
    echo "   Consider creating one with: python -m venv venv && source venv/bin/activate"
fi

# Install dependencies if needed
if [ ! -f "requirements_installed.flag" ]; then
    echo "📦 Installing dependencies..."
    pip install -r ../requirements.txt
    touch requirements_installed.flag
else
    echo "✅ Dependencies already installed"
fi

# Set Python path
export PYTHONPATH="$(pwd)/..:$PYTHONPATH"

# Start the application
echo "🌐 Starting web server on http://localhost:8000"
echo "💡 Press Ctrl+C to stop the server"
echo ""

python app.py
