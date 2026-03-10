"""
Metrics Logger
===============
Tracks pipeline performance: FPS, GPU usage, processing time per stage.
Saves to system_metrics table for the admin Performance Dashboard (UR5).
"""

import time
import logging
from collections import deque
from typing import Optional

from db.database import get_db_session
from db.models import SystemMetric
from config import settings

logger = logging.getLogger(__name__)


class MetricsLogger:
    """
    Tracks and logs pipeline performance metrics.
    
    Usage:
        metrics = MetricsLogger(camera_db_id=1)
        
        # In processing loop:
        metrics.frame_start()
        # ... process frame ...
        metrics.frame_end(detections_count=5)
        
        # Periodically saves to DB automatically
    """

    def __init__(self, camera_db_id: int):
        self.camera_db_id = camera_db_id

        # FPS calculation using rolling window
        self._frame_times: deque = deque(maxlen=60)
        self._frame_start_time: float = 0
        self._last_log_time: float = time.time()
        self._total_detections: int = 0
        self._total_alerts: int = 0
        self._frames_since_last_log: int = 0

    def frame_start(self):
        """Call at the beginning of processing each frame."""
        self._frame_start_time = time.time()

    def frame_end(self, detections_count: int = 0, alerts_count: int = 0):
        """Call after frame processing is complete."""
        elapsed = time.time() - self._frame_start_time
        self._frame_times.append(elapsed)
        self._total_detections += detections_count
        self._total_alerts += alerts_count
        self._frames_since_last_log += 1

        # Auto-log to DB every N seconds
        if time.time() - self._last_log_time >= settings.METRICS_LOG_INTERVAL:
            self._save_to_db()
            self._last_log_time = time.time()

    @property
    def current_fps(self) -> float:
        """Calculate current FPS from recent frame times."""
        if not self._frame_times:
            return 0.0
        avg_time = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        """Average per-frame processing time in milliseconds."""
        if not self._frame_times:
            return 0.0
        return (sum(self._frame_times) / len(self._frame_times)) * 1000

    def _get_gpu_stats(self) -> dict:
        """Get GPU utilization and memory usage."""
        try:
            import torch
            if torch.cuda.is_available():
                return {
                    "gpu_util": 0.0,  # need nvidia-smi or pynvml for real value
                    "gpu_memory_mb": torch.cuda.memory_allocated() / 1024 / 1024,
                }
        except ImportError:
            pass
        return {"gpu_util": 0.0, "gpu_memory_mb": 0.0}

    def _save_to_db(self):
        """Save current metrics to database."""
        try:
            gpu = self._get_gpu_stats()

            with get_db_session() as db:
                metric = SystemMetric(
                    camera_id=self.camera_db_id,
                    fps=round(self.current_fps, 2),
                    avg_latency_ms=round(self.avg_latency_ms, 2),
                    gpu_util=gpu["gpu_util"],
                    gpu_memory_mb=round(gpu["gpu_memory_mb"], 1),
                    detections_count=self._total_detections,
                    alerts_count=self._total_alerts,
                    pipeline_status="RUNNING",
                )
                db.add(metric)

            fps = self.current_fps
            status = "✓" if fps >= settings.TARGET_FPS else "⚠"
            logger.info(
                f"{status} [{self.camera_db_id}] FPS: {fps:.1f} | "
                f"Latency: {self.avg_latency_ms:.0f}ms | "
                f"GPU Mem: {gpu['gpu_memory_mb']:.0f}MB | "
                f"Detections: {self._total_detections}"
            )

            # Reset counters
            self._frames_since_last_log = 0

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
