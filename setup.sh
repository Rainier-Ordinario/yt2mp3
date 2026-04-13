#!/bin/bash

# YouTube to MP3 Converter - Setup Script
# This script sets up both the frontend and backend

set -e

echo "🎵 YouTube to MP3 Converter - Setup"
echo "===================================="
echo ""

# Check for required tools
echo "Checking requirements..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it from https://nodejs.org/"
    exit 1
fi
echo "✓ Node.js $(node -v)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it."
    exit 1
fi
echo "✓ Python $(python3 --version)"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. Run: brew install ffmpeg"
    echo "   (Continue without it for now - will be checked at runtime)"
fi

echo ""
echo "Setting up Frontend (Next.js)..."
echo "================================"

cd web

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "✓ Frontend dependencies already installed"
fi

echo "✓ Frontend ready at http://localhost:3000"

echo ""
echo "Setting up Backend (Python)..."
echo "=============================="

cd ../api

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo "✓ Backend ready at http://localhost:5000"

echo ""
echo "================================"
echo "✓ Setup Complete!"
echo "================================"
echo ""
echo "To start the application, run in two separate terminals:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd api"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd web"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
