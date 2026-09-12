"""
Explainable Multi-Factor Flood Risk Engine for FLOODTWIN RESPONDER.
Computes transparent composite risk index, factor attribution,
uncertainty metrics, missing data alerts, and actionable verification steps.
"""

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.app.schemas.contracts import SeverityLevel


class FloodRiskEngine:
    """
    Transparent Risk Scoring Engine.
    Formula:
        Score = min(100, (w_r * Rain + w_s * Sensor + w_d * Depth + w_e * Elev + w_v * Assets) * Freshness)
    """

    DEFAULT_WEIGHTS = {
        "rainfall": 0.25,
        "sensor_water_level": 0.30,
        "citizen_depth": 0.20,
        "elevation_vulnerability": 0.15,
        "critical_assets": 0.10,
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        # Normalize weights to sum to 1.0
        total_w = sum(self.weights.values())
        self.weights = {k: v / total_w for k, v in self.weights.items()}

    def calculate_risk(
        self,
        rainfall_3h_mm: Optional[float] = None,
        sensor_water_level_m: Optional[float] = None,
        sensor_warning_threshold_m: float = 3.0,
        sensor_danger_threshold_m: float = 4.0,
        reported_depth_cm: Optional[float] = None,
        elevation_m: float = 8.0,
        nearby_critical_assets_count: int = 0,
        report_age_hours: float = 0.5,
        source_confidence: float = 0.85,
        has_satellite_water_mask: bool = False
    ) -> Dict[str, Any]:
        missing_data = []
        uncertainty_factors = []

        # 1. Rainfall factor (0 to 100mm/3h maps to 0 to 1.0)
        if rainfall_3h_mm is not None:
            r_norm = min(1.0, max(0.0, rainfall_3h_mm / 100.0))
        else:
            r_norm = 0.0
            missing_data.append("Local rainfall radar/telemetry missing")
            uncertainty_factors.append(0.3)

        # 2. Sensor water level factor
        if sensor_water_level_m is not None:
            if sensor_water_level_m <= sensor_warning_threshold_m:
                s_norm = max(0.0, sensor_water_level_m / sensor_warning_threshold_m * 0.5)
            elif sensor_water_level_m >= sensor_danger_threshold_m:
                s_norm = 1.0
            else:
                ratio = (sensor_water_level_m - sensor_warning_threshold_m) / (sensor_danger_threshold_m - sensor_warning_threshold_m)
                s_norm = 0.5 + 0.5 * ratio
        else:
            s_norm = 0.0
            missing_data.append("Stream gauge hardware telemetry missing")
            uncertainty_factors.append(0.35)

        # 3. Reported ground depth factor (0 to 120cm maps to 0 to 1.0)
        if reported_depth_cm is not None:
            d_norm = min(1.0, max(0.0, reported_depth_cm / 120.0)) * source_confidence
        else:
            d_norm = 0.0
            missing_data.append("Citizen or field reported water depth missing")
            uncertainty_factors.append(0.2)

        # 4. Elevation vulnerability (sea-level lowlands < 4m = high vulnerability)
        if elevation_m < 3.0:
            e_norm = 1.0
        elif elevation_m > 15.0:
            e_norm = 0.05
        else:
            e_norm = max(0.05, 1.0 - (elevation_m - 3.0) / 12.0)

        # 5. Critical asset exposure factor
        v_norm = min(1.0, nearby_critical_assets_count * 0.25)

        # 6. Freshness decay (half-life = 6 hours)
        freshness_decay = math.exp(-max(0.0, report_age_hours) / 6.0)

        # Dynamic weight redistribution across active observed inputs
        active_weight = 0.0
        weighted_sum = 0.0
        
        if rainfall_3h_mm is not None:
            active_weight += self.weights["rainfall"]
            weighted_sum += self.weights["rainfall"] * r_norm

        if sensor_water_level_m is not None:
            active_weight += self.weights["sensor_water_level"]
            weighted_sum += self.weights["sensor_water_level"] * s_norm

        if reported_depth_cm is not None:
            active_weight += self.weights["citizen_depth"]
            weighted_sum += self.weights["citizen_depth"] * d_norm

        # Baseline spatial topography and asset vulnerability
        active_weight += self.weights["elevation_vulnerability"] + self.weights["critical_assets"]
        weighted_sum += (
            self.weights["elevation_vulnerability"] * e_norm +
            self.weights["critical_assets"] * v_norm
        )

        raw_composite = (weighted_sum / max(0.001, active_weight)) if active_weight > 0 else 0.0

        # Boost by satellite confirmation if available
        if has_satellite_water_mask:
            raw_composite = min(1.0, raw_composite * 1.15)

        final_score = round(min(100.0, max(0.0, raw_composite * freshness_decay * 100.0)), 1)

        # Severity determination
        if final_score < 30.0:
            severity = SeverityLevel.LOW
        elif final_score < 55.0:
            severity = SeverityLevel.MODERATE
        elif final_score < 80.0:
            severity = SeverityLevel.HIGH
        else:
            severity = SeverityLevel.CRITICAL

        # Factor attribution percentages
        total_active_raw = (
            self.weights["rainfall"] * r_norm +
            self.weights["sensor_water_level"] * s_norm +
            self.weights["citizen_depth"] * d_norm +
            self.weights["elevation_vulnerability"] * e_norm +
            self.weights["critical_assets"] * v_norm
        )
        if total_active_raw > 0:
            breakdown = {
                "rainfall_contribution": round((self.weights["rainfall"] * r_norm) / total_active_raw, 3),
                "sensor_water_level_contribution": round((self.weights["sensor_water_level"] * s_norm) / total_active_raw, 3),
                "citizen_reports_contribution": round((self.weights["citizen_depth"] * d_norm) / total_active_raw, 3),
                "elevation_vulnerability_contribution": round((self.weights["elevation_vulnerability"] * e_norm) / total_active_raw, 3),
                "critical_asset_density_contribution": round((self.weights["critical_assets"] * v_norm) / total_active_raw, 3),
            }
        else:
            breakdown = {
                "rainfall_contribution": 0.0,
                "sensor_water_level_contribution": 0.0,
                "citizen_reports_contribution": 0.0,
                "elevation_vulnerability_contribution": 0.0,
                "critical_asset_density_contribution": 0.0,
            }

        # Uncertainty calculation: penalized by missing streams and age
        base_uncertainty = sum(uncertainty_factors)
        if report_age_hours > 3.0:
            base_uncertainty += min(0.25, (report_age_hours - 3.0) * 0.05)
        uncertainty_score = round(min(1.0, max(0.05, base_uncertainty + (1.0 - source_confidence) * 0.2)), 2)

        # Actionable next verification step
        if sensor_water_level_m is None:
            next_step = "Dispatch field engineer to inspect nearest river staff gauge and verify ultrasonic sensor status."
        elif reported_depth_cm is None:
            next_step = "Cross-reference municipal helpline calls or dispatch ward volunteer for ground depth photo verification."
        elif uncertainty_score > 0.40:
            next_step = "Request auxiliary drone or field patrol survey to resolve sparse sensor coverage before escalating alert."
        elif severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL):
            next_step = "Notify District Disaster Management Authority (DDMA) liaison officer to verify emergency shelter readiness."
        else:
            next_step = "Maintain routine sensor telemetry monitoring interval (15 minutes)."

        return {
            "score": final_score,
            "severity": severity.value,
            "factors": breakdown,
            "uncertainty_score": uncertainty_score,
            "freshness_decay_multiplier": round(freshness_decay, 3),
            "missing_data": missing_data,
            "recommended_next_verification_step": next_step,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }
