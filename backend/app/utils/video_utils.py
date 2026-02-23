"""Video processing utilities."""
from typing import Any

import cv2
from loguru import logger


def get_video_metadata(file_path: str) -> dict[str, Any]:
    """
    Extract metadata from a video file.

    Args:
        file_path: Path to the video file

    Returns:
        Dictionary with video metadata
    """
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {file_path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0

        metadata = {
            "fps": round(fps, 2),
            "total_frames": frame_count,
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}",
            "duration_seconds": round(duration, 2),
        }

        logger.debug(f"Video metadata for {file_path}: {metadata}")
        return metadata

    finally:
        cap.release()


def extract_frame(file_path: str, frame_number: int) -> Any:
    """
    Extract a specific frame from a video.

    Args:
        file_path: Path to the video file
        frame_number: Frame number to extract

    Returns:
        Frame as numpy array (BGR format)
    """
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {file_path}")

    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if not ret:
            raise ValueError(f"Cannot read frame {frame_number} from {file_path}")

        return frame

    finally:
        cap.release()


def extract_thumbnail(file_path: str, output_path: str, target_frame: int = 0) -> str:
    """
    Extract a thumbnail image from a video.

    Args:
        file_path: Path to the video file
        output_path: Path to save the thumbnail
        target_frame: Frame number to use as thumbnail

    Returns:
        Path to saved thumbnail
    """
    frame = extract_frame(file_path, target_frame)
    cv2.imwrite(output_path, frame)
    logger.info(f"Saved thumbnail to {output_path}")
    return output_path


def format_timestamp(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
