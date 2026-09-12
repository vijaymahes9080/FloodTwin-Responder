"""
Response Brief and Human-in-the-Loop Approval endpoints for FLOODTWIN RESPONDER.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from agent.response_fsm import BoundedResponseAgent
from backend.app.core.auth import UserRole, get_current_user, require_role
from backend.app.core.config import settings
from backend.app.schemas.contracts import ApprovalStatus
from backend.app.services.store import store
from geospatial.spatial_engine import SpatialEngine
from rag.knowledge_base import PolicyKnowledgeBase
from risk_engine import FloodRiskEngine

router = APIRouter(prefix="/response-briefs", tags=["Response Briefs"])

spatial_engine = SpatialEngine(admin_boundaries=store.administrative_boundaries)
risk_engine = FloodRiskEngine()
knowledge_base = PolicyKnowledgeBase()
agent = BoundedResponseAgent(
    risk_engine=risk_engine,
    spatial_engine=spatial_engine,
    knowledge_base=knowledge_base
)


class GenerateBriefInput(BaseModel):
    zone_id: str = Field(default="ZONE_02_SOUTH")
    zone_name: Optional[str] = "South Chennai - Adyar Basin"
    latitude: Optional[float] = 13.018
    longitude: Optional[float] = 80.222


class DecisionInput(BaseModel):
    operator_comments: str = Field(..., min_length=3, description="Operational justification from human commander")


@router.post("", status_code=status.HTTP_201_CREATED)
def generate_response_brief(
    payload: GenerateBriefInput,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Synthesizes a response brief via the deterministic 8-state Bounded Response Agent.
    Strictly marked PENDING_HUMAN_APPROVAL.
    """
    # Collect zone context from data store
    zone_coords = {"latitude": payload.latitude or 13.018, "longitude": payload.longitude or 80.222}

    # Find relevant sensors and rainfall
    sensor_entry = store.sensors.get("SENSOR_ADYAR_SAIDAPET", list(store.sensors.values())[0] if store.sensors else None)
    rain_entry = store.rainfall_stations.get("AWS_MEENAMBAKKAM", list(store.rainfall_stations.values())[0] if store.rainfall_stations else None)

    # Filter reports for target zone
    zone_reports = list(store.reports.values())[:5]

    brief = agent.execute_workflow(
        target_zone_id=payload.zone_id,
        target_zone_name=payload.zone_name or "Chennai Flood Basin",
        zone_coords=zone_coords,
        rainfall_data=rain_entry,
        sensor_data=sensor_entry,
        citizen_reports=zone_reports,
        critical_assets=store.critical_assets,
        shelters=store.shelters,
        elevation_m=4.5
    )

    brief_dict = brief.model_dump()
    store.add_response_brief(brief_dict)

    store.record_audit(
        actor_id=current_user.get("id", "AGENT_SYSTEM"),
        actor_role=str(current_user.get("role", "SYSTEM_AGENT")),
        action="RESPONSE_BRIEF_GENERATED",
        resource_type="RESPONSE_BRIEF",
        resource_id=brief.id,
        details={
            "zone_id": payload.zone_id,
            "risk_score": brief.current_risk_score,
            "citations_count": len(brief.policy_citations),
            "approval_status": brief.approval_status.value
        }
    )

    return brief_dict


@router.get("")
def list_response_briefs():
    """Lists all response briefs and their approval status."""
    briefs = list(store.response_briefs.values())
    return {
        "count": len(briefs),
        "response_briefs": briefs
    }


@router.get("/{brief_id}")
def get_response_brief(brief_id: str):
    """Retrieves specific response brief with policy citations and evidence trail."""
    if brief_id not in store.response_briefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response brief '{brief_id}' not found."
        )
    return store.response_briefs[brief_id]


@router.post("/{brief_id}/approve")
def approve_response_brief(
    brief_id: str,
    payload: DecisionInput,
    current_user: Dict[str, Any] = Depends(require_role([UserRole.DISASTER_COMMANDER]))
):
    """
    Mandatory Human Approval Gate:
    Authorizes response brief and triggers mock simulation dispatch.
    Requires role DISASTER_COMMANDER.
    """
    if brief_id not in store.response_briefs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found.")

    brief = store.response_briefs[brief_id]
    brief["approval_status"] = ApprovalStatus.APPROVED.value
    brief["approved_by"] = current_user.get("name")
    brief["approved_by_id"] = current_user.get("id")
    brief["commander_comments"] = payload.operator_comments

    # Invariant: Trigger mock notification only
    mock_notification = {
        "dispatch_mode": "MOCK_SIMULATION",
        "mock_banner": "[SIMULATION ONLY - NOT A REAL EMERGENCY ALERT]",
        "brief_id": brief_id,
        "target_zone": brief["target_zone_name"],
        "recommended_actions": brief["recommended_actions"],
        "shelters_activated": [s["name"] for s in brief.get("recommended_shelters", [])[:2]],
        "dispatched_to_mock_sirens": False,
        "dispatched_to_mock_responders": True,
        "operator": current_user.get("name")
    }
    brief["mock_dispatch_payload"] = mock_notification

    store.record_audit(
        actor_id=current_user.get("id"),
        actor_role=current_user.get("role").value,
        action="RESPONSE_BRIEF_APPROVED",
        resource_type="RESPONSE_BRIEF",
        resource_id=brief_id,
        details={
            "comments": payload.operator_comments,
            "mock_notification": mock_notification
        }
    )

    return {
        "status": "APPROVED",
        "brief_id": brief_id,
        "decision": "APPROVED",
        "operator": current_user.get("name"),
        "mock_notification": mock_notification
    }


@router.post("/{brief_id}/reject")
def reject_response_brief(
    brief_id: str,
    payload: DecisionInput,
    current_user: Dict[str, Any] = Depends(require_role([UserRole.DISASTER_COMMANDER, UserRole.FIELD_ANALYST]))
):
    """Rejects response brief with justification."""
    if brief_id not in store.response_briefs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found.")

    brief = store.response_briefs[brief_id]
    brief["approval_status"] = ApprovalStatus.REJECTED.value
    brief["rejected_by"] = current_user.get("name")
    brief["rejection_comments"] = payload.operator_comments

    store.record_audit(
        actor_id=current_user.get("id"),
        actor_role=current_user.get("role").value,
        action="RESPONSE_BRIEF_REJECTED",
        resource_type="RESPONSE_BRIEF",
        resource_id=brief_id,
        details={"rejection_reason": payload.operator_comments}
    )

    return {
        "status": "REJECTED",
        "brief_id": brief_id,
        "decision": "REJECTED",
        "operator": current_user.get("name"),
        "reason": payload.operator_comments
    }
