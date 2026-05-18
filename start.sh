#!/bin/bash

# YouTube to MP3 Converter - Start Script
# Runs both the backend and frontend with a single command

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎵 Starting YouTube to MP3 Converter..."
echo ""

# Cleanup function - kills both processes when you press Ctrl+C
cleanup() {
    echo ""
    echo "Shutting down..."
    kill "$BACKEND_PID" 2>/dev/null || true
    kill "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start the backend
echo "Starting backend (Flask API on http://localhost:8000)..."
cd "$PROJECT_DIR/api"
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Give the backend a moment to start
sleep 2

# Start the frontend
echo "Starting frontend (Next.js on http://localhost:3000)..."
cd "$PROJECT_DIR/web"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo "✓ Both servers are running!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo ""
echo "  Press Ctrl+C to stop both servers"
echo "================================================"
echo ""

# Wait for both processes
wait
