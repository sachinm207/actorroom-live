#!/usr/bin/env bash
set -e

echo "🎬 Starting ActorRoom Live Server..."

# Ensure virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating backend virtualenv..."
    python3 -m venv backend/venv
    ./backend/venv/bin/pip install --upgrade pip
    ./backend/venv/bin/pip install -r backend/requirements.txt
fi

export PYTHONPATH=backend
echo "Launching FastAPI WebSocket streaming server on port 8000..."
./backend/venv/bin/python3 -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
