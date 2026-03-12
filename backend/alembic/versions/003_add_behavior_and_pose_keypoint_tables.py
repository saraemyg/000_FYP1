"""Add behaviors and pose_keypoints tables

Revision ID: 003
Revises: 002
Create Date: 2026-03-11 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── pose_keypoints ────────────────────────────────────────────────────────
    op.create_table(
        "pose_keypoints",
        sa.Column("keypoint_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("detection_id", sa.Integer(), nullable=False),
        sa.Column("keypoints_x",    postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("keypoints_y",    postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("keypoints_conf", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("keypoint_id"),
        sa.ForeignKeyConstraint(
            ["detection_id"], ["detections.detection_id"], ondelete="CASCADE"
        ),
    )
    op.create_index("idx_pose_keypoints_detection", "pose_keypoints", ["detection_id"])

    # ── behaviors ─────────────────────────────────────────────────────────────
    op.create_table(
        "behaviors",
        sa.Column("behavior_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("detection_id", sa.Integer(), nullable=False),
        sa.Column("behavior_type", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("raw_scores", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("behavior_id"),
        sa.ForeignKeyConstraint(
            ["detection_id"], ["detections.detection_id"], ondelete="CASCADE"
        ),
    )
    op.create_index("idx_behaviors_detection",     "behaviors", ["detection_id"])
    op.create_index("idx_behaviors_behavior_type", "behaviors", ["behavior_type"])
    op.create_index("idx_behaviors_created_at",    "behaviors", ["created_at"])


def downgrade() -> None:
    op.drop_table("behaviors")
    op.drop_table("pose_keypoints")
