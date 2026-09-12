"""
Sensor and Telemetry endpoints for FLOODTWIN RESPONDER.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.core.auth import get_current_user
from backend.app.services.store import store

router = APIRouter(prefix="/sensors", tags=["Sensors"])


class SensorReadingInput(BaseModel):
    sensor_id: str
    sensor_name: Optional[str] = None
    water_level_m: float = Field(..., ge=0.0, le=15.0)
    warning_threshold_m: Optional[float] = 3.0
    danger_threshold_m: Optional[float] = 4.0
    battery_percentage: Optional[float] = Field(default=100.0, ge=0.0, le=100.0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    quality_flag: Optional[str] = "VALID"


@router.post("/readings", status_code=status.HTTP_201_CREATED)
def submit_sensor_reading(
    payload: SensorReadingInput,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Ingests real-time IoT water-level sensor telemetry."""
    reading_dict = {
        "sensor_id": payload.sensor_id,
        "sensor_name": payload.sensor_name or f"Stream Gauge {payload.sensor_id}",
        "water_level_m": payload.water_level_m,
        "warning_threshold_m": payload.warning_threshold_m,
        "danger_threshold_m": payload.danger_threshold_m,
        "battery_percentage": payload.battery_percentage,
        "quality_flag": payload.quality_flag or "VALID",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_category": "MEASURED",
        "latitude": payload.latitude or 13.05,
        "longitude": payload.longitude or 80.24,
    }

    updated = store.add_sensor_reading(reading_dict)
    store.record_audit(
        actor_id=payload.sensor_id,
        actor_role="TELEMETRY_HARDWARE",
        action="SENSOR_TELEMETRY_INGESTED",
        resource_type="SENSOR",
        resource_id=payload.sensor_id,
        details={
            "water_level_m": payload.water_level_m,
            "quality_flag": payload.quality_flag
        }
    )
    return updated


@router.get("/status")
def get_sensor_status():
    """Lists current health and water stage of all network sensors."""
    sensors = list(store.sensors.values())
    rain_stations = list(store.rainfall_stations.values())
    return {
        "total_water_level_sensors": len(sensors),
        "total_rainfall_stations": len(rain_stations),
        "water_level_sensors": sensors,
        "rainfall_stations": rain_stations
    }
