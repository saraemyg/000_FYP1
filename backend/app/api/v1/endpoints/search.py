"""Search API endpoints."""
import csv
import io
import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import SearchHistory, User
from app.schemas import (
    AdvancedSearchQuery,
    NaturalLanguageQuery,
    ParsedQuery,
    SearchHistoryItem,
    SearchResponse,
)
from app.services import get_nlp_parser, get_search_engine

router = APIRouter()


@router.post("/query", response_model=SearchResponse)
def natural_language_search(
    query: NaturalLanguageQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    """
    Search detections using natural language query.

    Args:
        query: Natural language query
        db: Database session
        current_user: Current authenticated user

    Returns:
        Search results
    """
    # Parse the query
    parser = get_nlp_parser()
    parsed = parser.parse_query(query.query)

    parsed_query = ParsedQuery(
        gender=parsed.get("gender"),
        upper_color=parsed.get("upper_color"),
        lower_color=parsed.get("lower_color"),
        raw_query=query.query,
    )

    # Execute search
    search_engine = get_search_engine(db)
    results, total_count = search_engine.search(
        gender=parsed.get("gender"),
        upper_color=parsed.get("upper_color"),
        lower_color=parsed.get("lower_color"),
        min_confidence=query.min_confidence,
        limit=query.limit,
        offset=query.offset,
    )

    # Save to search history
    history_entry = SearchHistory(
        user_id=current_user.user_id,
        query_text=query.query,
        parsed_attributes=parsed,
        result_count=total_count,
    )
    db.add(history_entry)
    db.commit()

    return SearchResponse(
        query=query.query,
        parsed_attributes=parsed_query,
        total_count=total_count,
        results=results,
    )


@router.post("/advanced", response_model=SearchResponse)
def advanced_search(
    query: AdvancedSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResponse:
    """
    Search detections using structured attribute filters.

    Args:
        query: Advanced search query with filters
        db: Database session
        current_user: Current authenticated user

    Returns:
        Search results
    """
    # Execute search
    search_engine = get_search_engine(db)
    results, total_count = search_engine.search_advanced(query)

    # Build query description for history
    query_parts = []
    if query.gender:
        query_parts.append(f"gender={query.gender}")
    if query.upper_color:
        query_parts.append(f"upper={query.upper_color}")
    if query.lower_color:
        query_parts.append(f"lower={query.lower_color}")
    query_text = ", ".join(query_parts) if query_parts else "all"

    parsed_query = ParsedQuery(
        gender=query.gender,
        upper_color=query.upper_color,
        lower_color=query.lower_color,
        raw_query=query_text,
    )

    # Save to search history
    history_entry = SearchHistory(
        user_id=current_user.user_id,
        query_text=query_text,
        parsed_attributes={
            "gender": query.gender,
            "upper_color": query.upper_color,
            "lower_color": query.lower_color,
            "min_confidence": query.min_confidence,
        },
        result_count=total_count,
    )
    db.add(history_entry)
    db.commit()

    return SearchResponse(
        query=query_text,
        parsed_attributes=parsed_query,
        total_count=total_count,
        results=results,
    )


@router.get("/history", response_model=list[SearchHistoryItem])
def get_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
) -> list[SearchHistory]:
    """
    Get user's search history.

    Args:
        db: Database session
        current_user: Current authenticated user
        limit: Maximum number of records

    Returns:
        List of search history items
    """
    history = (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.user_id)
        .order_by(SearchHistory.search_timestamp.desc())
        .limit(limit)
        .all()
    )

    return history


