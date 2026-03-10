"""
Database Connection Manager
===========================
Creates the connection to PostgreSQL and provides session management.

Usage in other files:
    from db.database import get_db, engine
    
    # In FastAPI endpoint:
    @app.get("/alerts")
    def get_alerts(db: Session = Depends(get_db)):
        return db.query(Alert).all()
    
    # In pipeline scripts:
    with get_db_session() as db:
        db.add(detection)
        db.commit()
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings

# Create engine (connection pool to PostgreSQL)
# pool_size=5 means 5 connections kept open, max_overflow=10 means 10 more can be created if needed
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # test connections before using them (handles DB restarts)
    echo=False,          # set True to see SQL queries in console (useful for debugging)
)

# Session factory — creates new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency — yields a DB session, closes it after request.
    Use with: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for pipeline scripts — auto-commits or rolls back.
    
    Usage:
        with get_db_session() as db:
            db.add(Detection(...))
            # auto-commits on exit, rolls back on error
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Create all tables in the database.
    Run this once when setting up the system.
    """
    from db.models import Base
    Base.metadata.create_all(bind=engine)
    print("✓ All database tables created successfully.")
