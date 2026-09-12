"""
Flood Report ingestion and inspection endpoints for FLOODTWIN RESPONDER.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.core.auth import get_current_user
from backend.app.services.qc_engine import IngestionQCEngine
from backend.app.services.store import store

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportCreateInput(BaseModel):
    description: str = Field(..., description="Ground observation text")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude_m: Optional[float] = None
    reported_depth_cm: Optional[float] = Field(default=None, ge=0.0)
    water_flow: Optional[str] = "standing"
    source: Optional[str] = "CITIZEN_APP"
    image_url: Optional[str] = None
    timestamp: Optional[datetime] = None


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_report(
    payload: ReportCreateInput,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Submits a flood observation report.
    Executes bounds verification, duplicate detection, and automated PII scrubbing.
    """
    qc = IngestionQCEngine(existing_reports=list(store.reports.values()))
    report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
    ts = payload.timestamp or datetime.now(timezone.utc)

    qc_result = qc.process_report(
        report_id=report_id,
        raw_text=payload.description,
        lat=payload.latitude,
        lon=payload.longitude,
        timestamp=ts,
        source=payload.source or "CITIZEN_APP",
        reported_depth_cm=payload.reported_depth_cm,
        image_url=payload.image_url
    )

    if not qc_result["accepted"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "REPORT_VALIDATION_FAILED",
                "status": qc_result["status"],
                "reason": qc_result["reason"]
            }
        )

    # Construct report object
    report_record = {
        "id": report_id,
        "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
        "source": payload.source or "CITIZEN_APP",
        "data_category": "OBSERVED",
        "confidence": qc_result["confidence"],
        "coordinates": {
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "altitude_m": payload.altitude_m,
            "crs": "EPSG:4326"
        },
        "reported_depth_cm": payload.reported_depth_cm,
        "description": qc_result["sanitized_description"],
        "water_flow": payload.water_flow,
        "image_url": payload.image_url,
        "verification_status": qc_result["status"],
        "duplicate_of": qc_result["duplicate_of"],
        "version": "1.0.0",
        "provenance": {
            "source_system": "API_REPORT_INGEST",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "processing_pipeline": "QC-Pipeline-v1",
            "sanitization_applied": qc_result["sanitizations_applied"]
        }
    }

    # Store report and emit audit event
    store.add_report(report_record)
    store.record_audit(
        actor_id=current_user.get("id", "ANONYMOUS_CITIZEN"),
        actor_role=str(current_user.get("role", "CITIZEN")),
        action="REPORT_INGESTED",
        resource_type="REPORT",
        resource_id=report_id,
        details={
            "coordinates": [payload.latitude, payload.longitude],
            "status": qc_result["status"],
            "sanitizations": qc_result["sanitizations_applied"],
            "confidence": qc_result["confidence"]
        }
    )

    return report_record


@router.get("")
def list_reports(
    status_filter: Optional[str] = Query(None, description="Filter by verification_status"),
    source_filter: Optional[str] = Query(None, description="Filter by source"),
    include_duplicates: bool = Query(True, description="Whether to include duplicate reports")
):
    """Lists ingested flood reports with optional filters."""
    results = list(store.reports.values())
    if status_filter:
        results = [r for r in results if r.get("verification_status") == status_filter]
    if source_filter:
        results = [r for r in results if r.get("source") == source_filter]
    if not include_duplicates:
        results = [r for r in results if r.get("verification_status") != "LIKELY_DUPLICATE"]
    return {
        "count": len(results),
        "reports": results
    }


@router.get("/{report_id}")
def get_report(report_id: str):
    """Retrieves specific flood report by identifier."""
    if report_id not in store.reports:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' not found."
        )
    return store.reports[report_id]


@router.post("/transcribe-audio")
def transcribe_audio_report(audio_filename: str = Query("voice_note.wav")):
    """Whisper-compatible adapter endpoint for processing citizen voice notes."""
    result = IngestionQCEngine.mock_transcribe_audio(audio_filename)
    return result
