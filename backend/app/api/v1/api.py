"""API v1 router configuration."""
from fastapi import APIRouter

from app.api.v1.endpoints import alerts, auth, cameras, detections, metrics, search, videos

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(detections.router, prefix="/detections", tags=["Detections"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
