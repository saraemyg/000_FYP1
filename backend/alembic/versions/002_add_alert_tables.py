"""Add alert tables for UR5: Reduced Monitoring Burden

Revision ID: 002
Revises: 001
Create Date: 2024-02-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create alert_rules table
    op.create_table(
        "alert_rules",
        sa.Column("rule_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("upper_color", sa.String(50), nullable=True),
        sa.Column("lower_color", sa.String(50), nullable=True),
        sa.Column("min_confidence", sa.Float(), default=0.7),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("notify_on_match", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("rule_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
    )
    op.create_index("idx_alert_rules_user", "alert_rules", ["user_id"])
    op.create_index("idx_alert_rules_active", "alert_rules", ["is_active"])

    # Create triggered_alerts table
    op.create_table(
        "triggered_alerts",
        sa.Column("alert_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column("detection_id", sa.Integer(), nullable=False),
        sa.Column("video_id", sa.Integer(), nullable=False),
        sa.Column("matched_attributes", postgresql.JSONB(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("timestamp_in_video", sa.Float(), nullable=True),
        sa.Column("is_read", sa.Boolean(), default=False),
        sa.Column("is_acknowledged", sa.Boolean(), default=False),
        sa.Column("acknowledged_by", sa.Integer(), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("triggered_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("alert_id"),
        sa.ForeignKeyConstraint(["rule_id"], ["alert_rules.rule_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["detection_id"], ["detections.detection_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.video_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["acknowledged_by"], ["users.user_id"]),
    )
    op.create_index("idx_triggered_alerts_rule", "triggered_alerts", ["rule_id"])
    op.create_index("idx_triggered_alerts_detection", "triggered_alerts", ["detection_id"])
    op.create_index("idx_triggered_alerts_read", "triggered_alerts", ["is_read"])
    op.create_index("idx_triggered_alerts_acknowledged", "triggered_alerts", ["is_acknowledged"])


def downgrade() -> None:
    op.drop_table("triggered_alerts")
    op.drop_table("alert_rules")
