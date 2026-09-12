"""
API Tests for FLOODTWIN RESPONDER FastAPI Backend.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.auth import OPERATORS

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["mock_notification_mode"] is True


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["safety_invariants"]["autonomous_alerts_permitted"] is False


def test_list_reports():
    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert isinstance(data["reports"], list)


def test_submit_valid_report():
    payload = {
        "description": "Knee-deep water on Anna Salai road near Thousand Lights subway. Call volunteer 9840112233.",
        "latitude": 13.060,
        "longitude": 80.250,
        "reported_depth_cm": 45.0,
        "source": "CITIZEN_APP"
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["verification_status"] == "POSSIBLE_WATERLOGGING"
    # Verify PII was redacted
    assert "[PHONE_REDACTED]" in data["description"]
    assert "9840112233" not in data["description"]


def test_submit_out_of_bounds_report():
    payload = {
        "description": "Report in the middle of the Indian Ocean",
        "latitude": 5.00,
        "longitude": 80.00,
        "reported_depth_cm": 50.0
    }
    response = client.post("/api/v1/reports", json=payload)
    assert response.status_code == 422


def test_risk_analysis():
    payload = {
        "rainfall_3h_mm": 90.0,
        "sensor_water_level_m": 3.8,
        "reported_depth_cm": 65.0,
        "elevation_m": 4.5
    }
    response = client.post("/api/v1/risk/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "severity" in data
    assert "factors" in data
    assert data["score"] > 0


def test_nearby_assets_query():
    response = client.get("/api/v1/assets/nearby?latitude=13.018&longitude=80.222&radius_km=4.0")
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data
    assert data["count"] >= 1


def test_nearby_shelters_query():
    response = client.get("/api/v1/shelters/nearby?latitude=13.018&longitude=80.222&max_distance_km=6.0")
    assert response.status_code == 200
    data = response.json()
    assert "shelters" in data
    assert data["count"] >= 1


def test_response_brief_creation_and_approval_workflow():
    # 1. Generate Brief
    gen_res = client.post("/api/v1/response-briefs", json={
        "zone_id": "ZONE_02_SOUTH",
        "zone_name": "South Chennai - Adyar Basin",
        "latitude": 13.018,
        "longitude": 80.222
    })
    assert gen_res.status_code == 201
    brief = gen_res.json()
    assert brief["approval_status"] == "PENDING_HUMAN_APPROVAL"
    brief_id = brief["id"]

    # 2. Approve Brief with DISASTER_COMMANDER role
    appr_res = client.post(
        f"/api/v1/response-briefs/{brief_id}/approve",
        headers={"x-operator-key": "cmd_kumar"},
        json={"operator_comments": "Authorized deployment under Standard Operating Procedure 4.2."}
    )
    assert appr_res.status_code == 200
    appr_data = appr_res.json()
    assert appr_data["decision"] == "APPROVED"
    assert appr_data["mock_notification"]["dispatch_mode"] == "MOCK_SIMULATION"

    # 3. Check Audit Trail
    audit_res = client.get("/api/v1/audit")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["chain_integrity"] == "VALID"
