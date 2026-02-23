"""Performance metrics API endpoints.

UR9: Performance Transparency - Users shall be able to monitor system
performance metrics (FPS, detection counts, accuracy statistics) through
dashboard interface, enabling identification of performance issues or
configuration problems.
"""
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_db
from app.models import Attribute, Detection, PerformanceMetric, User, Video
from app.schemas import (
    ColorDistribution,
    GenderDistribution,
    MetricsDetail,
    MetricsSummary,
    VideoMetrics,
)

router = APIRouter()


@router.get("/summary", response_model=MetricsSummary)
def get_metrics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MetricsSummary:
    """
    Get overall system metrics summary.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Aggregated metrics summary
    """
    # Total videos
    total_videos = db.query(func.count(Video.video_id)).scalar() or 0

    # Total detections
    total_detections = db.query(func.count(Detection.detection_id)).scalar() or 0

    # Average FPS and processing time from performance metrics
    metrics_stats = db.query(
        func.avg(PerformanceMetric.avg_fps),
        func.avg(PerformanceMetric.area_reduction_percentage),
        func.sum(PerformanceMetric.processing_time_seconds),
    ).first()

    average_fps = metrics_stats[0] or 0.0
    average_area_reduction = metrics_stats[1] or 0.0
    total_processing_time = metrics_stats[2] or 0.0

    return MetricsSummary(
        total_videos=total_videos,
        total_detections=total_detections,
        average_fps=round(average_fps, 2),
        average_area_reduction=round(average_area_reduction, 2),
        total_processing_time=round(total_processing_time, 2),
    )


@router.get("/videos", response_model=list[VideoMetrics])
def get_video_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
) -> list[VideoMetrics]:
    """
    Get performance metrics per video.

    Args:
        db: Database session
        current_user: Current authenticated user
        limit: Maximum number of records

    Returns:
        List of video metrics
    """
    # Query videos with their metrics
    results = (
        db.query(Video, PerformanceMetric)
        .outerjoin(PerformanceMetric, Video.video_id == PerformanceMetric.video_id)
        .order_by(Video.upload_timestamp.desc())
        .limit(limit)
        .all()
    )

    video_metrics = []
    for video, metric in results:
        # Count detections for this video
        detection_count = (
            db.query(func.count(Detection.detection_id))
            .filter(Detection.video_id == video.video_id)
            .scalar() or 0
        )

        video_metrics.append(VideoMetrics(
            video_id=video.video_id,
            filename=video.filename,
            avg_fps=metric.avg_fps if metric else None,
            total_detections=detection_count,
            processing_time_seconds=metric.processing_time_seconds if metric else None,
            area_reduction_percentage=metric.area_reduction_percentage if metric else None,
            recorded_at=metric.recorded_at if metric else video.upload_timestamp,
        ))

    return video_metrics


@router.get("/attributes", response_model=MetricsDetail)
def get_attribute_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MetricsDetail:
    """
    Get attribute distribution metrics.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Detailed metrics with attribute distributions
    """
    # Get summary first
    summary = get_metrics_summary(db, current_user)

    # Gender distribution
    gender_counts = (
        db.query(Attribute.gender, func.count(Attribute.attribute_id))
        .filter(Attribute.gender.isnot(None))
        .group_by(Attribute.gender)
        .all()
    )

    gender_dist = {"male": 0, "female": 0, "unknown": 0}
    for gender, count in gender_counts:
        if gender in gender_dist:
            gender_dist[gender] = count

    # Upper color distribution (top 10)
    upper_colors = (
        db.query(Attribute.upper_color, func.count(Attribute.attribute_id))
        .filter(Attribute.upper_color.isnot(None))
        .group_by(Attribute.upper_color)
        .order_by(func.count(Attribute.attribute_id).desc())
        .limit(10)
        .all()
    )

    upper_color_dist = [
        ColorDistribution(color=color, count=count)
        for color, count in upper_colors
    ]

    # Lower color distribution (top 10)
    lower_colors = (
        db.query(Attribute.lower_color, func.count(Attribute.attribute_id))
        .filter(Attribute.lower_color.isnot(None))
        .group_by(Attribute.lower_color)
        .order_by(func.count(Attribute.attribute_id).desc())
        .limit(10)
        .all()
    )

    lower_color_dist = [
        ColorDistribution(color=color, count=count)
        for color, count in lower_colors
    ]

    return MetricsDetail(
        summary=summary,
        gender_distribution=GenderDistribution(**gender_dist),
        upper_color_distribution=upper_color_dist,
        lower_color_distribution=lower_color_dist,
    )