@router.delete("/history/{search_id}")
def delete_search_history_item(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Delete a search history item.

    Args:
        search_id: Search history ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Deletion confirmation
    """
    history_item = (
        db.query(SearchHistory)
        .filter(
            SearchHistory.search_id == search_id,
            SearchHistory.user_id == current_user.user_id,
        )
        .first()
    )

    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search history item not found",
        )

    db.delete(history_item)
    db.commit()

    return {"message": "Search history item deleted"}


@router.delete("/history")
def clear_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """
    Clear all search history for current user.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        Deletion confirmation
    """
    db.query(SearchHistory).filter(
        SearchHistory.user_id == current_user.user_id
    ).delete()
    db.commit()

    return {"message": "Search history cleared"}


@router.post("/export/json")
def export_search_results_json(
    query: AdvancedSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    UR8: Evidence Export - Export search results as JSON file.

    Args:
        query: Advanced search query with filters
        db: Database session
        current_user: Current authenticated user

    Returns:
        JSON file download
    """
    # Execute search with higher limit for export
    query.limit = min(query.limit, 1000)  # Cap at 1000 for export
    search_engine = get_search_engine(db)
    results, total_count = search_engine.search_advanced(query)

    # Build export data
    export_data = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "exported_by": current_user.username,
        "query_parameters": {
            "gender": query.gender,
            "upper_color": query.upper_color,
            "lower_color": query.lower_color,
            "min_confidence": query.min_confidence,
            "video_id": query.video_id,
            "start_timestamp": query.start_timestamp,
            "end_timestamp": query.end_timestamp,
        },
        "total_results": total_count,
        "results": [
            {
                "detection_id": r.detection_id,
                "video_id": r.video_id,
                "video_filename": r.video_filename,
                "frame_number": r.frame_number,
                "timestamp_in_video": r.timestamp_in_video,
                "bounding_box": {
                    "x": r.bbox_x,
                    "y": r.bbox_y,
                    "width": r.bbox_width,
                    "height": r.bbox_height,
                },
                "detection_confidence": r.detection_confidence,
                "attributes": {
                    "gender": r.gender,
                    "gender_confidence": r.gender_confidence,
                    "upper_color": r.upper_color,
                    "upper_color_confidence": r.upper_color_confidence,
                    "lower_color": r.lower_color,
                    "lower_color_confidence": r.lower_color_confidence,
                },
                "aggregate_confidence": r.aggregate_confidence,
            }
            for r in results
        ],
    }

    # Create JSON response
    json_content = json.dumps(export_data, indent=2)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.json"

    return StreamingResponse(
        io.BytesIO(json_content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/export/csv")
def export_search_results_csv(
    query: AdvancedSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    UR8: Evidence Export - Export search results as CSV file.

    Args:
        query: Advanced search query with filters
        db: Database session
        current_user: Current authenticated user

    Returns:
        CSV file download
    """
    # Execute search with higher limit for export
    query.limit = min(query.limit, 1000)  # Cap at 1000 for export
    search_engine = get_search_engine(db)
    results, total_count = search_engine.search_advanced(query)

    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Detection ID",
        "Video ID",
        "Video Filename",
        "Frame Number",
        "Timestamp (seconds)",
        "Bbox X",
        "Bbox Y",
        "Bbox Width",
        "Bbox Height",
        "Detection Confidence",
        "Gender",
        "Gender Confidence",
        "Upper Color",
        "Upper Color Confidence",
        "Lower Color",
        "Lower Color Confidence",
        "Aggregate Confidence",
    ])

    # Write data rows
    for r in results:
        writer.writerow([
            r.detection_id,
            r.video_id,
            r.video_filename,
            r.frame_number,
            round(r.timestamp_in_video, 2),
            r.bbox_x,
            r.bbox_y,
            r.bbox_width,
            r.bbox_height,
            round(r.detection_confidence, 3),
            r.gender or "",
            round(r.gender_confidence, 3) if r.gender_confidence else "",
            r.upper_color or "",
            round(r.upper_color_confidence, 3) if r.upper_color_confidence else "",
            r.lower_color or "",
            round(r.lower_color_confidence, 3) if r.lower_color_confidence else "",
            round(r.aggregate_confidence, 3),
        ])

    # Create response
    output.seek(0)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/detection/{detection_id}/metadata")
def export_detection_metadata(
    detection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    UR8: Evidence Export - Export metadata for a specific detection.

    Args:
        detection_id: Detection ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        JSON file with detection metadata
    """
    search_engine = get_search_engine(db)
    # Search for specific detection
    results, _ = search_engine.search(limit=1000)

    # Find the specific detection
    detection = None
    for r in results:
        if r.detection_id == detection_id:
            detection = r
            break

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    # Build metadata export
    export_data = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "exported_by": current_user.username,
        "detection": {
            "detection_id": detection.detection_id,
            "video_id": detection.video_id,
            "video_filename": detection.video_filename,
            "frame_number": detection.frame_number,
            "timestamp_in_video": detection.timestamp_in_video,
            "timestamp_formatted": f"{int(detection.timestamp_in_video // 60)}:{int(detection.timestamp_in_video % 60):02d}",
            "bounding_box": {
                "x": detection.bbox_x,
                "y": detection.bbox_y,
                "width": detection.bbox_width,
                "height": detection.bbox_height,
            },
            "detection_confidence": detection.detection_confidence,
            "attributes": {
                "gender": detection.gender,
                "gender_confidence": detection.gender_confidence,
                "upper_color": detection.upper_color,
                "upper_color_confidence": detection.upper_color_confidence,
                "lower_color": detection.lower_color,
                "lower_color_confidence": detection.lower_color_confidence,
            },
            "aggregate_confidence": detection.aggregate_confidence,
        },
    }

    json_content = json.dumps(export_data, indent=2)
    filename = f"detection_{detection_id}_metadata.json"

    return StreamingResponse(
        io.BytesIO(json_content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
