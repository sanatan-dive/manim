# Manim GenAI - Phase 2 Complete! 🚀

An AI-powered animation generation system using Manim and Gemini AI, now with asynchronous processing, enhanced error handling, and security features.

## Quick Start Guide

### Backend Setup (FastAPI)

1. **Navigate to backend directory:**

   ```bash
   cd backendManim
   ```

2. **Activate virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**

   - Ensure `.env` file exists with your `GEMINI_API_KEY`
   - The key is already configured in the current .env file

5. **Start the backend server:**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or use the convenience script:

   ```bash
   ./start.sh
   ```

   The API will be available at: http://localhost:8000

### Frontend Setup (React + Vite)

1. **Navigate to frontend directory:**

   ```bash
   cd manim
   ```

2. **Install dependencies (first time only):**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   ```

   The app will be available at: http://localhost:5173

### Using the Application

1. **Access the app:**

   - Open http://localhost:5173 in your browser
   - Navigate to the "Create" page at http://localhost:5173/create

2. **Generate an animation:**
   - Enter a prompt describing the animation you want (e.g., "Create a circle that transforms into a square")
   - Submit the form
   - The system will start processing in the background
   - Status updates will appear in the chat
   - The video will appear when rendering is complete (30-60 seconds)

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Generation Endpoints

- `POST /generate` - Start animation generation job

  - Request: `{"prompt": "your animation description"}`
  - Response: `{"job_id": "uuid", "status": "pending", "message": "..."}`
  - **Note:** Returns immediately, processing happens in background

- `GET /status/{job_id}` - Check job status

  - Response includes: status, code, video_url, error_message
  - Status values: pending, generating_code, rendering, completed, failed

- `GET /jobs?limit=20` - List recent jobs

## Architecture (Phase 2)

### Backend Structure

```
backendManim/
├── app/
│   ├── main.py              # FastAPI app with background tasks
│   ├── models/
│   │   └── job.py           # Job and JobStatus models
│   ├── services/
│   │   ├── ai_service.py    # Code generation + sanitization
│   │   ├── render_service.py # Manim rendering
│   │   └── job_store.py     # In-memory job tracking
│   └── ...
├── config.py                # Pydantic Settings with validation
└── .env                     # Environment variables
```

### Key Features

**✅ Asynchronous Processing**

- Jobs processed in background using FastAPI BackgroundTasks
- API responds immediately with job ID
- Frontend polls status endpoint for updates

**✅ Enhanced Error Handling**

- Custom exception types for different failure modes
- Detailed error messages returned to frontend
- Manim stdout/stderr captured for debugging

**✅ Security**

- Code sanitization checks for dangerous patterns
- Blocks imports: os, sys, subprocess, eval, exec, etc.
- Pattern-based security scanning

**✅ Configuration Management**

- Pydantic Settings with validation
- Environment variables from .env
- Automatic directory creation
- API key validation on startup

**✅ Structured Logging**

- Timestamps and log levels
- Job-specific logging with IDs
- Error stack traces for debugging

## Development Status

### ✅ Phase 1: Walking Skeleton (Complete)

- Basic FastAPI backend
- AI code generation using Gemini
- Manim video rendering
- Frontend integration
- CORS and static file serving

### ✅ Phase 2: Refinement & Configuration (Complete)

- Pydantic Settings with validation
- Background task processing
- Job tracking system
- Status polling endpoint
- Enhanced error handling
- Security sanitization
- Service-oriented architecture

### 🔜 Phase 3: Production Architecture (Next)

- Task queue (Celery + Redis)
- Database persistence (PostgreSQL)
- Cloud storage (S3/MinIO)
- Docker containerization
- Production deployment

## Troubleshooting

**Backend won't start:**

- Check `GEMINI_API_KEY` is set in `.env`
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check logs for Pydantic validation errors

**Frontend can't connect:**

- Verify backend is running on port 8000
- Check CORS settings in config.py
- Check browser console for errors

**Job stays in "pending" status:**

- Check backend logs for background task errors
- Ensure Manim is installed: `pip install manim`
- Verify media directories exist

**Security violation error:**

- AI generated code with dangerous imports
- Try rephrasing your prompt
- Check backend logs for specific pattern detected

**Video doesn't display:**

- Check job status endpoint for error_message
- Verify video exists: `media/videos/generated_animation/720p30/`
- Ensure static file serving is working at http://localhost:8000/videos/
