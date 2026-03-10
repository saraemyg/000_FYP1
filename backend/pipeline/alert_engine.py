"""
Alert Generation Engine
========================
Checks classified behaviors against user-configured alert rules.
When a behavior matches a rule, creates an alert record.

Flow:
1. At startup: Load all active alert criteria from DB
2. Per frame: For each behavior → check against all active rules
3. If match → create Alert record → publish to Redis for real-time push

Cooldown prevents alert spam (e.g., same person running for 30 seconds 
shouldn't generate 450 alerts at 15fps).
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from collections import defaultdict

from db.database import get_db_session
from db.models import Alert, AlertCriteria
from pipeline.detector import PersonDetection
from pipeline.classifier import BehaviorResult
from config import settings

logger = logging.getLogger(__name__)


class AlertEngine:
    """
    Evaluates behaviors against alert rules and generates alerts.
    
    Usage:
        engine = AlertEngine()
        engine.load_rules()
        alerts = engine.evaluate(detections, behaviors, camera_db_id, timestamp, frame_snapshot)
    """

    def __init__(self):
        self.rules: List[dict] = []
        self._cooldown_tracker: Dict[str, datetime] = defaultdict(lambda: datetime.min)

    def load_rules(self):
        """Load active alert criteria from database."""
        with get_db_session() as db:
            criteria = db.query(AlertCriteria).filter_by(is_enabled=True).all()
            self.rules = [
                {
                    "id": c.id,
                    "behavior_type": c.behavior_type,
                    "min_confidence": c.min_confidence,
                    "priority": c.priority,
                }
                for c in criteria
            ]
        logger.info(f"Loaded {len(self.rules)} active alert rules")

    def evaluate(
        self,
        detections: List[PersonDetection],
        behaviors: List[BehaviorResult],
        detection_ids: List[int],
        camera_db_id: int,
        timestamp: datetime,
        frame_snapshot: Optional[bytes] = None,
    ) -> List[int]:
        """
        Check each behavior against alert rules.
        
        Returns: List of created alert IDs.
        """
        if not self.rules or not behaviors:
            return []

        created_alert_ids = []

        for det, beh, det_id in zip(detections, behaviors, detection_ids):
            if beh.behavior_type == "unknown":
                continue

            for rule in self.rules:
                # Check if behavior matches this rule
                if (
                    beh.behavior_type == rule["behavior_type"]
                    and beh.confidence >= rule["min_confidence"]
                ):
                    # Check cooldown — prevent alert spam
                    cooldown_key = f"{camera_db_id}_{det.person_idx}_{beh.behavior_type}"
                    last_alert_time = self._cooldown_tracker[cooldown_key]

                    if (timestamp - last_alert_time).total_seconds() < settings.ALERT_COOLDOWN_SECONDS:
                        continue  # still in cooldown period, skip

                    # Create alert
                    alert_id = self._create_alert(
                        detection_id=det_id,
                        criteria_id=rule["id"],
                        camera_db_id=camera_db_id,
                        behavior_type=beh.behavior_type,
                        confidence=beh.confidence,
                        priority=rule["priority"],
                        timestamp=timestamp,
                        frame_snapshot=frame_snapshot,
                    )

                    if alert_id:
                        created_alert_ids.append(alert_id)
                        self._cooldown_tracker[cooldown_key] = timestamp

                    break  # one alert per detection per frame is enough

        return created_alert_ids

    def _create_alert(
        self,
        detection_id: int,
        criteria_id: int,
        camera_db_id: int,
        behavior_type: str,
        confidence: float,
        priority: str,
        timestamp: datetime,
        frame_snapshot: Optional[bytes],
    ) -> Optional[int]:
        """Insert an alert record into the database."""
        try:
            with get_db_session() as db:
                alert = Alert(
                    detection_id=detection_id,
                    criteria_id=criteria_id,
                    camera_id=camera_db_id,
                    behavior_type=behavior_type,
                    confidence=confidence,
                    priority=priority,
                    status="PENDING",
                    frame_snapshot=frame_snapshot,
                    timestamp=timestamp,
                )
                db.add(alert)
                db.flush()
                alert_id = alert.id

            logger.info(
                f"🚨 Alert #{alert_id}: {behavior_type} "
                f"(conf={confidence:.2f}, priority={priority})"
            )

            # TODO: Publish to Redis pub/sub for real-time WebSocket push
            # self._publish_alert(alert_id)

            return alert_id

        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return None

    def reload_rules(self):
        """Reload rules from DB (call when user updates alert config via UI)."""
        self.load_rules()
