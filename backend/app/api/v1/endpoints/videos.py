"""Video management API endpoints."""
import asyncio
import os
import tempfile
from typing import Any

import cv2
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models import Detection, User, Video
from app.schemas import VideoResponse, VideoProcessingStatus
from app.services import get_video_processor
from app.utils import (
    is_valid_video,
    save_upload_file,
    get_video_metadata,
    delete_file,
    delete_directory,
    get_file_size_mb,
)

router = APIRouter()

# Store for WebSocket connections (simple in-memory for demo)
processing_status: dict[int, VideoProcessingStatus] = {}


@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Video:
    """
    Upload a video file for processing.

    Args:
        file: Video file to upload
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created video record
    """
    # Validate file type
    if not file.filename or not is_valid_video(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video format. Allowed: mp4, avi, mov, mkv, wmv, flv",
        )

    # Save file
    videos_dir = os.path.join(settings.UPLOAD_DIR, "videos")
    file_path = await save_upload_file(file, videos_dir)

    # Check file size
    file_size = get_file_size_mb(file_path)
    if file_size > settings.MAX_UPLOAD_SIZE_MB:
        delete_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    try:
        # Extract video metadata
        metadata = get_video_metadata(file_path)

        # Create video record
        video = Video(
            filename=file.filename,
            file_path=file_path,
            duration_seconds=metadata["duration_seconds"],
            fps=metadata["fps"],
            resolution=metadata["resolution"],
            total_frames=metadata["total_frames"],
            processing_status="uploaded",
            uploaded_by=current_user.user_id,
        )
        db.add(video)
        db.commit()
        db.refresh(video)

        return video

    except Exception as e:
        delete_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing video: {str(e)}",
        )


@router.post("/{video_id}/process", response_model=dict[str, Any])
async def process_video(
    video_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Start processing a video for person detection.

    Args:
        video_id: Video ID to process
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user

    Returns:
        Processing status
    """
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    if video.processing_status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is already being processed",
        )

    # Initialize processing status
    processing_status[video_id] = VideoProcessingStatus(
        video_id=video_id,
        status="processing",
        progress=0,
        total_frames=video.total_frames,
    )

    # Start processing in background
    def update_status(status_data: dict[str, Any]) -> None:
        processing_status[video_id] = VideoProcessingStatus(**status_data)

    async def run_processing() -> None:
        processor = get_video_processor(db)
        await processor.process_video(video_id, progress_callback=update_status)

    background_tasks.add_task(asyncio.create_task, run_processing())

    return {
        "message": "Processing started",
        "video_id": video_id,
        "status": "processing",
    }


@router.get("/{video_id}/status", response_model=VideoProcessingStatus)
def get_processing_status(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoProcessingStatus:
    """
    Get current processing status for a video.

    Args:
        video_id: Video ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Processing status
    """
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    if video_id in processing_status:
        return processing_status[video_id]

    # Return status from database
    return VideoProcessingStatus(
        video_id=video_id,
        status=video.processing_status,
        progress=100 if video.processing_status == "completed" else 0,
        total_frames=video.total_frames,
    )


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Video:
    """
    Get video details by ID.

    Args:
        video_id: Video ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Video details
    """
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    return video


@router.get("", response_model=list[VideoResponse])
def list_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    status_filter: str | None = None,
) -> list[Video]:
    """
    List all videos with optional filtering.

    Args:
        db: Database session
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records
        status_filter: Optional status filter

    Returns:
        List of videos
    """
    query = db.query(Video)

    if status_filter:
        query = query.filter(Video.processing_status == status_filter)

    videos = query.order_by(Video.upload_timestamp.desc()).offset(skip).limit(limit).all()
    return videos


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Delete a video and its associated data.

    Args:
        video_id: Video ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        Deletion confirmation
    """
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Delete video file
    if video.file_path:
        delete_file(video.file_path)

    # Delete crops directory
    crops_dir = os.path.join(settings.UPLOAD_DIR, "crops", str(video_id))
    delete_directory(crops_dir)

    # Delete from database (cascades to detections and attributes)
    db.delete(video)
    db.commit()

    # Remove from processing status if present
    if video_id in processing_status:
        del processing_status[video_id]

    return {"message": "Video deleted successfully"}


@router.get("/{video_id}/clip/{detection_id}")
def extract_video_clip(
    video_id: int,
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    buffer_before: float = Query(3.0, ge=0, le=30, description="Seconds before detection"),
    buffer_after: float = Query(3.0, ge=0, le=30, description="Seconds after detection"),
) -> FileResponse:
    """
    FR11: Video Clip Extraction - Generate video clip containing detected person
    with configurable buffer duration before/after detection timestamp.

    Args:
        video_id: Video ID
        detection_id: Detection ID
        db: Database session
        current_user: Current authenticated user
        buffer_before: Seconds to include before detection (default: 3.0)
        buffer_after: Seconds to include after detection (default: 3.0)

    Returns:
        Video clip file response
    """
    # Verify video exists
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    if not video.file_path or not os.path.exists(video.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found",
        )

    # Verify detection exists and belongs to this video
    detection = (
        db.query(Detection)
        .filter(Detection.detection_id == detection_id, Detection.video_id == video_id)
        .first()
    )
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found for this video",
        )

    # Open source video
    cap = cv2.VideoCapture(video.file_path)
    if not cap.isOpened():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot open video file",
        )

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    # Calculate start and end frames with buffer
    detection_time = detection.timestamp_in_video
    start_time = max(0, detection_time - buffer_before)
    end_time = min(duration, detection_time + buffer_after)

    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    # Create temp file for output clip
    temp_dir = tempfile.gettempdir()
    clip_filename = f"clip_{video_id}_{detection_id}.mp4"
    clip_path = os.path.join(temp_dir, clip_filename)

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))

    # Extract frames
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    for frame_num in range(start_frame, end_frame + 1):
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()

    if not os.path.exists(clip_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create video clip",
        )

    return FileResponse(
        clip_path,
        media_type="video/mp4",
        filename=f"detection_{detection_id}_clip.mp4",
    )


@router.get("/{video_id}/clip-by-time")
def extract_clip_by_timerange(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_time: float = Query(..., ge=0, description="Start time in seconds"),
    end_time: float = Query(..., ge=0, description="End time in seconds"),
) -> FileResponse:
    """
    Extract a video clip by specifying time range.

    Args:
        video_id: Video ID
        db: Database session
        current_user: Current authenticated user
        start_time: Start time in seconds
        end_time: End time in seconds

    Returns:
        Video clip file response
    """
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    if not video.file_path or not os.path.exists(video.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found",
        )

    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be less than end_time",
        )

    # Open source video
    cap = cv2.VideoCapture(video.file_path)
    if not cap.isOpened():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot open video file",
        )

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    # Validate time range
    if start_time > duration or end_time > duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Time range exceeds video duration ({duration:.2f}s)",
        )

    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)

    # Create temp file for output clip
    temp_dir = tempfile.gettempdir()
    clip_filename = f"clip_{video_id}_{start_time:.0f}_{end_time:.0f}.mp4"
    clip_path = os.path.join(temp_dir, clip_filename)

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(clip_path, fourcc, fps, (width, height))

    # Extract frames
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    for frame_num in range(start_frame, end_frame + 1):
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()

    return FileResponse(
        clip_path,
        media_type="video/mp4",
        filename=f"video_{video_id}_clip_{start_time:.0f}s_{end_time:.0f}s.mp4",
    )
