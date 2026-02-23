"""Logging configuration using loguru."""
import sys
from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    # Remove default handler
    logger.remove()

    # Add console handler with formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # Add file handler for production
    if not settings.DEBUG:
        logger.add(
            "logs/app.log",
            rotation="500 MB",
            retention="10 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        )

    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")


# Export logger for use in other modules
__all__ = ["logger", "setup_logging"]
