"""
Main Entry Point
==================
Run this to start processing surveillance videos.

Usage:
    python main.py                    # process all cameras in config
    python main.py --camera cam_01    # process one specific camera
    python main.py --init-db          # create database tables only
"""

import json
import logging
import argparse
import threading
from pathlib import Path

from config import settings
from db.database import init_db, get_db_session
from db.models import Camera
from models.model_loader import get_yolo_model, get_mlp_model
from pipeline.pipeline_runner import PipelineRunner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def load_camera_config() -> dict:
    """
    Load camera configuration from JSON file.
    
    Expected format:
    {
        "cam_01": {
            "name": "Entrance Lobby",
            "location": "Building A, Floor 1",
            "video_path": "data/entrance.mp4",
            "mask_path": "masks/cam_01_mask.npy"
        },
        "cam_02": { ... }
    }
    """
    config_path = Path(settings.CAMERA_CONFIG_PATH)
    if not config_path.exists():
        logger.error(f"Camera config not found: {config_path}")
        logger.info("Creating example camera_config.json...")
        example = {
            "cam_01": {
                "name": "Entrance Lobby",
                "location": "Building A, Floor 1",
                "video_path": "data/sample_video.mp4",
                "mask_path": "masks/cam_01_mask.npy"
            }
        }
        config_path.write_text(json.dumps(example, indent=2))
        return example

    with open(config_path) as f:
        return json.load(f)


def ensure_cameras_in_db(camera_config: dict) -> dict:
    """
    Make sure all cameras from config exist in the database.
    Returns: {camera_id_string: camera_db_id_integer}
    """
    camera_id_map = {}

    with get_db_session() as db:
        for cam_id, cam_info in camera_config.items():
            camera = db.query(Camera).filter_by(camera_id=cam_id).first()
            if not camera:
                camera = Camera(
                    camera_id=cam_id,
                    name=cam_info.get("name", cam_id),
                    location=cam_info.get("location", ""),
                    video_path=cam_info.get("video_path", ""),
                )
                db.add(camera)
                db.flush()
                logger.info(f"Registered camera: {cam_id} (DB id={camera.id})")

            camera_id_map[cam_id] = camera.id

    return camera_id_map


def run_pipeline_for_camera(
    camera_id: str,
    camera_config: dict,
    camera_db_id: int,
    yolo_model,
    mlp_model,
):
    """Run the pipeline for a single camera."""
    config = camera_config[camera_id]

    runner = PipelineRunner(
        camera_id=camera_id,
        video_path=config["video_path"],
        mask_path=config.get("mask_path", ""),
        camera_db_id=camera_db_id,
        yolo_model=yolo_model,
        mlp_model=mlp_model,
    )
    runner.run()


def main():
    parser = argparse.ArgumentParser(description="AI Surveillance Pipeline")
    parser.add_argument("--camera", type=str, help="Process specific camera only")
    parser.add_argument("--init-db", action="store_true", help="Initialize database tables")
    args = parser.parse_args()

    # Initialize database
    if args.init_db:
        init_db()
        from db.seed import seed
        seed()
        return

    # Always ensure tables exist
    init_db()

    # Load camera config
    camera_config = load_camera_config()
    camera_id_map = ensure_cameras_in_db(camera_config)

    # Filter to specific camera if requested
    if args.camera:
        if args.camera not in camera_config:
            logger.error(f"Camera '{args.camera}' not found in config")
            return
        cameras_to_process = {args.camera: camera_config[args.camera]}
    else:
        cameras_to_process = camera_config

    # Load AI models ONCE (shared across all camera threads)
    logger.info("Loading AI models...")
    yolo_model = get_yolo_model()
    mlp_model = get_mlp_model()
    logger.info("Models loaded ✓")

    # Process cameras
    if len(cameras_to_process) == 1:
        # Single camera — run in main thread
        cam_id = list(cameras_to_process.keys())[0]
        run_pipeline_for_camera(
            cam_id, camera_config, camera_id_map[cam_id],
            yolo_model, mlp_model,
        )
    else:
        # Multiple cameras — run in separate threads
        threads = []
        for cam_id in cameras_to_process:
            t = threading.Thread(
                target=run_pipeline_for_camera,
                args=(cam_id, camera_config, camera_id_map[cam_id], yolo_model, mlp_model),
                name=f"pipeline-{cam_id}",
            )
            threads.append(t)
            t.start()
            logger.info(f"Started thread for {cam_id}")

        # Wait for all threads to finish
        for t in threads:
            t.join()

    logger.info("All pipelines complete.")


if __name__ == "__main__":
    main()
