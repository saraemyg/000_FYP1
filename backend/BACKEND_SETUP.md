# Backend Setup Guide

This guide will help you set up and test the backend on localhost:8000.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose v2+
- Git

## Quick Start (Docker - Recommended)

### Step 1: Navigate to project directory
```powershell
cd C:\Users\SARA\OneDrive\Desktop\00_FYP1\surveillance-saraem
```

### Step 2: Build and run ONLY the backend services
```powershell
docker compose up --build db redis backend
```

This starts only:
- **PostgreSQL database** (port 5432)
- **Redis cache** (port 6379)
- **FastAPI backend** (port 8000)

### Step 3: Verify backend is running
Open your browser and visit:
- **API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/v1/health (if available)

## Testing the Backend API

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. You'll see all available API endpoints
3. Click on any endpoint to expand it
4. Click "Try it out" to test the endpoint

### Using curl (PowerShell)
```powershell
# Test root endpoint
curl http://localhost:8000/

# Test API health
curl http://localhost:8000/api/v1/cameras

# Test with headers
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/cameras" -Method Get
```

## Stopping the Backend

```powershell
# Stop all services
docker compose down

# Stop and remove volumes (clears database)
docker compose down -v
```

## Troubleshooting

### Issue: Port 8000 already in use
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue: Database connection errors
Wait for PostgreSQL to be healthy before the backend connects:
```powershell
# Check container health
docker compose ps
```

### Issue: Need to rebuild after code changes
```powershell
docker compose up --build db redis backend
```

### Issue: View backend logs
```powershell
# View all logs
docker compose logs backend

# Follow logs in real-time
docker compose logs -f backend
```

## Local Development (Without Docker)

If you prefer running the backend directly:

### Step 1: Activate conda environment
```powershell
conda activate saraem
```

### Step 2: Navigate to backend directory
```powershell
cd backend
```

### Step 3: Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Set environment variables
```powershell
$env:DATABASE_URL="postgresql://surveillance_user:secure_password@localhost:5432/surveillance_db"
$env:REDIS_URL="redis://localhost:6379/0"
$env:SECRET_KEY="your-super-secret-jwt-key"
$env:DEBUG="true"
```

### Step 5: Start PostgreSQL and Redis via Docker
```powershell
cd ..
docker compose up -d db redis
```

### Step 6: Run the backend
```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | Swagger UI documentation |
| `/redoc` | GET | ReDoc documentation |
| `/api/v1/auth/*` | POST | Authentication endpoints |
| `/api/v1/cameras` | GET/POST | Camera management |
| `/api/v1/videos` | GET/POST | Video upload/management |
| `/api/v1/detections` | GET | Person detections |
| `/api/v1/search` | POST | Natural language search |
| `/api/v1/metrics` | GET | System metrics |

## Expected Output

When backend is running successfully, you should see:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Next Steps

Once backend is running on http://localhost:8000:
1. Test the API via Swagger UI at http://localhost:8000/docs
2. Create a test user via the auth endpoints
3. Upload a test video to verify the video processing pipeline
