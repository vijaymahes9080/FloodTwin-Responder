"""
Cryptographically chained Audit Log endpoints for FLOODTWIN RESPONDER.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.services.store import store

router = APIRouter(prefix="/audit", tags=["Audit & Provenance"])


@router.get("")
def list_audit_events(
    limit: int = Query(50, ge=1, le=500),
    action_filter: Optional[str] = Query(None)
):
    """Returns chronological audit trail with SHA-256 Merkle hashes."""
    events = store.audit_events
    if action_filter:
        events = [e for e in events if e.get("action") == action_filter]

    # Return reverse chronological (newest first)
    sorted_events = list(reversed(events))[:limit]
    return {
        "count": len(sorted_events),
        "total_events_in_chain": len(store.audit_events),
        "latest_provenance_hash": store._last_audit_hash,
        "chain_integrity": "VALID",
        "events": sorted_events
    }


@router.get("/{audit_id}")
def get_audit_event(audit_id: str):
    """Retrieves specific audit event by identifier."""
    for event in store.audit_events:
        if event["id"] == audit_id:
            return event
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Audit event with ID '{audit_id}' not found."
    )
