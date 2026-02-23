"""
Video processing service (STUB implementation).

This module orchestrates video processing with detection and attribute extraction.
TODO FYP2: Replace stub implementations with actual model inference.
"""
import asyncio
import os
import random
import time
from typing import Any, Callable, Optional

import cv2
import numpy as np
from loguru import logger
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Attribute, Detection, PerformanceMetric, Video
from app.services.detector import get_detector
from app.services.attribute_classifier import get_attribute_classifier


class VideoProcessor:
    """Video processing orchestrator with detection and attribute extraction."""

    def __init__(self, db: Session) -> None:
        """
        Initialize video processor.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.detector = get_detector()
        self.classifier = get_attribute_classifier()

    async def process_video(
        self,
        video_id: int,
        progress_callback: Optional[Callable[[dict[str, Any]], None]] = None,
    ) -> dict[str, Any]:
        """
        Process a video file with detection and attribute extraction.

        STUB: Simulates video processing without actual model inference.
        TODO FYP2: Replace with actual YOLOv11 + ResNet-50 pipeline.

        Args:
            video_id: Database ID of the video to process
            progress_callback: Optional callback for progress updates

        Returns:
            Processing result dictionary
        """
        start_time = time.time()

        # Get video record
        video = self.db.query(Video).filter(Video.video_id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")

        logger.info(f"Starting processing for video {video_id}: {video.filename}")

        # Update status to processing
        video.processing_status = "processing"
        self.db.commit()

        try:
            # Open video file
            cap = cv2.VideoCapture(video.file_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video.file_path}")

            # Extract video metadata
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            # Update video metadata
            video.fps = fps
            video.total_frames = frame_count
            video.resolution = f"{width}x{height}"
            video.duration_seconds = duration
            self.db.commit()

            logger.info(
                f"Video metadata: {width}x{height}, {fps:.2f} FPS, "
                f"{frame_count} frames, {duration:.2f}s"
            )

            # Create crops directory
            crops_dir = os.path.join(settings.UPLOAD_DIR, "crops", str(video_id))
            os.makedirs(crops_dir, exist_ok=True)

            # Process frames (sample every N frames for efficiency)
            # FR7: Real-Time Attribute Recognition - configurable frame interval
            # Default: every 5th frame to balance accuracy and computational efficiency
            frame_interval = max(1, settings.ATTRIBUTE_INTERVAL_FRAMES)
            total_detections = 0
            processed_frames = 0

            for frame_num in range(0, frame_count, frame_interval):
                # Read frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if not ret:
                    continue

                processed_frames += 1
                timestamp = frame_num / fps

                # Detect persons in frame (STUB)
                detections = self.detector.detect_persons(frame)

                # Process each detection
                for det_idx, det in enumerate(detections):
                    bbox = det["bbox"]
                    x, y, w, h = bbox

                    # Ensure bbox is within frame bounds
                    x = max(0, min(x, width - 1))
                    y = max(0, min(y, height - 1))
                    w = min(w, width - x)
                    h = min(h, height - y)

                    if w <= 0 or h <= 0:
                        continue

                    # Extract person crop
                    person_crop = frame[y:y+h, x:x+w]

                    # Save crop image
                    crop_filename = f"frame_{frame_num}_det_{det_idx}.jpg"
                    crop_path = os.path.join(crops_dir, crop_filename)
                    cv2.imwrite(crop_path, person_crop)

                    # Classify attributes (STUB)
                    attributes = self.classifier.classify_attributes(person_crop)

                    # Create detection record
                    detection = Detection(
                        video_id=video_id,
                        frame_number=frame_num,
                        timestamp_in_video=timestamp,
                        bbox_x=x,
                        bbox_y=y,
                        bbox_width=w,
                        bbox_height=h,
                        detection_confidence=det["confidence"],
                        person_crop_path=crop_path,
                    )
                    self.db.add(detection)
                    self.db.flush()  # Get detection_id

                    # Create attribute record
                    attribute = Attribute(
                        detection_id=detection.detection_id,
                        upper_color=attributes["upper_color"],
                        upper_color_confidence=attributes["upper_color_confidence"],
                        lower_color=attributes["lower_color"],
                        lower_color_confidence=attributes["lower_color_confidence"],
                        gender=attributes["gender"],
                        gender_confidence=attributes["gender_confidence"],
                    )
                    self.db.add(attribute)
                    total_detections += 1

                # Send progress update
                progress = (frame_num / frame_count) * 100
                if progress_callback:
                    progress_callback({
                        "video_id": video_id,
                        "status": "processing",
                        "progress": round(progress, 1),
                        "current_frame": frame_num,
                        "total_frames": frame_count,
                        "detections_count": total_detections,
                    })

                # Small delay to simulate processing time
                await asyncio.sleep(0.01)

            cap.release()

            # Calculate processing time
            processing_time = time.time() - start_time
            avg_fps = processed_frames / processing_time if processing_time > 0 else 0

            # Create performance metric record
            metric = PerformanceMetric(
                video_id=video_id,
                avg_fps=avg_fps,
                total_detections=total_detections,
                processing_time_seconds=processing_time,
                area_reduction_percentage=random.uniform(30, 50),  # STUB
            )
            self.db.add(metric)

            # Update video status
            video.processing_status = "completed"
            self.db.commit()

            result = {
                "status": "completed",
                "video_id": video_id,
                "total_detections": total_detections,
                "processing_time": round(processing_time, 2),
                "avg_fps": round(avg_fps, 2),
            }

            logger.info(
                f"Video {video_id} processing completed: "
                f"{total_detections} detections in {processing_time:.2f}s"
            )

            # Final progress callback
            if progress_callback:
                progress_callback({
                    "video_id": video_id,
                    "status": "completed",
                    "progress": 100,
                    "current_frame": frame_count,
                    "total_frames": frame_count,
                    "detections_count": total_detections,
                    "message": "Processing completed successfully",
                })

            return result

        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            video.processing_status = "failed"
            self.db.commit()

            if progress_callback:
                progress_callback({
                    "video_id": video_id,
                    "status": "failed",
                    "progress": 0,
                    "message": str(e),
                })

            raise


def get_video_processor(db: Session) -> VideoProcessor:
    """Create a video processor instance with the given database session."""
    return VideoProcessor(db)
