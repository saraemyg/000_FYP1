# AI-Based Person Detection Surveillance System

A full-stack AI surveillance system prototype for attribute-based person search with path segmentation optimization. This is an FYP1 academic project demonstrating core technical feasibility.

## Features

- **Authentication System**: JWT-based authentication with role-based access control (admin, security_personnel)
- **Video Processing**: Upload and process surveillance videos with person detection
- **Attribute Recognition**: Extract clothing colors and gender from detected persons (STUB implementation)
- **Natural Language Search**: Search for people using natural language queries (e.g., "male wearing red shirt")
- **Advanced Filtering**: Filter detections by gender, upper/lower body colors, and confidence threshold
- **Performance Dashboard**: Real-time metrics and statistics visualization
- **Camera Management**: Configure and manage surveillance cameras (admin only)

## Tech Stack

### Frontend
- React.js 18+ with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- shadcn/ui component library
- React Query for state management
- Axios for API calls
- Recharts for data visualization

### Backend
- FastAPI (Python 3.10+)
- Pydantic for data validation
- SQLAlchemy ORM
- Alembic for migrations
- JWT authentication
- OpenCV for video processing

### Database
- PostgreSQL 15+
- Redis for caching (optional)

### DevOps
- Docker & Docker Compose
- Structured logging (loguru)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed and running
- PowerShell or Bash terminal
- (Optional) Node.js 18+ for frontend local development
- (Optional) Python 3.10+ for backend local development

### Using Docker Compose (Recommended) ⭐

#### Step 1: Start Backend Services
Navigate to the project root and start the database, Redis, and backend:

```powershell
cd C:\Users\SARA\OneDrive\Desktop\00_FYP1\surveillance-saraem

# Start backend services (db, redis, backend API)
docker compose up db redis backend
```

**Wait for this message to appear:**
```
backend-1  | INFO:     Application startup complete.
```

#### Step 2: Test Backend API (Optional but Recommended)

Open a **new PowerShell terminal** and run:

```powershell
# Login to get JWT token
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'

# Display the token
$response

# Save token for testing
$token = $response.access_token

# Test authenticated endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Method Get `
  -Headers @{"Authorization"="Bearer $token"}
```

Or visit in browser:
- **Swagger API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health
- **API Root**: http://localhost:8000/

#### Step 3: Start Frontend (New Terminal)

```powershell
cd C:\Users\SARA\OneDrive\Desktop\00_FYP1\surveillance-saraem\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

#### Step 4: Login to Frontend

Use these credentials:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Security | security | security123 |

### Default Credentials

All default users are automatically created on first database initialization:

| Role | Username | Email | Password |
|------|----------|-------|----------|
| Admin | admin | admin@surveillance.dev | admin123 |
| Security Personnel | security | security@surveillance.dev | security123 |

## Local Development

### Backend Setup (Without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Windows PowerShell:
$env:DATABASE_URL = "postgresql://surveillance_user:secure_password@localhost:5432/surveillance_db"
$env:REDIS_URL = "redis://localhost:6379/0"

# Or Linux/Mac:
export DATABASE_URL=postgresql://surveillance_user:secure_password@localhost:5432/surveillance_db
export REDIS_URL=redis://localhost:6379/0

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

**Note:** You'll need PostgreSQL and Redis running locally. Use Docker Compose for those:
```powershell
docker compose up -d db redis
```

### Frontend Setup (Without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

The frontend will automatically proxy API calls to http://localhost:8000/api/v1

## Project Structure

```
surveillance-system/
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API service functions
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration and security
│   │   ├── db/            # Database setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic (STUB implementations)
│   │   └── utils/         # Utility functions
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - Register new user (admin only)
- `GET /api/v1/auth/me` - Get current user info

### Videos
- `POST /api/v1/videos/upload` - Upload video file
- `POST /api/v1/videos/{video_id}/process` - Start processing
- `GET /api/v1/videos/{video_id}/status` - Get processing status
- `GET /api/v1/videos` - List all videos
- `DELETE /api/v1/videos/{video_id}` - Delete video

### Search
- `POST /api/v1/search/query` - Natural language search
- `POST /api/v1/search/advanced` - Structured attribute search
- `GET /api/v1/search/history` - Get search history

### Metrics
- `GET /api/v1/metrics/summary` - System statistics
- `GET /api/v1/metrics/videos` - Per-video metrics
- `GET /api/v1/metrics/attributes` - Attribute distribution

### Cameras
- `GET /api/v1/cameras` - List cameras
- `POST /api/v1/cameras` - Create camera (admin)
- `PUT /api/v1/cameras/{id}` - Update camera (admin)
- `DELETE /api/v1/cameras/{id}` - Delete camera (admin)

## Natural Language Search Examples

The NLP parser supports queries like:
- "male wearing red shirt"
- "female with blue pants"
- "person with black top and white bottom"
- "man in green jacket"

## STUB Implementations

This prototype uses STUB implementations for ML components:

- **DetectorService**: Generates mock person detections with random bounding boxes
- **AttributeClassifier**: Returns random attributes (color, gender) with realistic confidence scores
- **SegmentationService**: Creates simple rectangular masks for walkable regions

These stubs are designed to be replaced with actual models in FYP2:
- YOLOv11 for person detection
- ResNet-50 for attribute classification
- DeepLabv3+ for semantic segmentation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://... |
| REDIS_URL | Redis connection string | redis://redis:6379/0 |
| SECRET_KEY | JWT signing key | your-secret-key |
| UPLOAD_DIR | Video upload directory | /app/uploads |
| MAX_UPLOAD_SIZE_MB | Maximum upload size | 500 |
| DETECTION_CONFIDENCE_THRESHOLD | Minimum detection confidence | 0.6 |

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Development Workflow

1. Create a feature branch
2. Make changes
3. Run tests
4. Submit pull request

## Restart & Troubleshooting

### Restart Backend Services

**Full restart (clears database):**
```powershell
docker compose down -v
docker compose up --build db redis backend
```

**Quick restart (keeps database):**
```powershell
docker compose down
docker compose up db redis backend
```

**Rebuild after code changes:**
```powershell
docker compose up --build db redis backend
```

### View Backend Logs

```powershell
# Last 50 lines
docker compose logs backend -n 50

# Follow logs in real-time
docker compose logs -f backend
```

### Common Issues

**Issue: Port 8000 already in use**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Issue: Database connection errors**
- Wait 10-15 seconds for PostgreSQL to fully initialize
- Check: `docker compose ps` to see if db container is healthy
- If unhealthy, run: `docker compose down -v && docker compose up db redis backend`

**Issue: Frontend can't reach backend**
- Ensure backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/app/core/config.py`
- Restart frontend: `npm run dev`

**Issue: 401 Unauthorized errors**
- Ensure you're sending the Authorization header with the Bearer token
- Token may be expired - re-login to get a new token
- Check token format: `Authorization: Bearer <token>`

### Stopping Services

```powershell
# Stop all services
docker compose down

# Stop and remove volumes (clears database data)
docker compose down -v

# Stop only specific services
docker compose stop backend
docker compose stop db redis
```

## Acknowledgments

This project is developed as part of FYP1 (Final Year Project Phase 1) to demonstrate full-stack development capabilities and understanding of AI/ML pipeline architecture.

## License

MIT License - See LICENSE file for details
