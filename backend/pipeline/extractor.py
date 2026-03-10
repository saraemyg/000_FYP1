"""
Frame Extractor (EXTRACT Stage)
================================
Reads video files frame-by-frame using OpenCV.
Adds metadata (timestamp, frame number, camera ID) to each frame.
Uses a thread-safe queue so frame reading doesn't block processing.

Simple explanation:
- Think of this as a "video player" that reads one image at a time
- It puts each image into a queue (like a conveyor belt)
- The next stage (ROI pruning) picks images off the belt
"""

import cv2
import logging
import threading
import queue
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import numpy as np

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class FrameData:
    """Container for one frame + its metadata."""
    frame: np.ndarray          # the actual image (H x W x 3 BGR)
    frame_number: int          # sequential frame count
    timestamp: datetime        # estimated capture time
    camera_id: str             # which camera this came from


class FrameExtractor:
    """
    Reads frames from a video file and puts them in a queue.
    
    Usage:
        extractor = FrameExtractor("cam_01", "data/entrance.mp4")
        extractor.start()
        
        while True:
            frame_data = extractor.get_frame()
            if frame_data is None:
                break  # video ended
            # process frame_data...
    """

    def __init__(self, camera_id: str, video_path: str, target_fps: int = None):
        self.camera_id = camera_id
        self.video_path = video_path
        self.target_fps = target_fps or settings.TARGET_FPS

        # Thread-safe queue to buffer frames
        self.frame_queue: queue.Queue = queue.Queue(maxsize=settings.FRAME_QUEUE_SIZE)

        # State
        self._cap: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._frame_count = 0
        self._video_fps = 30.0
        self._total_frames = 0

    @property
    def video_fps(self) -> float:
        return self._video_fps

    @property
    def total_frames(self) -> int:
        return self._total_frames

    def start(self):
        """Open video and start reading frames in background thread."""
        self._cap = cv2.VideoCapture(self.video_path)

        if not self._cap.isOpened():
            raise FileNotFoundError(f"Cannot open video: {self.video_path}")

        self._video_fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(
            f"[{self.camera_id}] Opened video: {self.video_path} "
            f"({self._total_frames} frames @ {self._video_fps:.1f} FPS)"
        )

        # Calculate frame skip interval
        # If video is 30fps and we want 15fps, we skip every other frame
        self._skip_interval = max(1, int(self._video_fps / self.target_fps))

        # Start reading in a separate thread so it doesn't block processing
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        """Background thread: continuously reads frames from video."""
        frame_idx = 0

        while not self._stop_event.is_set():
            ret, frame = self._cap.read()

            if not ret:
                # Video ended or read error
                self.frame_queue.put(None)  # signal end of video
                break

            frame_idx += 1

            # Skip frames to match target FPS
            if frame_idx % self._skip_interval != 0:
                continue

            # Skip corrupted frames (all black or all white)
            if frame is None or frame.size == 0:
                logger.warning(f"[{self.camera_id}] Skipped corrupted frame {frame_idx}")
                continue

            # Calculate estimated timestamp
            timestamp = datetime.utcnow() - timedelta(
                seconds=(self._total_frames - frame_idx) / self._video_fps
            )

            frame_data = FrameData(
                frame=frame,
                frame_number=frame_idx,
                timestamp=timestamp,
                camera_id=self.camera_id,
            )

            try:
                # Put frame in queue, wait up to 1 second if queue is full
                self.frame_queue.put(frame_data, timeout=1.0)
                self._frame_count += 1
            except queue.Full:
                # Queue full = processing can't keep up, drop this frame
                logger.warning(f"[{self.camera_id}] Frame queue full, dropping frame {frame_idx}")

        self._cap.release()
        logger.info(f"[{self.camera_id}] Video reading complete. {self._frame_count} frames extracted.")

    def get_frame(self, timeout: float = 5.0) -> Optional[FrameData]:
        """
        Get the next frame from the queue.
        Returns None when video is finished.
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        """Stop reading frames."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._cap and self._cap.isOpened():
            self._cap.release()

    @property
    def frames_extracted(self) -> int:
        return self._frame_count
