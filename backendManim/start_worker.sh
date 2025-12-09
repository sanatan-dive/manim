#!/bin/bash

# Start Celery worker for Manim animation generation
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found at .venv"
    exit 1
fi

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.celery_app worker --loglevel=info --concurrency=2
