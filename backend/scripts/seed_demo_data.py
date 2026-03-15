"""
Seed realistic demo data into PostgreSQL for frontend integration testing.

Run from backend/ directory:
    python scripts/seed_demo_data.py
    python scripts/seed_demo_data.py --clear    # wipe existing data first
    python scripts/seed_demo_data.py --scale large  # bigger dataset

What it generates:
    - 2 users      (admin + security)
    - 4 cameras
    - 8 videos     (2 per camera, different days)
    - ~6000 detections  spread across 7 days
    - ~6000 behaviors   one per detection
    - ~6000 pose_keypoints
    - ~480 triggered_alerts (realistic distribution, mixed status)
    - 8 performance_metrics (one per video)
    - 7 alert_rules (one per behavior class)
"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta

# ── path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Must override DATABASE_URL BEFORE importing anything from app.db
# because session.py reads it at import time via pydantic settings.
# When running locally (not inside Docker), the DB host is localhost, not "db".
_LOCAL_DB = "postgresql://surveillance_user:secure_password@localhost:5432/surveillance_db"
_early = argparse.ArgumentParser(add_help=False)
_early.add_argument("--db-url", default=None)
_early_args, _ = _early.parse_known_args()
_db_url = _early_args.db_url or os.environ.get("DATABASE_URL") or _LOCAL_DB
os.environ["DATABASE_URL"] = _db_url
print(f"Connecting to: {_db_url[:60]}...")

from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.camera import Camera
from app.models.video import Video
from app.models.detection import Detection
from app.models.behavior import Behavior
from app.models.pose_keypoint import PoseKeypoint
from app.models.alert import AlertRule, TriggeredAlert
from app.models.performance import PerformanceMetric

# ── config ────────────────────────────────────────────────────────────────────
random.seed(42)

BEHAVIOR_CLASSES   = ["walking", "standing", "sitting", "running", "bending", "falling", "suspicious"]
BEHAVIOR_WEIGHTS   = [0.35, 0.28, 0.12, 0.08, 0.07, 0.04, 0.06]   # realistic CCTV distribution
UPPER_COLORS       = ["black", "white", "grey", "blue", "red", "green", "yellow"]
LOWER_COLORS       = ["black", "blue", "grey", "brown", "white"]
GENDERS            = ["male", "female"]

CAMERA_DEFS = [
    {"camera_name": "Entrance Lobby",      "location": "Main Building — Ground Floor", "resolution": "1920x1080", "fps": 30.0},
    {"camera_name": "Parking Lot A",       "location": "Outdoor West",                 "resolution": "1280x720",  "fps": 25.0},
    {"camera_name": "Corridor B2",         "location": "Block B — Level 2",            "resolution": "1920x1080", "fps": 30.0},
    {"camera_name": "Emergency Exit North","location": "North Wing",                   "resolution": "1280x720",  "fps": 25.0},
]

VIDEO_DEFS_PER_CAMERA = [
    {"suffix": "morning",   "duration": 3600, "fps": 30.0, "total_frames": 108000},
    {"suffix": "afternoon", "duration": 3600, "fps": 30.0, "total_frames": 108000},
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--clear", action="store_true", help="Delete all seeded data before inserting")
    p.add_argument("--scale", choices=["small", "medium", "large"], default="medium")
    p.add_argument("--db-url", default=None, help="Override DATABASE_URL (default: localhost:5432)")
    return p.parse_args()


def rnd_conf(low=0.55, high=0.99):
    return round(random.uniform(low, high), 4)


def rnd_keypoints(bbox_x, bbox_y, bbox_w, bbox_h):
    """Generate plausible COCO-17 keypoints inside a bounding box."""
    kx, ky, kc = [], [], []
    for _ in range(17):
        kx.append(round(bbox_x + random.uniform(0.1, 0.9) * bbox_w, 2))
        ky.append(round(bbox_y + random.uniform(0.1, 0.9) * bbox_h, 2))
        kc.append(round(random.uniform(0.4, 0.99), 3))
    return kx, ky, kc


def rnd_raw_scores(winner_idx):
    scores = [round(random.uniform(0.01, 0.1), 4) for _ in BEHAVIOR_CLASSES]
    scores[winner_idx] = round(random.uniform(0.55, 0.95), 4)
    total = sum(scores)
    return {cls: round(s / total, 4) for cls, s in zip(BEHAVIOR_CLASSES, scores)}


def clear_data(db):
    print("Clearing existing demo data...")
    db.query(TriggeredAlert).delete()
    db.query(PerformanceMetric).delete()
    db.query(PoseKeypoint).delete()
    db.query(Behavior).delete()
    db.query(Detection).delete()
    db.query(AlertRule).delete()
    db.query(Video).delete()
    db.query(Camera).delete()
    db.commit()
    print("  Done.")


def seed(db, scale: str):
    det_count = {"small": 1500, "medium": 6000, "large": 15000}[scale]

    # ── Users ─────────────────────────────────────────────────────────────────
    print("Seeding users...")
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(username="admin", email="admin@surveillance.dev",
                     password_hash=get_password_hash("admin123"), role="admin", is_active=True)
        db.add(admin)
    security = db.query(User).filter(User.username == "security").first()
    if not security:
        security = User(username="security", email="security@surveillance.dev",
                        password_hash=get_password_hash("security123"), role="security_personnel", is_active=True)
        db.add(security)
    db.flush()
    admin_id    = admin.user_id
    security_id = security.user_id

    # ── Cameras ───────────────────────────────────────────────────────────────
    print("Seeding cameras...")
    cameras = []
    for cam_def in CAMERA_DEFS:
        existing = db.query(Camera).filter(Camera.camera_name == cam_def["camera_name"]).first()
        if existing:
            cameras.append(existing)
            continue
        cam = Camera(**cam_def, is_active=True)
        db.add(cam)
        db.flush()
        cameras.append(cam)

    # ── Alert Rules (one per behavior class) ──────────────────────────────────
    print("Seeding alert rules...")
    priorities = {"falling": 0.5, "suspicious": 0.6, "running": 0.65,
                  "bending": 0.7, "walking": 0.75, "standing": 0.8, "sitting": 0.8}
    rules = []
    for behavior in BEHAVIOR_CLASSES:
        existing = db.query(AlertRule).filter(AlertRule.name.ilike(f"%{behavior}%")).first()
        if existing:
            rules.append(existing)
            continue
        rule = AlertRule(
            user_id=admin_id,
            name=f"{behavior.title()} Detection Alert",
            description=f"Trigger alert when {behavior} behavior is detected",
            min_confidence=priorities[behavior],
            is_active=True,
            notify_on_match=True,
        )
        db.add(rule)
        db.flush()
        rules.append(rule)

    # ── Videos (2 per camera, spanning 7 days) ────────────────────────────────
    print("Seeding videos...")
    videos = []
    base_date = datetime.utcnow() - timedelta(days=7)
    for cam_idx, cam in enumerate(cameras):
        for day_offset in range(2):
            vid_date = base_date + timedelta(days=cam_idx + day_offset)
            suffix = VIDEO_DEFS_PER_CAMERA[day_offset]["suffix"]
            filename = f"cam{cam.camera_id:02d}_{vid_date.strftime('%Y%m%d')}_{suffix}.mp4"
            existing = db.query(Video).filter(Video.filename == filename).first()
            if existing:
                videos.append((existing, cam))
                continue
            vid = Video(
                filename=filename,
                file_path=f"/app/uploads/{filename}",
                duration_seconds=VIDEO_DEFS_PER_CAMERA[day_offset]["duration"],
                fps=VIDEO_DEFS_PER_CAMERA[day_offset]["fps"],
                resolution=cam.resolution,
                total_frames=VIDEO_DEFS_PER_CAMERA[day_offset]["total_frames"],
                processing_status="completed",
                uploaded_by=admin_id,
                upload_timestamp=vid_date,
            )
            db.add(vid)
            db.flush()
            videos.append((vid, cam))

    # ── Performance Metrics (one per video) ───────────────────────────────────
    print("Seeding performance metrics...")
    for vid, cam in videos:
        existing = db.query(PerformanceMetric).filter(PerformanceMetric.video_id == vid.video_id).first()
        if existing:
            continue
        pm = PerformanceMetric(
            video_id=vid.video_id,
            avg_fps=round(random.uniform(14.5, 18.2), 2),
            total_detections=random.randint(400, 900),
            processing_time_seconds=round(random.uniform(3500, 4200), 1),
            area_reduction_percentage=round(random.uniform(40, 68), 1),
        )
        db.add(pm)
    db.commit()

    # ── Detections + Behaviors + Keypoints ────────────────────────────────────
    print(f"Seeding {det_count} detections (+ behaviors + keypoints)...")
    resolutions = {v.filename: v.resolution for v, _ in videos}

    alert_candidates = []   # (det_id, rule, confidence, vid_id, ts) — collected for alert seeding

    BATCH = 200
    dets_inserted = 0

    for batch_start in range(0, det_count, BATCH):
        batch_size = min(BATCH, det_count - batch_start)

        for _ in range(batch_size):
            vid, cam = random.choice(videos)
            res = vid.resolution or "1920x1080"
            W, H = (int(x) for x in res.split("x"))

            frame_num   = random.randint(1, vid.total_frames or 108000)
            ts_in_video = round(frame_num / (vid.fps or 30.0), 3)

            bw = random.randint(60, 180)
            bh = random.randint(120, 360)
            bx = random.randint(0, max(0, W - bw))
            by = random.randint(0, max(0, H - bh))
            conf = rnd_conf()

            det = Detection(
                video_id=vid.video_id,
                frame_number=frame_num,
                timestamp_in_video=ts_in_video,
                bbox_x=bx, bbox_y=by,
                bbox_width=bw, bbox_height=bh,
                detection_confidence=conf,
            )
            db.add(det)
            db.flush()

            # Behavior
            beh_idx  = random.choices(range(len(BEHAVIOR_CLASSES)), weights=BEHAVIOR_WEIGHTS)[0]
            beh_type = BEHAVIOR_CLASSES[beh_idx]
            beh_conf = rnd_conf(0.52, 0.97)
            beh = Behavior(
                detection_id=det.detection_id,
                behavior_type=beh_type,
                confidence=beh_conf,
                raw_scores=rnd_raw_scores(beh_idx),
            )
            db.add(beh)

            # Pose keypoints
            kx, ky, kc = rnd_keypoints(bx, by, bw, bh)
            kp = PoseKeypoint(
                detection_id=det.detection_id,
                keypoints_x=kx,
                keypoints_y=ky,
                keypoints_conf=kc,
            )
            db.add(kp)

            # Collect candidates for alert seeding (all 7 behavior types)
            if beh_conf > 0.65:
                matching_rules = [r for r in rules if beh_type in r.name.lower() and r.is_active]
                if matching_rules:
                    alert_candidates.append((det.detection_id, matching_rules[0], beh_conf, vid.video_id, ts_in_video))

            dets_inserted += 1

        db.commit()
        print(f"  {dets_inserted}/{det_count} detections...", end="\r")

    print(f"\n  Done: {dets_inserted} detections inserted.")

    # ── Triggered Alerts ──────────────────────────────────────────────────────
    # Seed ~480 alerts from candidates, with mixed status
    print("Seeding triggered alerts...")
    random.shuffle(alert_candidates)
    n_alerts = min(len(alert_candidates), {"small": 80, "medium": 480, "large": 1200}[scale])
    alert_candidates = alert_candidates[:n_alerts]

    now = datetime.utcnow()
    for i, (det_id, rule, beh_conf, vid_id, ts_in_vid) in enumerate(alert_candidates):
        triggered_at = now - timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        # Realistic status distribution:
        # 30% unread, 40% read+unacknowledged, 30% acknowledged
        r = random.random()
        is_read         = r > 0.30
        is_acknowledged = r > 0.70
        ack_by          = security_id if is_acknowledged else None
        ack_at          = triggered_at + timedelta(minutes=random.randint(5, 60)) if is_acknowledged else None

        alert = TriggeredAlert(
            rule_id=rule.rule_id,
            detection_id=det_id,
            video_id=vid_id,
            matched_attributes={"behavior_type": rule.name.lower().split()[0]},
            confidence_score=beh_conf,
            timestamp_in_video=ts_in_vid,
            is_read=is_read,
            is_acknowledged=is_acknowledged,
            acknowledged_by=ack_by,
            acknowledged_at=ack_at,
            triggered_at=triggered_at,
        )
        db.add(alert)

        if (i + 1) % 50 == 0:
            db.commit()

    db.commit()
    print(f"  {n_alerts} alerts inserted.")


def main():
    args = parse_args()

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.clear:
            clear_data(db)
        seed(db, scale=args.scale)
        print("\n✓ Seed complete. Summary:")
        print(f"  Users:        {db.query(User).count()}")
        print(f"  Cameras:      {db.query(Camera).count()}")
        print(f"  Videos:       {db.query(Video).count()}")
        print(f"  Detections:   {db.query(Detection).count()}")
        print(f"  Behaviors:    {db.query(Behavior).count()}")
        print(f"  PoseKeypoints:{db.query(PoseKeypoint).count()}")
        print(f"  AlertRules:   {db.query(AlertRule).count()}")
        print(f"  Alerts:       {db.query(TriggeredAlert).count()}")
        print(f"  PerfMetrics:  {db.query(PerformanceMetric).count()}")
        print()
        print("Login credentials:")
        print("  admin    / admin123")
        print("  security / security123")
    except Exception as e:
        db.rollback()
        print(f"\n✗ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
