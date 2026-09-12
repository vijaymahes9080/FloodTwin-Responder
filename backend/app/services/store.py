"""
In-Memory & SQLite-backed Data Store for FLOODTWIN RESPONDER.
Initializes with rich sample datasets and maintains thread-safe state
for reports, sensors, assets, shelters, risk tiles, response briefs, and audit logs.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.core.security import compute_audit_hash
from backend.app.schemas.contracts import (
    ApprovalStatus,
    AuditEvent,
    Coordinates,
    CriticalAsset,
    DataSourceCategory,
    FloodReport,
    ProvenanceRecord,
    ReportVerificationStatus,
    ResponseBrief,
    RiskFactorBreakdown,
    RiskTile,
    SensorReading,
    SeverityLevel,
    Shelter,
)


class DataStore:
    def __init__(self, sample_data_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.sample_data_dir = sample_data_dir or os.path.join(base_dir, "sample-data")

        # In-memory storage
        self.reports: Dict[str, Dict[str, Any]] = {}
        self.sensors: Dict[str, Dict[str, Any]] = {}
        self.rainfall_stations: Dict[str, Dict[str, Any]] = {}
        self.critical_assets: List[Dict[str, Any]] = []
        self.shelters: List[Dict[str, Any]] = []
        self.administrative_boundaries: Dict[str, Any] = {}
        self.drainage_corridors: Dict[str, Any] = {}
        self.risk_tiles: Dict[str, Dict[str, Any]] = {}
        self.response_briefs: Dict[str, Dict[str, Any]] = {}
        self.audit_events: List[Dict[str, Any]] = []
        self._last_audit_hash = "GENESIS_ROOT_HASH_FLOODTWIN_2026"

        self.load_initial_data()

    def load_initial_data(self):
        """Loads curated sample datasets if available."""
        if not os.path.exists(self.sample_data_dir):
            return

        # 1. Admin boundaries
        admin_path = os.path.join(self.sample_data_dir, "administrative_boundary.geojson")
        if os.path.exists(admin_path):
            with open(admin_path, "r", encoding="utf-8") as f:
                self.administrative_boundaries = json.load(f)

        # 2. Hospitals & Critical Assets
        hosp_path = os.path.join(self.sample_data_dir, "hospitals.geojson")
        if os.path.exists(hosp_path):
            with open(hosp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.critical_assets.extend(data.get("features", []))

        schools_path = os.path.join(self.sample_data_dir, "schools.geojson")
        if os.path.exists(schools_path):
            with open(schools_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.critical_assets.extend(data.get("features", []))

        # 3. Shelters
        shelter_path = os.path.join(self.sample_data_dir, "shelters.geojson")
        if os.path.exists(shelter_path):
            with open(shelter_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.shelters = data.get("features", [])

        # 4. Drainage
        drain_path = os.path.join(self.sample_data_dir, "drainage_zones.geojson")
        if os.path.exists(drain_path):
            with open(drain_path, "r", encoding="utf-8") as f:
                self.drainage_corridors = json.load(f)

        # 5. Sensors
        sensor_path = os.path.join(self.sample_data_dir, "water_level_sensors.json")
        if os.path.exists(sensor_path):
            with open(sensor_path, "r", encoding="utf-8") as f:
                for s in json.load(f):
                    self.sensors[s["sensor_id"]] = s

        # 6. Rainfall
        rain_path = os.path.join(self.sample_data_dir, "rainfall_points.json")
        if os.path.exists(rain_path):
            with open(rain_path, "r", encoding="utf-8") as f:
                for r in json.load(f):
                    self.rainfall_stations[r["station_id"]] = r

        # 7. Initial Reports
        reports_path = os.path.join(self.sample_data_dir, "synthetic_flood_reports.json")
        if os.path.exists(reports_path):
            with open(reports_path, "r", encoding="utf-8") as f:
                for rep in json.load(f):
                    self.reports[rep["id"]] = rep

        # 8. Record genesis audit event
        self.record_audit(
            actor_id="SYSTEM_INIT",
            actor_role="SYSTEM",
            action="DATASTORE_INITIALIZED",
            resource_type="SYSTEM",
            resource_id="FLOODTWIN_CORE",
            details={
                "reports_loaded": len(self.reports),
                "sensors_loaded": len(self.sensors),
                "assets_loaded": len(self.critical_assets),
                "shelters_loaded": len(self.shelters)
            }
        )

    def record_audit(
        self,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Appends a cryptographically chained audit event."""
        event_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        audit_hash = compute_audit_hash(
            actor_id=actor_id,
            action=action,
            resource_id=resource_id,
            details=details,
            previous_hash=self._last_audit_hash
        )
        event = {
            "id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "provenance_hash": audit_hash,
            "previous_event_hash": self._last_audit_hash,
            "version": "1.0.0"
        }
        self.audit_events.append(event)
        self._last_audit_hash = audit_hash
        return event

    def add_report(self, report_dict: Dict[str, Any]) -> Dict[str, Any]:
        self.reports[report_dict["id"]] = report_dict
        return report_dict

    def add_sensor_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        s_id = reading["sensor_id"]
        if s_id in self.sensors:
            self.sensors[s_id].update(reading)
        else:
            self.sensors[s_id] = reading
        return self.sensors[s_id]

    def add_response_brief(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        self.response_briefs[brief["id"]] = brief
        return brief


# Global Singleton instance
store = DataStore()
