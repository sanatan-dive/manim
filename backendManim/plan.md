## Phase 1: The "Walking Skeleton" (MVP)

**Goal:** Get a video generated from a prompt and displayed on the frontend as quickly as possible.

### 1.1. Basic Backend Setup (FastAPI)

- [x] Initialize a simple FastAPI app (\`backendManim/app/main.py\`).
- [x] Create a single endpoint \`POST /generate\` that accepts a prompt.
- [x] **Mock the AI & Renderer first:** Return a hardcoded video URL or a dummy response to test the frontend connection.

### 1.2. Core Logic Implementation

- [x] Implement the "Prompt -> Code" logic using Gemini/OpenAI (hardcode API key temporarily for speed, then refactor).
- [x] Implement the "Code -> Video" logic using \`manim\` directly in the API process (blocking is fine for MVP).
- [x] Save video to a local \`static\` folder.

### 1.3. Frontend Integration

- [x] Connect the existing React frontend to the local FastAPI backend.
- [x] Display the generated video from the local static URL.
- [x] Add CORS middleware to backend for frontend access.
- [x] Configure static file serving for videos.

### 1.4. "It Works" Milestone

- [x] User types prompt -> System generates code -> System renders video -> User sees video.
- [x] _Note: It will be slow and block the server. That's okay for now._

---

## Phase 2: Refinement & Configuration (The "Senior" Touch)

**Goal:** Clean up the code, manage configuration, and stop blocking the main thread.

### 2.1. Environment Management

- [x] Introduce \`python-dotenv\`.
- [x] Move API keys, paths, and settings to \`.env\`.
- [x] Create a \`config.py\` to validate and load these settings.
- [x] Use Pydantic Settings for configuration validation.
- [x] Add directory creation on startup.

### 2.2. Asynchronous Execution (Simple)

- [x] Use FastAPI's \`BackgroundTasks\` to run the rendering so the API doesn't hang.
- [x] Implement a simple polling mechanism or status endpoint (\`GET /status/{job_id}\`) so the frontend knows when the video is ready.
- [x] Create in-memory job store for tracking job status.
- [x] Update frontend to poll status endpoint.

### 2.3. Error Handling & Logging

- [x] Add \`try/except\` blocks around the Manim rendering.
- [x] Capture Manim's stderr/stdout to debug rendering failures.
- [x] Return meaningful error messages to the frontend (e.g., "AI generated invalid code").
- [x] Create custom exception types (CodeGenerationError, RenderError, SecurityViolationError).
- [x] Enhanced logging with timestamps and log levels.

### 2.4. Basic Sanitization

- [x] Add basic checks to ensure the generated code doesn't do anything obviously dangerous (like \`os.system('rm -rf')\`).
- [x] Implement pattern-based security scanning.
- [x] Reject code with dangerous imports (os, subprocess, eval, exec, etc.).

---

## Phase 3: Production Architecture (Backend + Frontend)

**Goal:** Prepare both backend and frontend for production deployment with multiple users.

### 3.1. BACKEND: Task Queue & Infrastructure

- [x] Replace \`BackgroundTasks\` with Celery + Redis
- [x] Set up PostgreSQL database for job persistence
- [x] Implement database models (User, Job, Video)
- [ ] Add Alembic for database migrations
- [x] Configure S3/Cloudflare R2 for video storage
- [x] Update services to upload videos to cloud storage
      (to check and test , run 3 termanals
      )

### 3.2. FRONTEND: State Management & Error Handling

- [x] Implement proper state management (React Context or Zustand)
- [x] Add loading states and skeleton screens
- [x] Implement error boundaries for graceful error handling
- [x] Add retry logic for failed API calls
- [x] Show progress indicators (generating code → rendering → complete)
- [x] Add toast notifications for user feedback

### 3.3. BACKEND: Containerization

- [x] Create Dockerfile for FastAPI app
- [x] Create Dockerfile for Celery worker (with Manim dependencies)
- [x] Create docker-compose.yml (API + Worker + Redis + PostgreSQL)
- [x] Add health check endpoints
- [x] Configure environment variables for containers

### 3.4. FRONTEND: Build Optimization

- [x] Optimize bundle size (code splitting, lazy loading)
- [x] Add environment-based configuration (.env for dev/prod)
- [x] Implement proper asset optimization (images, fonts)
- [x] Add service worker for PWA (optional)
- [x] Configure production build settings

---

## Phase 4: Production Ready (Integrated Backend + Frontend)

**Goal:** Both frontend and backend production-ready with authentication, monitoring, and deployment.

### 4.1. Authentication & User Management (Full Stack)

**Backend:**

- [ ] Implement user registration endpoint
- [ ] Implement login endpoint (JWT tokens)
- [ ] Add password hashing (bcrypt)
- [ ] Create user profile endpoints
- [ ] Add rate limiting middleware
- [ ] Implement API key generation for users
- [ ] Add usage tracking and quotas

**Frontend:**

- [ ] Create login/signup pages
- [ ] Implement authentication flow (store JWT in httpOnly cookies)
- [ ] Add protected routes (redirect to login if not authenticated)
- [ ] Create user profile page
- [ ] Show usage statistics (videos generated, quota remaining)
- [ ] Add logout functionality
- [ ] Implement "forgot password" flow

### 4.2. Video Library & History (Full Stack)

**Backend:**

- [ ] Create endpoint to list user's videos
- [ ] Add video metadata (title, created_at, duration)
- [ ] Implement video deletion endpoint
- [ ] Add search/filter capabilities
- [ ] Create video sharing links (public URLs)

**Frontend:**

- [ ] Create video library/gallery page
- [ ] Add video cards with thumbnails
- [ ] Implement delete functionality with confirmation
- [ ] Add search and filter UI
- [ ] Show video details (date created, prompt used)
- [ ] Add video download button

### 4.3. Enhanced User Experience (Frontend)

- [ ] Add example prompts/templates
- [ ] Implement prompt history (recent prompts)
- [ ] Add video player with controls
- [ ] Create landing page with feature showcase
- [ ] Add pricing/plans page (if monetizing)
- [ ] Implement dark mode toggle
- [ ] Add keyboard shortcuts
- [ ] Create help/documentation page

### 4.4. Monitoring & Analytics (Full Stack)

**Backend:**

- [ ] Integrate Sentry for error tracking
- [ ] Add structured logging (JSON format)
- [ ] Implement metrics endpoint (Prometheus format)
- [ ] Set up queue monitoring
- [ ] Add performance tracking
- [ ] Create admin dashboard endpoints (user stats, job stats)

**Frontend:**

- [ ] Integrate Sentry for frontend errors
- [ ] Add Google Analytics or Plausible
- [ ] Track user interactions (button clicks, video generations)
- [ ] Implement performance monitoring (Web Vitals)
- [ ] Add user feedback widget

### 4.5. Production Safety & Performance (Full Stack)

**Backend:**

- [ ] Add request validation (Pydantic models)
- [ ] Implement job timeout limits
- [ ] Set max concurrent renders per user
- [ ] Add CORS configuration for production domains
- [ ] Implement request throttling
- [ ] Add database connection pooling
- [ ] Configure Redis connection pooling

**Frontend:**

- [ ] Add input validation on forms
- [ ] Implement debouncing for API calls
- [ ] Add offline detection and messaging
- [ ] Configure CSP headers
- [ ] Add meta tags for SEO
- [ ] Implement proper 404 and error pages

### 4.6. Deployment Infrastructure (Full Stack)

**Backend:**

- [ ] Set up nginx reverse proxy
- [ ] Configure SSL certificates (Let's Encrypt)
- [ ] Create deployment scripts
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure automatic database backups
- [ ] Set up log aggregation (CloudWatch/Papertrail)
- [ ] Deploy to production server (Railway/Render/AWS)

**Frontend:**

- [ ] Configure Vite for production builds
- [ ] Set up CDN for static assets (Cloudflare/Vercel)
- [ ] Deploy to hosting (Vercel/Netlify/Cloudflare Pages)
- [ ] Configure custom domain
- [ ] Set up preview deployments for PRs
- [ ] Add analytics and monitoring scripts

---

## V1 Production Launch Checklist

### Critical (Must Complete Before Launch)

**Backend:**

- [ ] PostgreSQL database set up with migrations
- [ ] Cloud storage (S3/R2) configured
- [ ] User authentication working
- [ ] Rate limiting active
- [ ] Error tracking (Sentry) configured
- [ ] Database backups automated
- [ ] Health checks implemented
- [ ] API documented (Swagger/OpenAPI)

**Frontend:**

- [ ] Authentication flow complete
- [ ] Video library functional
- [ ] Error handling graceful
- [ ] Loading states polished
- [ ] Mobile responsive
- [ ] SEO optimized
- [ ] Analytics tracking active

**Infrastructure:**

- [ ] HTTPS/SSL configured
- [ ] Environment variables secured
- [ ] Monitoring alerts set up
- [ ] Load testing completed (100+ concurrent users)
- [ ] Backup restore tested
- [ ] Rollback procedure documented

### Important (Launch Week)

**Backend:**

- [ ] Admin dashboard endpoints
- [ ] Job cancellation working
- [ ] Video download endpoint
- [ ] Usage analytics endpoints

**Frontend:**

- [ ] User onboarding flow
- [ ] Help documentation
- [ ] Video sharing functionality
- [ ] Dark mode (if time permits)

**DevOps:**

- [ ] CI/CD pipeline running
- [ ] Automated testing in pipeline
- [ ] Blue-green deployment setup
- [ ] Monitoring dashboards configured

### Nice to Have (V1.1 - Post Launch)

- [ ] Example gallery/showcase
- [ ] Video thumbnails generation
- [ ] Batch processing
- [ ] Advanced prompt editor
- [ ] Webhook notifications
- [ ] API versioning
- [ ] Payment integration (if monetizing)
- [ ] Social sharing features
- [ ] Collaborative features

---

## Production Architecture (Full Stack)

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    CDN (Cloudflare)                          │
│              Static Assets + Video Delivery                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + Vite)                     │
│              Hosted on Vercel/Netlify                        │
│          - Authentication UI                                 │
│          - Video Library                                     │
│          - Generation Interface                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│            Load Balancer / nginx (SSL/TLS)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (2-3 instances)                 │
│          - User Authentication (JWT)                         │
│          - Job Management                                    │
│          - Rate Limiting                                     │
│          - API Endpoints                                     │
└─────────────────────────────────────────────────────────────┘
              ↓                       ↓                ↓
    ┌─────────────┐      ┌─────────────────┐   ┌─────────────┐
    │   Redis     │←────→│ Celery Workers  │   │ PostgreSQL  │
    │  (Broker)   │      │   (3-5 nodes)   │   │  Database   │
    │             │      │  - AI Service   │   │  - Users    │
    │             │      │  - Manim Render │   │  - Jobs     │
    └─────────────┘      └─────────────────┘   │  - Videos   │
                                   ↓            └─────────────┘
                         ┌─────────────────┐
                         │   S3/R2 Storage │
                         │  - Video Files  │
                         │  - Thumbnails   │
                         └─────────────────┘
                                   ↓
                         ┌─────────────────┐
                         │   CDN (Videos)  │
                         │  Fast Delivery  │
                         └─────────────────┘
```

### Monitoring & Logging Layer

```
┌─────────────────────────────────────────────────────────────┐
│  Sentry (Error Tracking)  │  Prometheus (Metrics)           │
│  CloudWatch (Logs)         │  Uptime Robot (Monitoring)     │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Strategy

### Development Environment

- **Frontend:** `npm run dev` (localhost:5173)
- **Backend:** `uvicorn app.main:app --reload` (localhost:8000)
- **Worker:** `celery -A app.celery_app worker`
- **Redis:** Docker container
- **Database:** SQLite or local PostgreSQL

### Staging Environment

- **Frontend:** Vercel preview deployment
- **Backend:** Railway/Render staging instance
- **Database:** Separate staging PostgreSQL
- **Storage:** Separate S3 bucket

### Production Environment

- **Frontend:** Vercel production (auto-deploy from main branch)
- **Backend:** Railway/Render production (manual or auto-deploy)
- **Database:** Managed PostgreSQL (Railway/Render/AWS RDS)
- **Storage:** Production S3/R2 bucket
- **CDN:** Cloudflare

---

## Tech Stack Summary

### Frontend

- **Framework:** React 19
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State:** React Context / Zustand
- **Routing:** React Router
- **Auth:** Clerk / Custom JWT
- **Hosting:** Vercel / Netlify

### Backend

- **Framework:** FastAPI
- **Task Queue:** Celery + Redis
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Auth:** JWT (python-jose)
- **Storage:** AWS S3 / Cloudflare R2
- **Hosting:** Railway / Render / AWS

### DevOps

- **Containers:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry + Prometheus
- **Logging:** Structured JSON logs
- **Reverse Proxy:** nginx
- **SSL:** Let's Encrypt

---

## Current Status: Phase 2 Complete! ✅

**Architecture Improvements:**

- ✅ Pydantic Settings with validation
- ✅ Background task processing with FastAPI BackgroundTasks
- ✅ Job tracking system (in-memory)
- ✅ Status polling endpoint
- ✅ Enhanced error handling with custom exceptions
- ✅ Security scanning for dangerous code patterns
- ✅ Structured logging
- ✅ Service-oriented architecture (AI service, Render service, Job store)

**Next Steps: Ready for Phase 3 (Production Architecture)**
