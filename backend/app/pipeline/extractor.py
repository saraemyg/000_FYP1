"""Frame Extractor (EXTRACT stage) — reads video frames with metadata."""
import cv2
import threading
import queue
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
import numpy as np
from loguru import logger


@dataclass
class FrameData:
    """One frame + its metadata."""
    frame: np.ndarray
    frame_number: int
    timestamp: datetime
    camera_id: str


class FrameExtractor:
    """Reads frames from a video file in a background thread."""

    def __init__(self, camera_id: str, video_path: str, target_fps: int = 15):
        self.camera_id = camera_id
        self.video_path = video_path
        self.target_fps = target_fps
        self.frame_queue: queue.Queue = queue.Queue(maxsize=30)
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
        self._cap = cv2.VideoCapture(self.video_path)
        if not self._cap.isOpened():
            raise FileNotFoundError(f"Cannot open video: {self.video_path}")
        self._video_fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._skip_interval = max(1, int(self._video_fps / self.target_fps))
        logger.info(f"[{self.camera_id}] Opened {self.video_path} ({self._total_frames} frames @ {self._video_fps:.0f}fps, skip={self._skip_interval})")
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        frame_idx = 0
        while not self._stop_event.is_set():
            ret, frame = self._cap.read()
            if not ret:
                self.frame_queue.put(None)
                break
            frame_idx += 1
            if frame_idx % self._skip_interval != 0:
                continue
            if frame is None or frame.size == 0:
                continue
            ts = datetime.utcnow() - timedelta(seconds=(self._total_frames - frame_idx) / self._video_fps)
            try:
                self.frame_queue.put(FrameData(frame=frame, frame_number=frame_idx, timestamp=ts, camera_id=self.camera_id), timeout=1.0)
                self._frame_count += 1
            except queue.Full:
                pass
        self._cap.release()

    def get_frame(self, timeout: float = 5.0) -> Optional[FrameData]:
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._cap and self._cap.isOpened():
            self._cap.release()

    @property
    def frames_extracted(self) -> int:
        return self._frame_count
