"""
Parametric Flood Insurance Assessment & Automated Claim Settlement Engine.
Evaluates index-based catastrophe triggers for smallholder farmers and urban infrastructure.
Executes multi-source fraud-prevention cross-checks (IoT river stage + SAR satellite inundation).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import hashlib


class ParametricInsuranceEngine:
    """
    Evaluates objective parametric triggers (water stage level, rainfall accumulation, inundation duration)
    to calculate guaranteed insurance indemnities without lengthy loss-adjustment litigation.
    """

    @classmethod
    def evaluate_claim_trigger(
        cls,
        policy_id: str,
        insured_asset_name: str,
        asset_lat: float,
        asset_lon: float,
        coverage_amount_inr: float,
        water_stage_measured_m: float,
        rainfall_24h_mm: float,
        satellite_inundation_detected: bool,
        sensor_status: str = "nominal"
    ) -> Dict[str, Any]:
        """
        Determines payout percentage based on pre-defined objective parameters.
        Enforces dual-verification: sensor anomaly flags suppress automated payout.
        """
        if sensor_status in ["fault", "tamper"]:
            return {
                "policy_id": policy_id,
                "payout_triggered": False,
                "payout_percentage": 0.0,
                "payout_amount_inr": 0.0,
                "decision": "SUSPENDED_FOR_MANUAL_INSPECTION",
                "rationale": f"Sensor telemetry flagged with hardware defect: '{sensor_status}'. Manual surveyor verification required."
            }

        # Multi-tier index trigger rules
        payout_pct = 0.0
        tier_label = "NO_TRIGGER"

        if water_stage_measured_m >= 3.5 or (water_stage_measured_m >= 2.8 and satellite_inundation_detected):
            payout_pct = 100.0
            tier_label = "TIER_3_CATASTROPHIC_FLOOD"
        elif water_stage_measured_m >= 2.5 or rainfall_24h_mm >= 150.0:
            payout_pct = 60.0
            tier_label = "TIER_2_SEVERE_INUNDATION"
        elif water_stage_measured_m >= 1.8 or rainfall_24h_mm >= 100.0:
            payout_pct = 30.0
            tier_label = "TIER_1_MODERATE_WATERLOGGING"

        payout_inr = round((payout_pct / 100.0) * coverage_amount_inr, 2)
        is_triggered = payout_pct > 0.0

        # Cryptographic claim certificate hash
        cert_text = f"{policy_id}|{water_stage_measured_m}|{rainfall_24h_mm}|{payout_inr}|{datetime.now(timezone.utc).isoformat()}"
        cert_hash = hashlib.sha256(cert_text.encode("utf-8")).hexdigest()

        return {
            "policy_id": policy_id,
            "insured_asset": insured_asset_name,
            "coordinates": (asset_lat, asset_lon),
            "total_coverage_inr": coverage_amount_inr,
            "measured_water_stage_m": water_stage_measured_m,
            "cumulative_rainfall_24h_mm": rainfall_24h_mm,
            "satellite_inundation_corroborated": satellite_inundation_detected,
            "payout_triggered": is_triggered,
            "trigger_tier": tier_label,
            "payout_percentage": payout_pct,
            "payout_amount_inr": payout_inr,
            "claim_certificate_sha256": cert_hash,
            "disclaimer": "Parametric index settlement calculated under India Climate Disaster Resilience Model."
        }
