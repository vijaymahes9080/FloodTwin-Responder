import pytest
from backend.app.services.parametric_insurance import ParametricInsuranceEngine


def test_parametric_insurance_full_payout():
    # Catastrophic flood: stage 3.6m (> 3.5m)
    claim = ParametricInsuranceEngine.evaluate_claim_trigger(
        policy_id="POL-NOYYAL-088",
        insured_asset_name="Pappampatti Organic Paddy Farm",
        asset_lat=10.98,
        asset_lon=77.02,
        coverage_amount_inr=500000.0,
        water_stage_measured_m=3.6,
        rainfall_24h_mm=120.0,
        satellite_inundation_detected=True,
        sensor_status="nominal"
    )

    assert claim["payout_triggered"] is True
    assert claim["trigger_tier"] == "TIER_3_CATASTROPHIC_FLOOD"
    assert claim["payout_percentage"] == 100.0
    assert claim["payout_amount_inr"] == 500000.0
    assert len(claim["claim_certificate_sha256"]) == 64


def test_parametric_insurance_partial_payout_with_satellite():
    # Moderate stage 2.8m, but confirmed by satellite inundation -> elevated to Tier 3
    claim = ParametricInsuranceEngine.evaluate_claim_trigger(
        policy_id="POL-NOYYAL-089",
        insured_asset_name="Singanallur Cotton Mill Warehouse",
        asset_lat=11.00,
        asset_lon=76.99,
        coverage_amount_inr=1000000.0,
        water_stage_measured_m=2.85,
        rainfall_24h_mm=80.0,
        satellite_inundation_detected=True,
        sensor_status="nominal"
    )

    assert claim["payout_triggered"] is True
    assert claim["trigger_tier"] == "TIER_3_CATASTROPHIC_FLOOD"
    assert claim["payout_amount_inr"] == 1000000.0


def test_parametric_insurance_tamper_suspension():
    # Sensor status flagged as tamper / fault
    claim = ParametricInsuranceEngine.evaluate_claim_trigger(
        policy_id="POL-NOYYAL-090",
        insured_asset_name="Suspicious Claim Target",
        asset_lat=11.01,
        asset_lon=76.98,
        coverage_amount_inr=200000.0,
        water_stage_measured_m=4.0,
        rainfall_24h_mm=200.0,
        satellite_inundation_detected=False,
        sensor_status="tamper"
    )

    assert claim["payout_triggered"] is False
    assert claim["decision"] == "SUSPENDED_FOR_MANUAL_INSPECTION"
    assert claim["payout_amount_inr"] == 0.0
