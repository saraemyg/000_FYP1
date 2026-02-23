"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.db.init_db import init_db
from app.utils.file_handler import ensure_upload_dirs


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown."""
    # Startup
    setup_logging()
    logger.info("Starting Surveillance System API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Initialize default data
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

    # Ensure upload directories exist
    ensure_upload_dirs()

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down Surveillance System API...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-based Person Detection Surveillance System API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files for uploads
uploads_path = settings.UPLOAD_DIR
if os.path.exists(uploads_path):
    app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
