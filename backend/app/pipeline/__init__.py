"""
ETL Pipeline package for surveillance video processing.

This package handles: Extract (video frames) → Transform (YOLO + MLP) → Load (PostgreSQL).
Uses the same database session and models as the FastAPI app.
"""
