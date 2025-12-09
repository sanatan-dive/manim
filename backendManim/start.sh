#!/bin/bash

# Start the FastAPI backend server with proper reload exclusions
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Ensure dependencies are installed
pip install -q -r requirements.txt

# Start uvicorn with exclusions for generated files and media
# This prevents server reload when animation files are created
uvicorn app.main:app \
  --reload \
  --reload-exclude "generated/*" \
  --reload-exclude "media/*" \
  --reload-exclude "*.pyc" \
  --reload-exclude "__pycache__/*" \
  --host 0.0.0.0 \
  --port 8000
