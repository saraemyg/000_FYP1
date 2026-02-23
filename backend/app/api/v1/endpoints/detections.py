"""Detection API endpoints."""
import os
import tempfile

import cv2
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models import Attribute, Detection, User, Video
from app.schemas import DetectionResponse
from app.utils.image_utils import draw_bounding_box

router = APIRouter()


# Color mapping for visualization
COLOR_MAP = {
    "red": (0, 0, 255),
    "blue": (255, 0, 0),
    "green": (0, 255, 0),
    "yellow": (0, 255, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "brown": (42, 42, 165),
    "pink": (203, 192, 255),
    "orange": (0, 165, 255),
}


@router.get("/video/{video_id}", response_model=list[DetectionResponse])
def get_video_detections(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    min_confidence: float = 0.0,
) -> list[Detection]:
    """
    Get all detections for a specific video.

    Args:
        video_id: Video ID
        db: Database session
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records
        min_confidence: Minimum detection confidence

    Returns:
        List of detections
    """
    # Verify video exists
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Query detections with attributes
    detections = (
        db.query(Detection)
        .options(joinedload(Detection.attributes))
        .filter(Detection.video_id == video_id)
        .filter(Detection.detection_confidence >= min_confidence)
        .order_by(Detection.frame_number)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return detections


@router.get("/{detection_id}", response_model=DetectionResponse)
def get_detection(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Detection:
    """
    Get a specific detection by ID.

    Args:
        detection_id: Detection ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Detection details
    """
    detection = (
        db.query(Detection)
        .options(joinedload(Detection.attributes))
        .filter(Detection.detection_id == detection_id)
        .first()
    )

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    return detection


@router.get("/{detection_id}/image")
def get_detection_image(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """
    Get the cropped person image for a detection.

    Args:
        detection_id: Detection ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Image file response
    """
    detection = db.query(Detection).filter(Detection.detection_id == detection_id).first()

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    if not detection.person_crop_path or not os.path.exists(detection.person_crop_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection image not found",
        )

    return FileResponse(
        detection.person_crop_path,
        media_type="image/jpeg",
        filename=f"detection_{detection_id}.jpg",
    )


@router.get("/video/{video_id}/summary")
def get_video_detection_summary(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get summary statistics for detections in a video.

    Args:
        video_id: Video ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Detection summary statistics
    """
    # Verify video exists
    video = db.query(Video).filter(Video.video_id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Get all detections with attributes
    detections = (
        db.query(Detection)
        .options(joinedload(Detection.attributes))
        .filter(Detection.video_id == video_id)
        .all()
    )

    # Calculate summary
    total = len(detections)
    gender_counts = {"male": 0, "female": 0, "unknown": 0}
    upper_color_counts: dict[str, int] = {}
    lower_color_counts: dict[str, int] = {}

    for det in detections:
        for attr in det.attributes:
            if attr.gender:
                gender_counts[attr.gender] = gender_counts.get(attr.gender, 0) + 1

            if attr.upper_color:
                upper_color_counts[attr.upper_color] = (
                    upper_color_counts.get(attr.upper_color, 0) + 1
                )

            if attr.lower_color:
                lower_color_counts[attr.lower_color] = (
                    lower_color_counts.get(attr.lower_color, 0) + 1
                )

    return {
        "video_id": video_id,
        "total_detections": total,
        "gender_distribution": gender_counts,
        "upper_color_distribution": upper_color_counts,
        "lower_color_distribution": lower_color_counts,
    }


@router.get("/{detection_id}/annotated-frame")
def get_annotated_frame(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    show_all_detections: bool = Query(
        False, description="Show all detections in the same frame"
    ),
) -> FileResponse:
    """
    Get the source video frame with bounding box and attribute labels overlaid.

    FR4: Detection Visualization - Display detection results with bounding boxes
    overlaid on source video frames, showing detected attribute labels and
    confidence scores for user verification.

    Args:
        detection_id: Detection ID
        db: Database session
        current_user: Current authenticated user
        show_all_detections: If True, show all detections from the same frame

    Returns:
        Annotated image file response
    """
    # Get detection with attributes
    detection = (
        db.query(Detection)
        .options(joinedload(Detection.attributes))
        .filter(Detection.detection_id == detection_id)
        .first()
    )

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    # Get video to access source file
    video = db.query(Video).filter(Video.video_id == detection.video_id).first()
    if not video or not video.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found",
        )

    # Extract frame from video
    cap = cv2.VideoCapture(video.file_path)
    if not cap.isOpened():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot open video file",
        )

    cap.set(cv2.CAP_PROP_POS_FRAMES, detection.frame_number)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot read video frame",
        )

    # Get detections to draw
    if show_all_detections:
        detections = (
            db.query(Detection)
            .options(joinedload(Detection.attributes))
            .filter(
                Detection.video_id == detection.video_id,
                Detection.frame_number == detection.frame_number,
            )
            .all()
        )
    else:
        detections = [detection]

    # Draw bounding boxes with labels
    for det in detections:
        # Build label from attributes
        attr = det.attributes[0] if det.attributes else None
        label_parts = []

        if attr:
            if attr.gender and attr.gender != "unknown":
                label_parts.append(f"{attr.gender.upper()}")
            if attr.upper_color:
                label_parts.append(f"Top:{attr.upper_color}")
            if attr.lower_color:
                label_parts.append(f"Bot:{attr.lower_color}")

        confidence = det.detection_confidence
        label_parts.append(f"{confidence:.0%}")
        label = " | ".join(label_parts)

        # Choose color based on upper body color or default green
        box_color = (0, 255, 0)  # Default green
        if attr and attr.upper_color:
            box_color = COLOR_MAP.get(attr.upper_color.lower(), (0, 255, 0))

        # Highlight primary detection differently
        thickness = 3 if det.detection_id == detection_id else 2

        frame = draw_bounding_box(
            frame,
            det.bbox_x,
            det.bbox_y,
            det.bbox_width,
            det.bbox_height,
            color=box_color,
            thickness=thickness,
            label=label,
        )

    # Save annotated frame to temp file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"annotated_{detection_id}.jpg")
    cv2.imwrite(temp_path, frame)

    return FileResponse(
        temp_path,
        media_type="image/jpeg",
        filename=f"annotated_detection_{detection_id}.jpg",
    )


@router.get("/frame/{video_id}/{frame_number}/annotated")
def get_frame_with_all_detections(
    video_id: int,
    frame_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """
    Get a specific video frame with all detections overlaid.

    Args:
        video_id: Video ID
        frame_number: Frame number
        db: Database session
        current_user: Current authenticated user

    Returns:
        Annotated image file response
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

    # Extract frame from video
    cap = cv2.VideoCapture(video.file_path)
    if not cap.isOpened():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot open video file",
        )

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot read frame {frame_number}",
        )

    # Get all detections for this frame
    detections = (
        db.query(Detection)
        .options(joinedload(Detection.attributes))
        .filter(
            Detection.video_id == video_id,
            Detection.frame_number == frame_number,
        )
        .all()
    )

    # Draw all detections
    for det in detections:
        attr = det.attributes[0] if det.attributes else None
        label_parts = []

        if attr:
            if attr.gender and attr.gender != "unknown":
                label_parts.append(f"{attr.gender.upper()}")
            if attr.upper_color:
                label_parts.append(f"Top:{attr.upper_color}")
            if attr.lower_color:
                label_parts.append(f"Bot:{attr.lower_color}")

        label_parts.append(f"{det.detection_confidence:.0%}")
        label = " | ".join(label_parts)

        box_color = (0, 255, 0)
        if attr and attr.upper_color:
            box_color = COLOR_MAP.get(attr.upper_color.lower(), (0, 255, 0))

        frame = draw_bounding_box(
            frame,
            det.bbox_x,
            det.bbox_y,
            det.bbox_width,
            det.bbox_height,
            color=box_color,
            thickness=2,
            label=label,
        )

    # Save annotated frame
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"frame_{video_id}_{frame_number}.jpg")
    cv2.imwrite(temp_path, frame)

    return FileResponse(
        temp_path,
        media_type="image/jpeg",
        filename=f"frame_{video_id}_{frame_number}_annotated.jpg",
    )
