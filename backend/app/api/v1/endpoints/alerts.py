"""Alert management API endpoints.

UR5: Reduced Monitoring Burden - Security operators shall be able to review
automated detection alerts rather than maintaining continuous vigilance
across multiple video feeds, reducing cognitive load and improving detection
of relevant events.
"""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models import AlertRule, TriggeredAlert, User, Video
from app.schemas import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    TriggeredAlertResponse,
    AlertStats,
)

router = APIRouter()


@router.get("/rules", response_model=list[AlertRuleResponse])
def list_alert_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    active_only: bool = Query(False, description="Filter to active rules only"),
) -> list[AlertRule]:
    """
    List all alert rules for the current user.

    Args:
        db: Database session
        current_user: Current authenticated user
        active_only: If True, only return active rules

    Returns:
        List of alert rules
    """
    query = db.query(AlertRule).filter(AlertRule.user_id == current_user.user_id)

    if active_only:
        query = query.filter(AlertRule.is_active == True)

    rules = query.order_by(AlertRule.created_at.desc()).all()
    return rules


@router.post("/rules", response_model=AlertRuleResponse)
def create_alert_rule(
    rule: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRule:
    """
    Create a new alert rule.

    Args:
        rule: Alert rule configuration
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created alert rule
    """
    # Validate that at least one filter criterion is specified
    if not any([rule.gender, rule.upper_color, rule.lower_color]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one attribute filter (gender, upper_color, lower_color) must be specified",
        )

    db_rule = AlertRule(
        user_id=current_user.user_id,
        name=rule.name,
        description=rule.description,
        gender=rule.gender,
        upper_color=rule.upper_color,
        lower_color=rule.lower_color,
        min_confidence=rule.min_confidence,
        is_active=rule.is_active,
        notify_on_match=rule.notify_on_match,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)

    return db_rule


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRule:
    """
    Get a specific alert rule by ID.

    Args:
        rule_id: Alert rule ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Alert rule details
    """
    rule = (
        db.query(AlertRule)
        .filter(AlertRule.rule_id == rule_id, AlertRule.user_id == current_user.user_id)
        .first()
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found",
        )

    return rule


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    rule_id: int,
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRule:
    """
    Update an existing alert rule.

    Args:
        rule_id: Alert rule ID
        rule_update: Updated rule configuration
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated alert rule
    """
    rule = (
        db.query(AlertRule)
        .filter(AlertRule.rule_id == rule_id, AlertRule.user_id == current_user.user_id)
        .first()
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found",
        )

    # Update fields if provided
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)

    return rule


