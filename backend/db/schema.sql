-- ============================================================
-- AI Person Detection & Behavior Recognition System
-- Database Schema for PostgreSQL
-- Based on FYP1 Class Diagram (Figure 4.13) + Requirements
-- ============================================================

-- Run this file to create all tables:
--   psql -U postgres -d surveillance_db -f schema.sql

-- ============================================================
-- TABLE: users
-- Purpose: Login authentication + role-based access (UR1)
-- Roles: 'security_personnel' or 'admin'
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,          -- bcrypt hashed, NEVER store plain text
    role            VARCHAR(20) NOT NULL DEFAULT 'security_personnel'
                    CHECK (role IN ('security_personnel', 'admin')),
    full_name       VARCHAR(100),
    email           VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW(),
    last_login      TIMESTAMP
);

-- ============================================================
-- TABLE: cameras
-- Purpose: Registry of all surveillance cameras in the system
-- Links to: segmentation_masks, detections, alerts
-- ============================================================
CREATE TABLE IF NOT EXISTS cameras (
    id              SERIAL PRIMARY KEY,
    camera_id       VARCHAR(20) UNIQUE NOT NULL,    -- e.g., 'cam_01', 'cam_02'
    name            VARCHAR(100) NOT NULL,          -- e.g., 'Entrance Lobby'
    location        VARCHAR(200),                   -- e.g., 'Building A, Floor 1'
    video_path      VARCHAR(500),                   -- path to video file
    resolution_w    INTEGER,                        -- frame width in pixels
    resolution_h    INTEGER,                        -- frame height in pixels
    fps             FLOAT DEFAULT 30.0,             -- native video FPS
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: segmentation_masks
-- Purpose: Pre-computed DeepLabv3+ binary masks per camera
-- These define the walkable ROI area for each camera view
-- Generated OFFLINE, loaded ONCE at pipeline startup
-- ============================================================
CREATE TABLE IF NOT EXISTS segmentation_masks (
    id              SERIAL PRIMARY KEY,
    camera_id       INTEGER NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    mask_path       VARCHAR(500) NOT NULL,          -- path to .npy mask file
    crop_x1         INTEGER NOT NULL,               -- bounding rect of walkable area
    crop_y1         INTEGER NOT NULL,
    crop_x2         INTEGER NOT NULL,
    crop_y2         INTEGER NOT NULL,
    area_reduction  FLOAT,                          -- percentage of frame area removed (target: ≥40%)
    model_name      VARCHAR(50) DEFAULT 'deeplabv3plus',
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(camera_id)                               -- one mask per camera
);

-- ============================================================
-- TABLE: detections
-- Purpose: Every person detected in every processed frame
-- This is the highest-volume table — one row per person per frame
-- Indexed by timestamp + camera for fast dashboard queries
-- ============================================================
CREATE TABLE IF NOT EXISTS detections (
    id              SERIAL PRIMARY KEY,
    camera_id       INTEGER NOT NULL REFERENCES cameras(id),
    frame_number    INTEGER NOT NULL,
    timestamp       TIMESTAMP NOT NULL,             -- when this frame was captured
    person_idx      INTEGER NOT NULL,               -- person index within this frame (0, 1, 2...)
    bbox_x1         FLOAT NOT NULL,                 -- bounding box top-left x (original frame coords)
    bbox_y1         FLOAT NOT NULL,
    bbox_x2         FLOAT NOT NULL,                 -- bounding box bottom-right x
    bbox_y2         FLOAT NOT NULL,
    confidence      FLOAT NOT NULL,                 -- YOLO detection confidence (0.0 - 1.0)
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries (FR4: temporal filtering, FR5: multi-camera)
CREATE INDEX IF NOT EXISTS idx_detections_camera_ts ON detections(camera_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp);

-- ============================================================
-- TABLE: pose_keypoints
-- Purpose: 17 YOLO keypoints per detected person
-- Stored as arrays for compact storage
-- Keypoint order follows COCO format:
--   0:nose, 1:left_eye, 2:right_eye, 3:left_ear, 4:right_ear,
--   5:left_shoulder, 6:right_shoulder, 7:left_elbow, 8:right_elbow,
--   9:left_wrist, 10:right_wrist, 11:left_hip, 12:right_hip,
--   13:left_knee, 14:right_knee, 15:left_ankle, 16:right_ankle
-- ============================================================
CREATE TABLE IF NOT EXISTS pose_keypoints (
    id              SERIAL PRIMARY KEY,
    detection_id    INTEGER NOT NULL REFERENCES detections(id) ON DELETE CASCADE,
    keypoints_x     FLOAT[] NOT NULL,               -- array of 17 x-coordinates
    keypoints_y     FLOAT[] NOT NULL,               -- array of 17 y-coordinates
    keypoints_conf  FLOAT[] NOT NULL,               -- array of 17 confidence scores
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_keypoints_detection ON pose_keypoints(detection_id);

-- ============================================================
-- TABLE: behaviors
-- Purpose: Classified behavior label for each detection
-- One behavior per detection (the MLP output)
-- Labels: walking, standing, sitting, running, bending, falling, suspicious
-- ============================================================
CREATE TABLE IF NOT EXISTS behaviors (
    id              SERIAL PRIMARY KEY,
    detection_id    INTEGER NOT NULL REFERENCES detections(id) ON DELETE CASCADE,
    behavior_type   VARCHAR(30) NOT NULL,           -- e.g., 'walking', 'running', 'falling'
    confidence      FLOAT NOT NULL,                 -- MLP classification confidence
    raw_scores      JSONB,                          -- full softmax output for all classes (for analysis)
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_behaviors_detection ON behaviors(detection_id);
CREATE INDEX IF NOT EXISTS idx_behaviors_type ON behaviors(behavior_type);

-- ============================================================
-- TABLE: alert_criteria
-- Purpose: User-configurable rules that define when to generate alerts
-- Security personnel configure these via the web interface (UR3)
-- Matches Table 5.1 in the report
-- ============================================================
CREATE TABLE IF NOT EXISTS alert_criteria (
    id              SERIAL PRIMARY KEY,
    behavior_type   VARCHAR(30) NOT NULL,           -- which behavior triggers this rule
    min_confidence  FLOAT NOT NULL DEFAULT 0.7,     -- minimum confidence to trigger (0.5 - 0.9)
    priority        VARCHAR(10) NOT NULL DEFAULT 'MEDIUM'
                    CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),
    is_enabled      BOOLEAN DEFAULT TRUE,
    created_by      INTEGER REFERENCES users(id),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- TABLE: alerts
-- Purpose: Generated alerts when a detection matches an active rule
-- Alert lifecycle: PENDING → ACKNOWLEDGED → RESOLVED / FALSE_POSITIVE
-- This is what appears on the Alert Dashboard (FR3)
-- ============================================================
CREATE TABLE IF NOT EXISTS alerts (
    id              SERIAL PRIMARY KEY,
    detection_id    INTEGER NOT NULL REFERENCES detections(id),
    criteria_id     INTEGER NOT NULL REFERENCES alert_criteria(id),
    camera_id       INTEGER NOT NULL REFERENCES cameras(id),
    behavior_type   VARCHAR(30) NOT NULL,
    confidence      FLOAT NOT NULL,
    priority        VARCHAR(10) NOT NULL
                    CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                    CHECK (status IN ('PENDING', 'ACKNOWLEDGED', 'RESOLVED', 'FALSE_POSITIVE')),
    frame_snapshot  BYTEA,                          -- JPEG thumbnail of the frame (for alert card)
    timestamp       TIMESTAMP NOT NULL,             -- when the alert-triggering frame was captured
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    resolved_at     TIMESTAMP,
    notes           TEXT,                           -- operator notes when resolving
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for Alert History Dashboard (FR4: temporal filtering + sorting)
CREATE INDEX IF NOT EXISTS idx_alerts_camera_ts ON alerts(camera_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON alerts(priority);
CREATE INDEX IF NOT EXISTS idx_alerts_behavior ON alerts(behavior_type);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC);

-- ============================================================
-- TABLE: system_metrics
-- Purpose: Performance monitoring data for admin dashboard (UR5)
-- Logged periodically by the pipeline's metrics_logger
-- ============================================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id              SERIAL PRIMARY KEY,
    camera_id       INTEGER REFERENCES cameras(id),
    fps             FLOAT,                          -- current processing FPS
    avg_latency_ms  FLOAT,                          -- average per-frame processing time
    gpu_util        FLOAT,                          -- GPU utilization percentage
    gpu_memory_mb   FLOAT,                          -- GPU memory used in MB
    cpu_util        FLOAT,                          -- CPU utilization percentage
    detections_count INTEGER,                       -- number of persons detected in period
    alerts_count    INTEGER,                        -- number of alerts generated in period
    pipeline_status VARCHAR(20) DEFAULT 'RUNNING'   -- RUNNING, PAUSED, ERROR, STOPPED
                    CHECK (pipeline_status IN ('RUNNING', 'PAUSED', 'ERROR', 'STOPPED')),
    error_message   TEXT,                           -- if pipeline_status = ERROR
    recorded_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_camera_ts ON system_metrics(camera_id, recorded_at);

-- ============================================================
-- TABLE: processing_sessions
-- Purpose: Track each pipeline run (start/end time, total frames, etc.)
-- Useful for debugging and report generation
-- ============================================================
CREATE TABLE IF NOT EXISTS processing_sessions (
    id              SERIAL PRIMARY KEY,
    camera_id       INTEGER NOT NULL REFERENCES cameras(id),
    video_path      VARCHAR(500),
    started_at      TIMESTAMP DEFAULT NOW(),
    ended_at        TIMESTAMP,
    total_frames    INTEGER DEFAULT 0,
    processed_frames INTEGER DEFAULT 0,
    avg_fps         FLOAT,
    status          VARCHAR(20) DEFAULT 'RUNNING'
                    CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    error_message   TEXT
);
