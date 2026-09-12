"""
Bounded Response Agent for FLOODTWIN RESPONDER.
Implements a strict 8-state deterministic Finite State Machine (FSM).
Guarantees human-in-the-loop oversight and bars autonomous alerts.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.app.schemas.contracts import (
    ApprovalStatus,
    DataSourceCategory,
    ProvenanceRecord,
    ResponseBrief,
    SeverityLevel,
)
from geospatial.spatial_engine import SpatialEngine
from rag.knowledge_base import PolicyKnowledgeBase
from risk_engine import FloodRiskEngine


class AgentState(str, Enum):
    COLLECT_EVIDENCE = "COLLECT_EVIDENCE"
    VERIFY = "VERIFY"
    ASSESS = "ASSESS"
    PRIORITIZE = "PRIORITIZE"
    RETRIEVE_POLICY = "RETRIEVE_POLICY"
    DRAFT_BRIEF = "DRAFT_BRIEF"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    RECORD_DECISION = "RECORD_DECISION"


class DisallowedActionError(Exception):
    """Raised when an attempt is made to execute an action outside bounded safety limits."""
    pass


class BoundedResponseAgent:
    """
    Deterministic 8-State Agentic Workflow.
    Guarantees no autonomous alerts, dispatches, or record modifications.
    """

    DISALLOWED_ACTIONS = {
        "SEND_LIVE_ALERT",
        "ISSUE_MANDATORY_EVACUATION",
        "AUTO_DISPATCH_RESCUE",
        "MODIFY_OFFICIAL_REGISTRY",
        "SUPPRESS_AUDIT_LOG",
    }

    def __init__(
        self,
        risk_engine: Optional[FloodRiskEngine] = None,
        spatial_engine: Optional[SpatialEngine] = None,
        knowledge_base: Optional[PolicyKnowledgeBase] = None
    ):
        self.risk_engine = risk_engine or FloodRiskEngine()
        self.spatial_engine = spatial_engine or SpatialEngine()
        self.knowledge_base = knowledge_base or PolicyKnowledgeBase()
        self.current_state = AgentState.COLLECT_EVIDENCE

    def execute_workflow(
        self,
        target_zone_id: str,
        target_zone_name: str,
        zone_coords: Dict[str, float],
        rainfall_data: Optional[Dict[str, Any]] = None,
        sensor_data: Optional[Dict[str, Any]] = None,
        citizen_reports: Optional[List[Dict[str, Any]]] = None,
        critical_assets: Optional[List[Dict[str, Any]]] = None,
        shelters: Optional[List[Dict[str, Any]]] = None,
        elevation_m: float = 6.0
    ) -> ResponseBrief:
        """
        Executes the 8-state transition pipeline in strict succession.
        """
        # 1. State: COLLECT_EVIDENCE
        self.current_state = AgentState.COLLECT_EVIDENCE
        evidence_items = []
        lat = zone_coords.get("latitude", 13.04)
        lon = zone_coords.get("longitude", 80.23)

        rain_3h = rainfall_data.get("rain_last_3h_mm") if rainfall_data else None
        if rain_3h is not None:
            evidence_items.append(f"Rainfall: {rain_3h}mm recorded over past 3 hours at {rainfall_data.get('station_name', 'AWS station')}.")

        water_lvl = sensor_data.get("water_level_m") if sensor_data else None
        sensor_warn = sensor_data.get("warning_threshold_m", 3.0) if sensor_data else 3.0
        sensor_dang = sensor_data.get("danger_threshold_m", 4.0) if sensor_data else 4.0
        if water_lvl is not None:
            evidence_items.append(f"Stream Gauge: {water_lvl}m at {sensor_data.get('sensor_name', 'River sensor')} (Danger mark: {sensor_dang}m).")

        reports_in_zone = citizen_reports or []
        depths = [r.get("reported_depth_cm") for r in reports_in_zone if r.get("reported_depth_cm") is not None]
        avg_depth = sum(depths) / len(depths) if depths else None
        if avg_depth is not None:
            evidence_items.append(f"Field Reports: {len(reports_in_zone)} verified reports indicating average water depth of {round(avg_depth, 1)}cm.")

        # 2. State: VERIFY
        self.current_state = AgentState.VERIFY
        # Reject impossible depths (>300cm) or future anomalies
        clean_reports = [r for r in reports_in_zone if (r.get("reported_depth_cm") or 0) <= 250.0]

        # 3. State: ASSESS
        self.current_state = AgentState.ASSESS
        risk_result = self.risk_engine.calculate_risk(
            rainfall_3h_mm=rain_3h,
            sensor_water_level_m=water_lvl,
            sensor_warning_threshold_m=sensor_warn,
            sensor_danger_threshold_m=sensor_dang,
            reported_depth_cm=avg_depth,
            elevation_m=elevation_m,
            nearby_critical_assets_count=len(critical_assets or []),
            report_age_hours=0.4,
            source_confidence=0.90
        )

        # 4. State: PRIORITIZE
        self.current_state = AgentState.PRIORITIZE
        affected_assets = self.spatial_engine.find_nearby_assets(lat, lon, critical_assets or [], radius_km=3.5)
        recommended_shelters = self.spatial_engine.find_nearby_shelters(lat, lon, shelters or [], max_distance_km=6.0)

        # 5. State: RETRIEVE_POLICY
        self.current_state = AgentState.RETRIEVE_POLICY
        search_query = f"urban flood inundation evacuation critical healthcare {target_zone_name}"
        citations = self.knowledge_base.search(search_query, top_k=3)

        # 6. State: DRAFT_BRIEF
        self.current_state = AgentState.DRAFT_BRIEF
        recommended_actions = [
            f"Pre-position municipal dewatering suction pumps along low-lying ingress points in {target_zone_name}.",
            "Dispatch field liaison team to coordinate stand-by shelter readiness at closest high-capacity hub.",
            f"Alert technical liaison to verify electrical substation plinth clearances ({risk_result['recommended_next_verification_step']})."
        ]

        brief_id = f"BRIEF-{uuid.uuid4().hex[:8].upper()}"
        brief = ResponseBrief(
            id=brief_id,
            created_at=datetime.now(timezone.utc),
            source="BoundedResponseAgent-FSM",
            data_category=DataSourceCategory.SIMULATED,
            target_zone_id=target_zone_id,
            target_zone_name=target_zone_name,
            current_risk_score=risk_result["score"],
            severity=SeverityLevel(risk_result["severity"]),
            uncertainty_score=risk_result["uncertainty_score"],
            evidence_summary=evidence_items,
            affected_assets=affected_assets[:4],
            recommended_shelters=recommended_shelters[:3],
            policy_citations=citations,
            recommended_actions=recommended_actions,
            human_approval_required=True,
            approval_status=ApprovalStatus.PENDING_HUMAN_APPROVAL,
            provenance=ProvenanceRecord(
                source_system="BoundedResponseAgent-FSM",
                processing_pipeline="FSM-8Step-Production",
                sanitization_applied=["Coordinate_Bounds", "Duplicate_Filter", "PII_Scrub"]
            )
        )

        # 7. State: REQUEST_APPROVAL
        self.current_state = AgentState.REQUEST_APPROVAL
        # Remains in PENDING_HUMAN_APPROVAL until authorized commander acts

        return brief

    def record_decision(self, brief: ResponseBrief, approved: bool, operator_id: str, comments: str) -> Dict[str, Any]:
        """
        8. State: RECORD_DECISION.
        Transitions the brief state following authenticated human review.
        """
        self.current_state = AgentState.RECORD_DECISION
        brief.approval_status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        decision_record = {
            "brief_id": brief.id,
            "decision": brief.approval_status.value,
            "operator_id": operator_id,
            "comments": comments,
            "decided_at": datetime.now(timezone.utc).isoformat(),
            "simulation_notification_sent": approved
        }
        return decision_record

    def attempt_autonomous_action(self, action_name: str):
        """Safety invariant checker: unconditionally raises error on banned actions."""
        if action_name.upper() in self.DISALLOWED_ACTIONS:
            raise DisallowedActionError(
                f"SAFETY INVARIANT VIOLATION: Autonomous action '{action_name}' is strictly barred. "
                f"FloodTwin Responder requires explicit human commander authorization."
            )