@router.delete("/rules/{rule_id}")
def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Delete an alert rule.

    Args:
        rule_id: Alert rule ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Deletion confirmation
    """
    rule = (
        db.query(AlertRule)
        .filter(AlertRule.rule_id == rule_id, AlertRule.user_id == current_user.user_id)
        .first()
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found",
        )

    db.delete(rule)
    db.commit()

    return {"message": "Alert rule deleted successfully"}


@router.get("/triggered", response_model=list[TriggeredAlertResponse])
def list_triggered_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    unread_only: bool = Query(False, description="Filter to unread alerts only"),
    unacknowledged_only: bool = Query(False, description="Filter to unacknowledged alerts only"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    """
    List triggered alerts for the current user's rules.

    Args:
        db: Database session
        current_user: Current authenticated user
        unread_only: If True, only return unread alerts
        unacknowledged_only: If True, only return unacknowledged alerts
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of triggered alerts
    """
    query = (
        db.query(TriggeredAlert, AlertRule, Video)
        .join(AlertRule, TriggeredAlert.rule_id == AlertRule.rule_id)
        .join(Video, TriggeredAlert.video_id == Video.video_id)
        .filter(AlertRule.user_id == current_user.user_id)
    )

    if unread_only:
        query = query.filter(TriggeredAlert.is_read == False)

    if unacknowledged_only:
        query = query.filter(TriggeredAlert.is_acknowledged == False)

    results = (
        query
        .order_by(TriggeredAlert.triggered_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Transform to response format
    alerts = []
    for triggered, rule, video in results:
        alerts.append({
            "alert_id": triggered.alert_id,
            "rule_id": triggered.rule_id,
            "rule_name": rule.name,
            "detection_id": triggered.detection_id,
            "video_id": triggered.video_id,
            "video_filename": video.filename,
            "matched_attributes": triggered.matched_attributes,
            "confidence_score": triggered.confidence_score,
            "timestamp_in_video": triggered.timestamp_in_video,
            "is_read": triggered.is_read,
            "is_acknowledged": triggered.is_acknowledged,
            "acknowledged_by": triggered.acknowledged_by,
            "acknowledged_at": triggered.acknowledged_at,
            "triggered_at": triggered.triggered_at,
        })

    return alerts


@router.post("/triggered/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Mark an alert as read.

    Args:
        alert_id: Triggered alert ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Confirmation message
    """
    alert = (
        db.query(TriggeredAlert)
        .join(AlertRule, TriggeredAlert.rule_id == AlertRule.rule_id)
        .filter(TriggeredAlert.alert_id == alert_id, AlertRule.user_id == current_user.user_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert.is_read = True
    db.commit()

    return {"message": "Alert marked as read"}


@router.post("/triggered/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Acknowledge an alert.

    Args:
        alert_id: Triggered alert ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Confirmation message
    """
    alert = (
        db.query(TriggeredAlert)
        .join(AlertRule, TriggeredAlert.rule_id == AlertRule.rule_id)
        .filter(TriggeredAlert.alert_id == alert_id, AlertRule.user_id == current_user.user_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert.is_read = True
    alert.is_acknowledged = True
    alert.acknowledged_by = current_user.user_id
    alert.acknowledged_at = datetime.utcnow()
    db.commit()

    return {"message": "Alert acknowledged"}


@router.post("/triggered/mark-all-read")
def mark_all_alerts_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Mark all unread alerts as read.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Confirmation message with count
    """
    # Get user's rule IDs
    rule_ids = (
        db.query(AlertRule.rule_id)
        .filter(AlertRule.user_id == current_user.user_id)
        .all()
    )
    rule_ids = [r[0] for r in rule_ids]

    # Update all unread alerts
    count = (
        db.query(TriggeredAlert)
        .filter(TriggeredAlert.rule_id.in_(rule_ids), TriggeredAlert.is_read == False)
        .update({TriggeredAlert.is_read: True}, synchronize_session=False)
    )
    db.commit()

    return {"message": f"Marked {count} alerts as read"}


@router.get("/stats", response_model=AlertStats)
def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertStats:
    """
    Get alert statistics for the current user.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Alert statistics
    """
    # Count rules
    total_rules = (
        db.query(func.count(AlertRule.rule_id))
        .filter(AlertRule.user_id == current_user.user_id)
        .scalar() or 0
    )

    active_rules = (
        db.query(func.count(AlertRule.rule_id))
        .filter(AlertRule.user_id == current_user.user_id, AlertRule.is_active == True)
        .scalar() or 0
    )

    # Get user's rule IDs
    rule_ids = (
        db.query(AlertRule.rule_id)
        .filter(AlertRule.user_id == current_user.user_id)
        .all()
    )
    rule_ids = [r[0] for r in rule_ids]

    # Count triggered alerts
    total_triggered = 0
    unread_alerts = 0
    unacknowledged_alerts = 0

    if rule_ids:
        total_triggered = (
            db.query(func.count(TriggeredAlert.alert_id))
            .filter(TriggeredAlert.rule_id.in_(rule_ids))
            .scalar() or 0
        )

        unread_alerts = (
            db.query(func.count(TriggeredAlert.alert_id))
            .filter(TriggeredAlert.rule_id.in_(rule_ids), TriggeredAlert.is_read == False)
            .scalar() or 0
        )

        unacknowledged_alerts = (
            db.query(func.count(TriggeredAlert.alert_id))
            .filter(TriggeredAlert.rule_id.in_(rule_ids), TriggeredAlert.is_acknowledged == False)
            .scalar() or 0
        )

    return AlertStats(
        total_rules=total_rules,
        active_rules=active_rules,
        total_triggered=total_triggered,
        unread_alerts=unread_alerts,
        unacknowledged_alerts=unacknowledged_alerts,
    )
