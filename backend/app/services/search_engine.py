"""
Search engine for attribute-based person detection queries.

This module provides database search functionality based on parsed attributes.
"""
from typing import Optional

from sqlalchemy import and_, asc, desc, func
from sqlalchemy.orm import Session, joinedload

from app.models import Attribute, Detection, Video
from app.schemas.search import AdvancedSearchQuery, SearchResultItem
from loguru import logger


class SearchEngine:
    """Search engine for querying detections by attributes."""

    def __init__(self, db: Session) -> None:
        """
        Initialize search engine with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def search(
        self,
        gender: Optional[str] = None,
        upper_color: Optional[str] = None,
        lower_color: Optional[str] = None,
        min_confidence: float = 0.6,
        video_id: Optional[int] = None,
        start_timestamp: Optional[float] = None,
        end_timestamp: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "confidence",
        sort_order: str = "desc",
    ) -> tuple[list[SearchResultItem], int]:
        """
        Execute database search based on attributes.

        Args:
            gender: Filter by gender
            upper_color: Filter by upper clothing color
            lower_color: Filter by lower clothing color
            min_confidence: Minimum aggregate confidence threshold
            video_id: Filter by specific video
            start_timestamp: Filter by minimum timestamp
            end_timestamp: Filter by maximum timestamp
            limit: Maximum results to return
            offset: Number of results to skip
            sort_by: Sort field ('confidence' or 'timestamp')
            sort_order: Sort direction ('asc' or 'desc')

        Returns:
            Tuple of (list of SearchResultItem, total count)
        """
        logger.debug(
            f"Searching: gender={gender}, upper={upper_color}, "
            f"lower={lower_color}, min_conf={min_confidence}"
        )

        # Build base query
        query = (
            self.db.query(Detection, Attribute, Video)
            .join(Attribute, Detection.detection_id == Attribute.detection_id)
            .join(Video, Detection.video_id == Video.video_id)
        )

        # Apply filters
        filters = []

        if gender:
            filters.append(Attribute.gender == gender)

        if upper_color:
            filters.append(Attribute.upper_color == upper_color)

        if lower_color:
            filters.append(Attribute.lower_color == lower_color)

        if video_id:
            filters.append(Detection.video_id == video_id)

        if start_timestamp is not None:
            filters.append(Detection.timestamp_in_video >= start_timestamp)

        if end_timestamp is not None:
            filters.append(Detection.timestamp_in_video <= end_timestamp)

        # Apply confidence filter (computed from individual confidences)
        # FR9: Search Result Ranking - aggregate confidence is product of
        # detection confidence and attribute classification confidences
        # Using geometric mean of available confidences for balanced filtering
        filters.append(
            Detection.detection_confidence *
            func.coalesce(Attribute.upper_color_confidence, 1.0) *
            func.coalesce(Attribute.lower_color_confidence, 1.0) *
            func.coalesce(Attribute.gender_confidence, 1.0) >= min_confidence
        )

        if filters:
            query = query.filter(and_(*filters))

        # Get total count before pagination
        total_count = query.count()

        # Apply sorting
        # FR9: Sort by product of detection and attribute confidences
        if sort_by == "confidence":
            sort_expr = (
                Detection.detection_confidence *
                func.coalesce(Attribute.upper_color_confidence, 1.0) *
                func.coalesce(Attribute.lower_color_confidence, 1.0) *
                func.coalesce(Attribute.gender_confidence, 1.0)
            )
        else:  # timestamp
            sort_expr = Detection.timestamp_in_video

        if sort_order == "desc":
            query = query.order_by(desc(sort_expr))
        else:
            query = query.order_by(asc(sort_expr))

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        results = query.all()

        # Transform to response schema
        items = []
        for detection, attribute, video in results:
            # FR9: Aggregate confidence is product of detection and attribute confidences
            aggregate_conf = (
                detection.detection_confidence *
                (attribute.upper_color_confidence or 1.0) *
                (attribute.lower_color_confidence or 1.0) *
                (attribute.gender_confidence or 1.0)
            )

            items.append(SearchResultItem(
                detection_id=detection.detection_id,
                video_id=detection.video_id,
                video_filename=video.filename,
                frame_number=detection.frame_number,
                timestamp_in_video=detection.timestamp_in_video,
                bbox_x=detection.bbox_x,
                bbox_y=detection.bbox_y,
                bbox_width=detection.bbox_width,
                bbox_height=detection.bbox_height,
                detection_confidence=detection.detection_confidence,
                person_crop_path=detection.person_crop_path,
                upper_color=attribute.upper_color,
                upper_color_confidence=attribute.upper_color_confidence,
                lower_color=attribute.lower_color,
                lower_color_confidence=attribute.lower_color_confidence,
                gender=attribute.gender,
                gender_confidence=attribute.gender_confidence,
                aggregate_confidence=round(aggregate_conf, 3),
            ))

        logger.info(f"Search returned {len(items)} results (total: {total_count})")
        return items, total_count

    def search_advanced(self, query: AdvancedSearchQuery) -> tuple[list[SearchResultItem], int]:
        """
        Execute search using AdvancedSearchQuery schema.

        Args:
            query: AdvancedSearchQuery with all search parameters

        Returns:
            Tuple of (list of SearchResultItem, total count)
        """
        return self.search(
            gender=query.gender,
            upper_color=query.upper_color,
            lower_color=query.lower_color,
            min_confidence=query.min_confidence,
            video_id=query.video_id,
            start_timestamp=query.start_timestamp,
            end_timestamp=query.end_timestamp,
            limit=query.limit,
            offset=query.offset,
            sort_by=query.sort_by,
            sort_order=query.sort_order,
        )


def get_search_engine(db: Session) -> SearchEngine:
    """Create a search engine instance with the given database session."""
    return SearchEngine(db)
