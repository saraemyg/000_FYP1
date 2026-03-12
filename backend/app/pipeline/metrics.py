"""Metrics Logger — tracks FPS, GPU, latency. Saves to PerformanceMetric table."""
import time
from collections import deque
from loguru import logger
from app.db.session import SessionLocal
from app.models.performance import PerformanceMetric

METRICS_LOG_INTERVAL = 5  # seconds


class MetricsLogger:
    def __init__(self, video_id: int):
        self.video_id = video_id
        self._frame_times: deque = deque(maxlen=60)
        self._start: float = 0
        self._last_log: float = time.time()
        self._total_detections = 0
        self._total_alerts = 0

    def frame_start(self):
        self._start = time.time()

    def frame_end(self, detections: int = 0, alerts: int = 0):
        self._frame_times.append(time.time() - self._start)
        self._total_detections += detections
        self._total_alerts += alerts
        if time.time() - self._last_log >= METRICS_LOG_INTERVAL:
            self._save()
            self._last_log = time.time()

    @property
    def current_fps(self) -> float:
        if not self._frame_times:
            return 0.0
        avg = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / avg if avg > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        if not self._frame_times:
            return 0.0
        return (sum(self._frame_times) / len(self._frame_times)) * 1000

    def _save(self):
        try:
            db = SessionLocal()
            metric = PerformanceMetric(
                video_id=self.video_id,
                avg_fps=round(self.current_fps, 2),
                total_detections=self._total_detections,
                processing_time_seconds=round(sum(self._frame_times), 2),
            )
            db.add(metric)
            db.commit()
            db.close()
            fps = self.current_fps
            tag = "✓" if fps >= 15 else "⚠"
            logger.info(f"{tag} FPS: {fps:.1f} | Latency: {self.avg_latency_ms:.0f}ms | Detections: {self._total_detections}")
        except Exception as e:
            logger.error(f"Metrics save error: {e}")
