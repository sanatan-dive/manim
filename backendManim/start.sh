#!/bin/bash
# filepath: backendManim/start_all.sh

echo "🚀 Starting Manim Animation Generator..."

# Check if Redis is running
if ! docker ps | grep -q manim_redis; then
    echo "📦 Starting Redis..."
    docker-compose up -d redis
    sleep 2
fi

echo "✅ Redis is running"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate
fi

echo "📋 Services to start:"
echo "  1. Redis (Docker) - Running ✅"
echo "  2. Celery Worker"
echo "  3. FastAPI Server"
echo ""
echo "Choose startup mode:"
echo "  [1] Start Celery Worker"
echo "  [2] Start FastAPI Server"
echo "  [3] Start Both (requires tmux)"
echo "  [4] Stop all services"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo "🔨 Starting Celery Worker..."
        # Using -P processes (prefork) causes issues with gRPC (Gemini). switching to threads or solo.
        # threads works well for I/O bound tasks (AI calls) + subprocesses (Manim).
        celery -A app.celery_app worker --loglevel=info --concurrency=4 --pool=threads
        ;;
    2)
        echo "🌐 Starting FastAPI Server..."
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
            --reload-exclude 'generated/*' --reload-exclude 'media/*'
        ;;
    3)
        if ! command -v tmux &> /dev/null; then
            echo "❌ tmux not installed. Install with: brew install tmux"
            exit 1
        fi
        
        echo "🚀 Starting both services in tmux..."
        
        # Create tmux session
        tmux new-session -d -s manim
        
        # Window 1: Celery Worker
        tmux rename-window -t manim:0 'Celery'
        tmux send-keys -t manim:0 "cd $PWD && source .venv/bin/activate && celery -A app.celery_app worker --loglevel=info --concurrency=4 --pool=threads" C-m
        
        # Window 2: FastAPI
        tmux new-window -t manim:1 -n 'FastAPI'
        tmux send-keys -t manim:1 "cd $PWD && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude 'generated/*' --reload-exclude 'media/*'" C-m
        
        echo "✅ Services started in tmux session 'manim'"
        echo "📺 To view:"
        echo "  - Attach: tmux attach -t manim"
        echo "  - Switch: Ctrl+b then window number (0 or 1)"
        echo "  - Detach: Ctrl+b then d"
        echo ""
        
        # Attach to session
        tmux attach -t manim
        ;;
    4)
        echo "🛑 Stopping services..."
        docker-compose down
        pkill -f "celery.*worker"
        pkill -f "uvicorn.*app.main"
        tmux kill-session -t manim 2>/dev/null
        echo "✅ All services stopped"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac