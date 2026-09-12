"""
Bounded Response Agent FSM and Safety Invariant Tests for FLOODTWIN RESPONDER.
"""

import pytest
from agent.response_fsm import BoundedResponseAgent, DisallowedActionError, AgentState
from backend.app.schemas.contracts import ApprovalStatus


def test_agent_workflow_execution():
    agent = BoundedResponseAgent()
    brief = agent.execute_workflow(
        target_zone_id="ZONE_02_SOUTH",
        target_zone_name="South Chennai - Adyar Basin",
        zone_coords={"latitude": 13.018, "longitude": 80.222},
        rainfall_data={"rain_last_3h_mm": 95.0},
        sensor_data={"water_level_m": 4.1, "warning_threshold_m": 3.0, "danger_threshold_m": 4.0},
        elevation_m=4.5
    )

    assert brief.id.startswith("BRIEF-")
    assert brief.human_approval_required is True
    assert brief.approval_status == ApprovalStatus.PENDING_HUMAN_APPROVAL
    assert len(brief.evidence_summary) > 0
    assert len(brief.policy_citations) > 0


def test_disallowed_autonomous_action_prevention():
    agent = BoundedResponseAgent()
    with pytest.raises(DisallowedActionError) as exc_info:
        agent.attempt_autonomous_action("SEND_LIVE_ALERT")
    assert "SAFETY INVARIANT VIOLATION" in str(exc_info.value)

    with pytest.raises(DisallowedActionError):
        agent.attempt_autonomous_action("ISSUE_MANDATORY_EVACUATION")


def test_human_decision_recording():
    agent = BoundedResponseAgent()
    brief = agent.execute_workflow(
        target_zone_id="ZONE_01_CENTRAL",
        target_zone_name="Central Chennai",
        zone_coords={"latitude": 13.07, "longitude": 80.25}
    )

    record = agent.record_decision(
        brief=brief,
        approved=True,
        operator_id="CMD_001",
        comments="Approved deployment of inflatable rescue boats."
    )
    assert record["decision"] == "APPROVED"
    assert brief.approval_status == ApprovalStatus.APPROVED