@router.get("/recent-activity")
def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
) -> list[dict]:
    """
    Get recent processing activity.

    Args:
        db: Database session
        current_user: Current authenticated user
        limit: Maximum number of records

    Returns:
        List of recent activity items
    """
    # Get recently processed videos
    recent_videos = (
        db.query(Video)
        .filter(Video.processing_status.in_(["completed", "processing", "failed"]))
        .order_by(Video.upload_timestamp.desc())
        .limit(limit)
        .all()
    )

    activities = []
    for video in recent_videos:
        # Get detection count
        detection_count = (
            db.query(func.count(Detection.detection_id))
            .filter(Detection.video_id == video.video_id)
            .scalar() or 0
        )

        # Get performance metric if available
        metric = (
            db.query(PerformanceMetric)
            .filter(PerformanceMetric.video_id == video.video_id)
            .first()
        )

        activities.append({
            "video_id": video.video_id,
            "filename": video.filename,
            "status": video.processing_status,
            "timestamp": video.upload_timestamp.isoformat(),
            "detection_count": detection_count,
            "processing_time": metric.processing_time_seconds if metric else None,
            "duration": video.duration_seconds,
        })

    return activities


@router.get("/processing-status")
def get_processing_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    UR9: Performance Transparency - Get real-time processing status for all videos.

    Returns current processing state including videos being processed,
    completed videos, and failed videos with detailed metrics.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Processing status summary with detailed metrics
    """
    # Get videos currently processing
    processing_videos = (
        db.query(Video)
        .filter(Video.processing_status == "processing")
        .all()
    )

    # Get recently completed videos (last 24 hours worth)
    completed_videos = (
        db.query(Video, PerformanceMetric)
        .outerjoin(PerformanceMetric, Video.video_id == PerformanceMetric.video_id)
        .filter(Video.processing_status == "completed")
        .order_by(Video.upload_timestamp.desc())
        .limit(10)
        .all()
    )

    # Get failed videos
    failed_videos = (
        db.query(Video)
        .filter(Video.processing_status == "failed")
        .order_by(Video.upload_timestamp.desc())
        .limit(5)
        .all()
    )

    # Build processing queue status
    processing_queue = []
    for video in processing_videos:
        detection_count = (
            db.query(func.count(Detection.detection_id))
            .filter(Detection.video_id == video.video_id)
            .scalar() or 0
        )
        processing_queue.append({
            "video_id": video.video_id,
            "filename": video.filename,
            "total_frames": video.total_frames,
            "duration_seconds": video.duration_seconds,
            "fps": video.fps,
            "resolution": video.resolution,
            "current_detections": detection_count,
            "upload_timestamp": video.upload_timestamp.isoformat() if video.upload_timestamp else None,
        })

    # Build completed list with performance metrics
    completed_list = []
    for video, metric in completed_videos:
        detection_count = (
            db.query(func.count(Detection.detection_id))
            .filter(Detection.video_id == video.video_id)
            .scalar() or 0
        )
        completed_list.append({
            "video_id": video.video_id,
            "filename": video.filename,
            "total_detections": detection_count,
            "avg_fps": metric.avg_fps if metric else None,
            "processing_time_seconds": metric.processing_time_seconds if metric else None,
            "area_reduction_percentage": metric.area_reduction_percentage if metric else None,
        })

    # Build failed list
    failed_list = [
        {
            "video_id": video.video_id,
            "filename": video.filename,
            "upload_timestamp": video.upload_timestamp.isoformat() if video.upload_timestamp else None,
        }
        for video in failed_videos
    ]

    return {
        "processing_count": len(processing_videos),
        "processing_queue": processing_queue,
        "recently_completed": completed_list,
        "failed_videos": failed_list,
        "system_status": "healthy" if len(processing_videos) < 5 else "busy",
    }


@router.get("/accuracy-stats")
def get_accuracy_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    UR9: Performance Transparency - Get accuracy statistics.

    Returns confidence score distributions and detection quality metrics.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Accuracy statistics
    """
    # Get confidence score statistics for detections
    detection_stats = db.query(
        func.avg(Detection.detection_confidence),
        func.min(Detection.detection_confidence),
        func.max(Detection.detection_confidence),
        func.count(Detection.detection_id),
    ).first()

    # Get confidence score statistics for attributes
    attribute_stats = db.query(
        func.avg(Attribute.gender_confidence),
        func.avg(Attribute.upper_color_confidence),
        func.avg(Attribute.lower_color_confidence),
    ).first()

    # Count detections by confidence range
    high_confidence = (
        db.query(func.count(Detection.detection_id))
        .filter(Detection.detection_confidence >= 0.8)
        .scalar() or 0
    )
    medium_confidence = (
        db.query(func.count(Detection.detection_id))
        .filter(Detection.detection_confidence >= 0.6, Detection.detection_confidence < 0.8)
        .scalar() or 0
    )
    low_confidence = (
        db.query(func.count(Detection.detection_id))
        .filter(Detection.detection_confidence < 0.6)
        .scalar() or 0
    )

    total_detections = detection_stats[3] or 0

    return {
        "detection_confidence": {
            "average": round(detection_stats[0], 3) if detection_stats[0] else 0,
            "minimum": round(detection_stats[1], 3) if detection_stats[1] else 0,
            "maximum": round(detection_stats[2], 3) if detection_stats[2] else 0,
            "total_count": total_detections,
        },
        "attribute_confidence": {
            "gender_average": round(attribute_stats[0], 3) if attribute_stats[0] else 0,
            "upper_color_average": round(attribute_stats[1], 3) if attribute_stats[1] else 0,
            "lower_color_average": round(attribute_stats[2], 3) if attribute_stats[2] else 0,
        },
        "confidence_distribution": {
            "high": high_confidence,  # >= 0.8
            "medium": medium_confidence,  # 0.6 - 0.8
            "low": low_confidence,  # < 0.6
            "high_percentage": round(high_confidence / total_detections * 100, 1) if total_detections > 0 else 0,
            "medium_percentage": round(medium_confidence / total_detections * 100, 1) if total_detections > 0 else 0,
            "low_percentage": round(low_confidence / total_detections * 100, 1) if total_detections > 0 else 0,
        },
    }


