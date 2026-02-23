"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    # Create videos table
    op.create_table(
        "videos",
        sa.Column("video_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("upload_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("resolution", sa.String(20), nullable=True),
        sa.Column("total_frames", sa.Integer(), nullable=True),
        sa.Column("processing_status", sa.String(20), default="uploaded"),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("video_id"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.user_id"]),
    )

    # Create cameras table
    op.create_table(
        "cameras",
        sa.Column("camera_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("camera_name", sa.String(100), nullable=False),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("resolution", sa.String(20), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("mask_file_path", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("camera_id"),
    )

    # Create detections table
    op.create_table(
        "detections",
        sa.Column("detection_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("video_id", sa.Integer(), nullable=False),
        sa.Column("frame_number", sa.Integer(), nullable=False),
        sa.Column("timestamp_in_video", sa.Float(), nullable=False),
        sa.Column("bbox_x", sa.Integer(), nullable=False),
        sa.Column("bbox_y", sa.Integer(), nullable=False),
        sa.Column("bbox_width", sa.Integer(), nullable=False),
        sa.Column("bbox_height", sa.Integer(), nullable=False),
        sa.Column("detection_confidence", sa.Float(), nullable=False),
        sa.Column("person_crop_path", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("detection_id"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.video_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("video_id", "frame_number", "bbox_x", "bbox_y", name="uq_detection_location"),
    )
    op.create_index("idx_detections_video", "detections", ["video_id"])
    op.create_index("idx_detections_timestamp", "detections", ["timestamp_in_video"])

    # Create attributes table
    op.create_table(
        "attributes",
        sa.Column("attribute_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("detection_id", sa.Integer(), nullable=False),
        sa.Column("upper_color", sa.String(20), nullable=True),
        sa.Column("upper_color_confidence", sa.Float(), nullable=True),
        sa.Column("lower_color", sa.String(20), nullable=True),
        sa.Column("lower_color_confidence", sa.Float(), nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("gender_confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("attribute_id"),
        sa.ForeignKeyConstraint(["detection_id"], ["detections.detection_id"], ondelete="CASCADE"),
    )
    op.create_index("idx_attributes_detection", "attributes", ["detection_id"])
    op.create_index("idx_attributes_upper_color", "attributes", ["upper_color"])
    op.create_index("idx_attributes_lower_color", "attributes", ["lower_color"])
    op.create_index("idx_attributes_gender", "attributes", ["gender"])

    # Create segmentation_masks table
    op.create_table(
        "segmentation_masks",
        sa.Column("mask_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("camera_id", sa.Integer(), nullable=True),
        sa.Column("mask_file_path", sa.String(500), nullable=False),
        sa.Column("reduction_percentage", sa.Float(), nullable=True),
        sa.Column("generation_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("sample_frame_path", sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint("mask_id"),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.camera_id"]),
    )

    # Create performance_metrics table
    op.create_table(
        "performance_metrics",
        sa.Column("metric_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("video_id", sa.Integer(), nullable=True),
        sa.Column("avg_fps", sa.Float(), nullable=True),
        sa.Column("total_detections", sa.Integer(), nullable=True),
        sa.Column("processing_time_seconds", sa.Float(), nullable=True),
        sa.Column("area_reduction_percentage", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("metric_id"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.video_id"]),
    )

    # Create search_history table
    op.create_table(
        "search_history",
        sa.Column("search_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("parsed_attributes", postgresql.JSONB(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True),
        sa.Column("search_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("search_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
    )
    op.create_index("idx_search_user", "search_history", ["user_id"])


def downgrade() -> None:
    op.drop_table("search_history")
    op.drop_table("performance_metrics")
    op.drop_table("segmentation_masks")
    op.drop_table("attributes")
    op.drop_table("detections")
    op.drop_table("cameras")
    op.drop_table("videos")
    op.drop_table("users")
