# Manim GenAI Project

## Prerequisites

- Docker & Docker Compose
- Node.js & npm
- Python 3.11+ (for local dev)

## How to Run

### 1. Start the Backend (Docker)

This runs the API, Worker, Database (PostgreSQL), and Redis containers.

```bash
cd backendManim
docker-compose up --build
```

- **API URL:** `http://localhost:8000`
- **Docs:** `http://localhost:8000/docs`

### 2. Start the Frontend (Local Development)

This runs the React application with Hot Module Replacement.

```bash
cd manim
npm install  # (Only if you haven't installed dependencies)
npm run dev
```

- **App URL:** `http://localhost:5173`

## Environment Setup

### Backend (`backendManim/.env`)

Ensure these keys are set:

```ini
GEMINI_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_aws_key  # Optional if using local storage
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket
STORAGE_MODE=s3 # or local
```

### Frontend (`manim/.env`)

Ensure these keys are set:

```ini
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key
VITE_API_URL=http://localhost:8000
```