@router.get("/system-health")
def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """
    UR9: Performance Transparency - Get system health overview.

    Returns overall system health status including database connectivity,
    processing capacity, and performance metrics.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        System health status
    """
    # Check database connectivity (implicit - we're already connected)
    db_healthy = True

    # Count processing videos
    processing_count = (
        db.query(func.count(Video.video_id))
        .filter(Video.processing_status == "processing")
        .scalar() or 0
    )

    # Get average FPS from recent processing
    recent_fps = (
        db.query(func.avg(PerformanceMetric.avg_fps))
        .order_by(PerformanceMetric.recorded_at.desc())
        .limit(10)
        .scalar()
    )

    # Determine system status
    if processing_count > 5:
        status = "overloaded"
    elif processing_count > 2:
        status = "busy"
    else:
        status = "healthy"

    # Check FPS performance
    fps_status = "good" if (recent_fps and recent_fps >= 15) else "degraded" if recent_fps else "unknown"

    return {
        "overall_status": status,
        "database_connected": db_healthy,
        "processing_queue_size": processing_count,
        "recent_avg_fps": round(recent_fps, 2) if recent_fps else None,
        "fps_status": fps_status,
        "target_fps": 15,
        "checks": {
            "database": "pass" if db_healthy else "fail",
            "processing_capacity": "pass" if processing_count < 5 else "warning",
            "fps_performance": "pass" if fps_status == "good" else "warning" if fps_status == "degraded" else "unknown",
        },
    }
