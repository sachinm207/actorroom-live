#!/usr/bin/env bash
set -e

echo "🎬 Starting ActorRoom Live Server..."

# Select python / pip command
if [ -d "backend/venv" ]; then
    PYTHON_CMD="./backend/venv/bin/python3"
    PIP_CMD="./backend/venv/bin/pip"
else
    echo "Setting up Python environment..."
    if python3 -m venv backend/venv 2>/dev/null; then
        PYTHON_CMD="./backend/venv/bin/python3"
        PIP_CMD="./backend/venv/bin/pip"
    else
        PYTHON_CMD="python3"
        PIP_CMD="pip"
    fi
    $PIP_CMD install --upgrade pip || true
    $PIP_CMD install -r backend/requirements.txt
fi

export PYTHONPATH=backend
echo "Launching FastAPI WebSocket streaming server on port 8000..."
$PYTHON_CMD -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
