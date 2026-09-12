"""
Explainable Flood Risk analysis and tile endpoints for FLOODTWIN RESPONDER.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from backend.app.core.auth import get_current_user
from backend.app.services.store import store
from risk_engine import FloodRiskEngine

router = APIRouter(prefix="/risk", tags=["Risk Analysis"])
risk_engine = FloodRiskEngine()


class RiskAnalyzeInput(BaseModel):
    rainfall_3h_mm: Optional[float] = Field(default=None, ge=0.0)
    sensor_water_level_m: Optional[float] = Field(default=None, ge=0.0)
    sensor_warning_threshold_m: Optional[float] = 3.0
    sensor_danger_threshold_m: Optional[float] = 4.0
    reported_depth_cm: Optional[float] = Field(default=None, ge=0.0)
    elevation_m: Optional[float] = 6.0
    nearby_critical_assets_count: Optional[int] = 2
    report_age_hours: Optional[float] = 0.5
    source_confidence: Optional[float] = 0.85
    has_satellite_water_mask: Optional[bool] = False


@router.post("/analyze")
def analyze_flood_risk(
    payload: RiskAnalyzeInput,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Computes explainable composite flood risk score with factor breakdown,
    uncertainty analysis, and actionable verification recommendation.
    """
    result = risk_engine.calculate_risk(
        rainfall_3h_mm=payload.rainfall_3h_mm,
        sensor_water_level_m=payload.sensor_water_level_m,
        sensor_warning_threshold_m=payload.sensor_warning_threshold_m or 3.0,
        sensor_danger_threshold_m=payload.sensor_danger_threshold_m or 4.0,
        reported_depth_cm=payload.reported_depth_cm,
        elevation_m=payload.elevation_m or 6.0,
        nearby_critical_assets_count=payload.nearby_critical_assets_count or 0,
        report_age_hours=payload.report_age_hours or 0.5,
        source_confidence=payload.source_confidence or 0.85,
        has_satellite_water_mask=payload.has_satellite_water_mask or False
    )

    store.record_audit(
        actor_id=current_user.get("id", "ANALYST"),
        actor_role=str(current_user.get("role", "FIELD_ANALYST")),
        action="RISK_ANALYSIS_COMPUTED",
        resource_type="RISK_CALCULATION",
        resource_id=f"RISK-{result['score']}",
        details={
            "score": result["score"],
            "severity": result["severity"],
            "uncertainty": result["uncertainty_score"]
        }
    )

    return result


@router.get("/tiles")
def get_risk_tiles():
    """Returns pre-calculated explainable risk tiles across Chennai flood zones."""
    # Synthesize explainable tile scores for active zones
    zones = [
        {
            "tile_id": "ZONE_01_CENTRAL",
            "name": "Central Chennai - Cooum Basin",
            "bbox": [80.220, 13.060, 80.280, 13.095],
            "rainfall_3h_mm": 98.0,
            "sensor_water_level_m": 3.85,
            "reported_depth_cm": 60.0,
            "elevation_m": 6.5,
            "assets_count": 3
        },
        {
            "tile_id": "ZONE_02_SOUTH",
            "name": "South Chennai - Adyar Basin",
            "bbox": [80.210, 13.000, 80.270, 13.055],
            "rainfall_3h_mm": 115.5,
            "sensor_water_level_m": 4.45,
            "reported_depth_cm": 110.0,
            "elevation_m": 4.2,
            "assets_count": 4
        },
        {
            "tile_id": "ZONE_03_WEST",
            "name": "West Chennai - Chembarambakkam Runoff",
            "bbox": [80.150, 13.020, 80.210, 13.080],
            "rainfall_3h_mm": 142.0,
            "sensor_water_level_m": 3.40,
            "reported_depth_cm": 45.0,
            "elevation_m": 6.1,
            "assets_count": 2
        },
        {
            "tile_id": "ZONE_04_NORTH",
            "name": "North Chennai - Buckingham Canal North",
            "bbox": [80.220, 13.100, 80.280, 13.150],
            "rainfall_3h_mm": 52.0,
            "sensor_water_level_m": 2.20,
            "reported_depth_cm": 20.0,
            "elevation_m": 7.5,
            "assets_count": 1
        }
    ]

    tiles_output = []
    for z in zones:
        calc = risk_engine.calculate_risk(
            rainfall_3h_mm=z["rainfall_3h_mm"],
            sensor_water_level_m=z["sensor_water_level_m"],
            reported_depth_cm=z["reported_depth_cm"],
            elevation_m=z["elevation_m"],
            nearby_critical_assets_count=z["assets_count"],
            report_age_hours=0.3
        )
        tiles_output.append({
            "tile_id": z["tile_id"],
            "zone_name": z["name"],
            "bbox": z["bbox"],
            "risk_score": calc["score"],
            "severity": calc["severity"],
            "uncertainty_score": calc["uncertainty_score"],
            "factors": calc["factors"],
            "missing_data": calc["missing_data"],
            "recommended_step": calc["recommended_next_verification_step"]
        })

    return {
        "count": len(tiles_output),
        "crs": "EPSG:4326",
        "tiles": tiles_output
    }
