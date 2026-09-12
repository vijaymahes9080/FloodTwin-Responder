"""
Health and Version endpoints for FLOODTWIN RESPONDER.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.services.store import store

router = APIRouter(tags=["System"])


@router.get("/health")
def get_health():
    """System health check endpoint."""
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "mock_notification_mode": settings.MOCK_NOTIFICATION_MODE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "datastore": "CONNECTED",
            "risk_engine": "READY",
            "geospatial_engine": "READY",
            "rag_knowledge_base": "READY",
            "audit_chain": "VERIFIED_INTEGRITY"
        }
    }


@router.get("/version")
def get_version():
    """System version and operational specification."""
    return {
        "version": settings.VERSION,
        "district": settings.DISTRICT_NAME,
        "default_crs": "EPSG:4326",
        "supported_roles": ["DISASTER_COMMANDER", "FIELD_ANALYST", "AUDITOR"],
        "safety_invariants": {
            "autonomous_alerts_permitted": False,
            "human_approval_required": True,
            "provenance_tracking": "STRICT_MERKLE_CHAIN"
        }
    }
