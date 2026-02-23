"""File handling utilities."""
import os
import shutil
from typing import BinaryIO
import uuid

import aiofiles
from fastapi import UploadFile
from loguru import logger

from app.core.config import settings


ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension."""
    return os.path.splitext(filename)[1].lower()


def is_valid_video(filename: str) -> bool:
    """Check if file is a valid video format."""
    return get_file_extension(filename) in ALLOWED_VIDEO_EXTENSIONS


def is_valid_image(filename: str) -> bool:
    """Check if file is a valid image format."""
    return get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension."""
    ext = get_file_extension(original_filename)
    unique_id = uuid.uuid4().hex[:12]
    base_name = os.path.splitext(original_filename)[0]
    # Sanitize base name
    safe_base = "".join(c for c in base_name if c.isalnum() or c in "-_")[:50]
    return f"{safe_base}_{unique_id}{ext}"


async def save_upload_file(
    upload_file: UploadFile,
    destination_dir: str,
    filename: str | None = None,
) -> str:
    """
    Save an uploaded file to the destination directory.

    Args:
        upload_file: FastAPI UploadFile object
        destination_dir: Directory to save the file
        filename: Optional custom filename

    Returns:
        Full path to saved file
    """
    os.makedirs(destination_dir, exist_ok=True)

    if filename is None:
        filename = generate_unique_filename(upload_file.filename or "upload")

    file_path = os.path.join(destination_dir, filename)

    async with aiofiles.open(file_path, "wb") as buffer:
        while chunk := await upload_file.read(1024 * 1024):  # 1MB chunks
            await buffer.write(chunk)

    logger.info(f"Saved uploaded file to {file_path}")
    return file_path


def delete_file(file_path: str) -> bool:
    """
    Delete a file from the filesystem.

    Args:
        file_path: Path to the file to delete

    Returns:
        True if deleted, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False


def delete_directory(dir_path: str) -> bool:
    """
    Delete a directory and all its contents.

    Args:
        dir_path: Path to the directory to delete

    Returns:
        True if deleted, False otherwise
    """
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            logger.info(f"Deleted directory: {dir_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting directory {dir_path}: {e}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    return os.path.getsize(file_path) / (1024 * 1024)


def ensure_upload_dirs() -> None:
    """Ensure all upload directories exist."""
    dirs = [
        settings.UPLOAD_DIR,
        os.path.join(settings.UPLOAD_DIR, "videos"),
        os.path.join(settings.UPLOAD_DIR, "crops"),
        os.path.join(settings.UPLOAD_DIR, "masks"),
        os.path.join(settings.UPLOAD_DIR, "frames"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    logger.info("Upload directories initialized")
