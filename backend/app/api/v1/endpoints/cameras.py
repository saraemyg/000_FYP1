"""Camera management API endpoints."""
import os
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user, get_current_user, get_db
from app.core.config import settings
from app.models import Camera, SegmentationMask, User
from app.schemas import CameraCreate, CameraResponse, CameraUpdate, SegmentationMaskResponse
from app.services import get_segmentation_service
from app.utils import is_valid_image, save_upload_file

router = APIRouter()


@router.get("", response_model=list[CameraResponse])
def list_cameras(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_inactive: bool = False,
) -> list[Camera]:
    """
    List all cameras.

    Args:
        db: Database session
        current_user: Current authenticated user
        include_inactive: Include inactive cameras

    Returns:
        List of cameras
    """
    query = db.query(Camera)

    if not include_inactive:
        query = query.filter(Camera.is_active == True)

    cameras = query.order_by(Camera.camera_name).all()
    return cameras


@router.post("", response_model=CameraResponse)
def create_camera(
    camera_data: CameraCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> Camera:
    """
    Create a new camera entry (admin only).

    Args:
        camera_data: Camera creation data
        db: Database session
        current_admin: Current admin user

    Returns:
        Created camera
    """
    camera = Camera(
        camera_name=camera_data.camera_name,
        location=camera_data.location,
        resolution=camera_data.resolution,
        fps=camera_data.fps,
        is_active=True,
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)

    return camera


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Camera:
    """
    Get camera by ID.

    Args:
        camera_id: Camera ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Camera details
    """
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> Camera:
    """
    Update camera information (admin only).

    Args:
        camera_id: Camera ID
        camera_data: Camera update data
        db: Database session
        current_admin: Current admin user

    Returns:
        Updated camera
    """
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    # Update fields
    update_data = camera_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)

    db.commit()
    db.refresh(camera)

    return camera


@router.delete("/{camera_id}")
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> dict[str, str]:
    """
    Delete a camera (admin only).

    Args:
        camera_id: Camera ID
        db: Database session
        current_admin: Current admin user

    Returns:
        Deletion confirmation
    """
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    db.delete(camera)
    db.commit()

    return {"message": "Camera deleted successfully"}


@router.post("/{camera_id}/mask/generate", response_model=SegmentationMaskResponse)
async def generate_camera_mask(
    camera_id: int,
    sample_frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> SegmentationMask:
    """
    Generate segmentation mask for a camera (admin only).

    STUB: Generates a mock segmentation mask.
    TODO FYP2: Replace with actual semantic segmentation.

    Args:
        camera_id: Camera ID
        sample_frame: Sample frame image for mask generation
        db: Database session
        current_admin: Current admin user

    Returns:
        Generated segmentation mask
    """
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    # Validate file type
    if not sample_frame.filename or not is_valid_image(sample_frame.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed: jpg, jpeg, png, bmp, gif",
        )

    # Save sample frame
    frames_dir = os.path.join(settings.UPLOAD_DIR, "frames")
    sample_path = await save_upload_file(
        sample_frame,
        frames_dir,
        filename=f"camera_{camera_id}_sample.jpg",
    )

    # Load image and generate mask (STUB)
    import cv2
    import numpy as np

    image = cv2.imread(sample_path)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot read uploaded image",
        )

    segmentation = get_segmentation_service()
    mask, reduction_pct = segmentation.generate_mask(image)
    mask_path = segmentation.save_mask(mask, camera_id)

    # Update camera mask path
    camera.mask_file_path = mask_path
    db.commit()

    # Create mask record
    mask_record = SegmentationMask(
        camera_id=camera_id,
        mask_file_path=mask_path,
        reduction_percentage=reduction_pct,
        sample_frame_path=sample_path,
    )
    db.add(mask_record)
    db.commit()
    db.refresh(mask_record)

    return mask_record


@router.get("/{camera_id}/masks", response_model=list[SegmentationMaskResponse])
def get_camera_masks(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SegmentationMask]:
    """
    Get all segmentation masks for a camera.

    Args:
        camera_id: Camera ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of segmentation masks
    """
    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )

    masks = (
        db.query(SegmentationMask)
        .filter(SegmentationMask.camera_id == camera_id)
        .order_by(SegmentationMask.generation_timestamp.desc())
        .all()
    )

    return masks
