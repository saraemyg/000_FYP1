"""Alert Engine — checks behaviors against AlertRule table from app/models/alert.py.

When an alert fires it is saved to the DB AND published to Redis channel
'alerts' so the WebSocket broadcaster can push it to connected browsers.
"""
import json
from datetime import datetime
from typing import List, Optional, Dict
from collections import defaultdict
from loguru import logger

from app.db.session import SessionLocal
from app.models.alert import AlertRule, TriggeredAlert
from app.pipeline.detector import PersonDetection
from app.pipeline.classifier import BehaviorResult

ALERT_COOLDOWN_SECONDS = 10
REDIS_ALERT_CHANNEL = "alerts"


def _get_redis():
    """Return a Redis client, or None if Redis is unavailable."""
    try:
        import redis as _redis
        from app.core.config import settings
        return _redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        return None


class AlertEngine:
    """Evaluates behaviors against alert rules and publishes matches."""

    def __init__(self):
        self.rules: List[dict] = []
        self._cooldown: Dict[str, datetime] = defaultdict(lambda: datetime.min)
        self._redis = _get_redis()

    def load_rules(self):
        """Load active alert rules from database."""
        db = SessionLocal()
        try:
            rules = db.query(AlertRule).filter(AlertRule.is_active == True).all()
            self.rules = [
                {
                    "id": r.rule_id,
                    "name": r.name,
                    "min_confidence": r.min_confidence or 0.7,
                    "user_id": r.user_id,
                }
                for r in rules
            ]
            logger.info(f"Loaded {len(self.rules)} active alert rules")
        finally:
            db.close()

    def evaluate(
        self,
        detections: List[PersonDetection],
        behaviors: List[BehaviorResult],
        detection_ids: List[int],   # may be empty when async loader is used
        video_id: int,
        timestamp: datetime,
    ) -> List[int]:
        """Check behaviors against rules. Returns created alert IDs."""
        if not self.rules or not behaviors:
            return []

        alert_ids = []
        for i, (det, beh) in enumerate(zip(detections, behaviors)):
            if beh.behavior_type == "unknown":
                continue
            det_id = detection_ids[i] if i < len(detection_ids) else None
            for rule in self.rules:
                if (
                    beh.behavior_type.lower() in rule["name"].lower()
                    and beh.confidence >= rule["min_confidence"]
                ):
                    cooldown_key = f"{video_id}_{det.person_idx}_{beh.behavior_type}"
                    elapsed = (timestamp - self._cooldown[cooldown_key]).total_seconds()
                    if elapsed < ALERT_COOLDOWN_SECONDS:
                        continue
                    aid = self._create_alert(rule["id"], det_id, video_id, beh, timestamp)
                    if aid:
                        alert_ids.append(aid)
                        self._cooldown[cooldown_key] = timestamp
                    break
        return alert_ids

    def _create_alert(
        self,
        rule_id: int,
        detection_id: Optional[int],
        video_id: int,
        beh: BehaviorResult,
        timestamp: datetime,
    ) -> Optional[int]:
        db = SessionLocal()
        try:
            alert = TriggeredAlert(
                rule_id=rule_id,
                detection_id=detection_id,
                video_id=video_id,
                matched_attributes={"behavior": beh.behavior_type},
                confidence_score=beh.confidence,
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            logger.info(f"Alert #{alert.alert_id}: {beh.behavior_type} (conf={beh.confidence:.2f})")
            self._publish_redis(alert.alert_id, rule_id, video_id, beh, timestamp)
            return alert.alert_id
        except Exception as e:
            db.rollback()
            logger.error(f"Alert creation failed: {e}")
            return None
        finally:
            db.close()

    def _publish_redis(
        self,
        alert_id: int,
        rule_id: int,
        video_id: int,
        beh: BehaviorResult,
        timestamp: datetime,
    ):
        if self._redis is None:
            return
        try:
            payload = json.dumps({
                "alert_id":      alert_id,
                "rule_id":       rule_id,
                "video_id":      video_id,
                "behavior_type": beh.behavior_type,
                "confidence":    round(beh.confidence, 4),
                "triggered_at":  timestamp.isoformat(),
            })
            self._redis.publish(REDIS_ALERT_CHANNEL, payload)
        except Exception as e:
            logger.warning(f"Redis publish failed (alert still saved to DB): {e}")
