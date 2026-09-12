"""
Explainable Risk Engine Tests for FLOODTWIN RESPONDER.
"""

import pytest
from risk_engine import FloodRiskEngine


def test_zero_flood_risk():
    engine = FloodRiskEngine()
    calc = engine.calculate_risk(
        rainfall_3h_mm=0.0,
        sensor_water_level_m=0.5,
        reported_depth_cm=0.0,
        elevation_m=20.0,
        nearby_critical_assets_count=0
    )
    assert calc["score"] < 20.0
    assert calc["severity"] == "LOW"


def test_critical_flood_risk():
    engine = FloodRiskEngine()
    calc = engine.calculate_risk(
        rainfall_3h_mm=130.0,
        sensor_water_level_m=4.5,
        sensor_warning_threshold_m=3.0,
        sensor_danger_threshold_m=4.0,
        reported_depth_cm=110.0,
        elevation_m=3.5,
        nearby_critical_assets_count=4
    )
    assert calc["score"] >= 75.0
    assert calc["severity"] in ("HIGH", "CRITICAL")
    assert "rainfall_contribution" in calc["factors"]


def test_missing_data_and_uncertainty_penalty():
    engine = FloodRiskEngine()
    # Telemetry and sensor data completely absent
    calc = engine.calculate_risk(
        rainfall_3h_mm=None,
        sensor_water_level_m=None,
        reported_depth_cm=40.0,
        report_age_hours=4.0
    )
    assert calc["uncertainty_score"] > 0.40
    assert len(calc["missing_data"]) >= 2
    assert "Stream gauge hardware telemetry missing" in calc["missing_data"]
