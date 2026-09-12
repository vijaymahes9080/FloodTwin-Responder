"""
Data Contracts and Pydantic Models for FLOODTWIN RESPONDER.
Strictly specifies provenance, uncertainty, spatial geometry, and data state categories.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class DataSourceCategory(str, Enum):
    MEASURED = "MEASURED"        # Ground truth IoT sensors, stream gauges
    OBSERVED = "OBSERVED"        # Verified human observer, citizen ground report
    ESTIMATED = "ESTIMATED"      # Interpolated surface, spatial risk estimation
    SIMULATED = "SIMULATED"      # Hydrological runoff simulation, synthetic testbed


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReportVerificationStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    POSSIBLE_WATERLOGGING = "POSSIBLE_WATERLOGGING"
    VERIFIED_FIELD = "VERIFIED_FIELD"
    LIKELY_DUPLICATE = "LIKELY_DUPLICATE"
    REJECTED_IMPOSSIBLE = "REJECTED_IMPOSSIBLE"
    ADVERSARIAL_SUPPRESSED = "ADVERSARIAL_SUPPRESSED"


class ApprovalStatus(str, Enum):
    PENDING_HUMAN_APPROVAL = "PENDING_HUMAN_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REQUIRES_FIELD_INSPECTION = "REQUIRES_FIELD_INSPECTION"


class ProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    source_system: str = Field(..., description="System or ingest channel origin")
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_pipeline: str = "FloodTwin-v1.0"
    raw_payload_hash: Optional[str] = None
    sanitization_applied: List[str] = Field(default_factory=list)


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude_m: Optional[float] = None
    crs: str = "EPSG:4326"


# 1. FloodReport
class FloodReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Unique UUID")
    timestamp: datetime = Field(..., description="Observation timestamp")
    source: str = Field(..., description="Citizen report, emergency hotline, field staff")
    data_category: DataSourceCategory = DataSourceCategory.OBSERVED
    confidence: float = Field(..., ge=0.0, le=1.0, description="Verification credibility score")
    coordinates: Coordinates
    reported_depth_cm: Optional[float] = Field(default=None, ge=0.0, description="Estimated water depth in cm")
    description: str = Field(..., description="PII-sanitized textual description")
    water_flow: Optional[str] = Field(default="standing", description="standing, moving, rapid")
    image_url: Optional[str] = None
    verification_status: ReportVerificationStatus = ReportVerificationStatus.UNVERIFIED
    duplicate_of: Optional[str] = None
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 2. SensorReading
class SensorReading(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Unique Reading UUID")
    sensor_id: str = Field(..., description="Hardware sensor identifier")
    timestamp: datetime = Field(..., description="Timestamp of telemetry reading")
    source: str = "TELEMETRY_IOT"
    data_category: DataSourceCategory = DataSourceCategory.MEASURED
    coordinates: Coordinates
    water_level_m: float = Field(..., description="Surface water stage in meters")
    flood_threshold_m: float = Field(default=2.5, description="Warning stage threshold")
    battery_percentage: Optional[float] = Field(default=100.0, ge=0.0, le=100.0)
    signal_rssi: Optional[int] = None
    quality_flag: str = Field(default="VALID", description="VALID, SUSPECT, STALE, OUTAGE")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 3. SatelliteObservation
class SatelliteObservation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Unique Satellite Scene UUID")
    timestamp: datetime = Field(..., description="Acquisition timestamp")
    source: str = Field(..., description="Sentinel-1 SAR, Sentinel-2 Optical, Synthetic Tile")
    data_category: DataSourceCategory = DataSourceCategory.ESTIMATED
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    sensor_type: str = Field(default="SAR_C_BAND", description="SAR or Multispectral")
    resolution_meters: float = Field(default=10.0, ge=0.1)
    bounding_box: List[float] = Field(..., description="[min_lon, min_lat, max_lon, max_lat]")
    water_mask_coverage_pct: float = Field(..., ge=0.0, le=100.0)
    crs: str = "EPSG:4326"
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 4. RiskTile
class RiskFactorBreakdown(BaseModel):
    rainfall_contribution: float = Field(..., ge=0.0, le=1.0)
    sensor_water_level_contribution: float = Field(..., ge=0.0, le=1.0)
    citizen_reports_contribution: float = Field(..., ge=0.0, le=1.0)
    elevation_vulnerability_contribution: float = Field(..., ge=0.0, le=1.0)
    critical_asset_density_contribution: float = Field(..., ge=0.0, le=1.0)


class RiskTile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    tile_id: str = Field(..., description="Geohash or Quadkey identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "FloodTwin-RiskEngine"
    data_category: DataSourceCategory = DataSourceCategory.ESTIMATED
    bounding_box: List[float] = Field(..., description="[min_lon, min_lat, max_lon, max_lat]")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Transparent explainable composite risk (0-100)")
    severity: SeverityLevel
    factors: RiskFactorBreakdown
    uncertainty_score: float = Field(..., ge=0.0, le=1.0, description="Uncertainty due to sensor sparsity or stale reports")
    missing_data_items: List[str] = Field(default_factory=list)
    recommended_verification_step: str
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 5. CriticalAsset
class CriticalAsset(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Asset identifier")
    name: str = Field(..., description="Asset title e.g. Rajiv Gandhi Govt General Hospital")
    category: str = Field(..., description="HOSPITAL, SCHOOL, BRIDGE, POWER_STATION, WATER_TREATMENT")
    source: str = "OpenStreetMap_DistrictMaster"
    data_category: DataSourceCategory = DataSourceCategory.OBSERVED
    coordinates: Coordinates
    elevation_m: float = Field(..., description="Ground elevation in meters above MSL")
    capacity_or_beds: Optional[int] = None
    flood_protection_tier_cm: float = Field(default=30.0, description="Bund / plinth flood height barrier in cm")
    is_operational: bool = True
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 6. Shelter
class Shelter(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Shelter identifier")
    name: str = Field(..., description="Shelter facility name")
    source: str = "District_Emergency_Management_Office"
    data_category: DataSourceCategory = DataSourceCategory.OBSERVED
    coordinates: Coordinates
    total_capacity: int = Field(..., ge=1)
    current_occupancy: int = Field(default=0, ge=0)
    operational_status: str = Field(default="OPEN", description="OPEN, STANDBY, AT_CAPACITY, INACCESSIBLE")
    emergency_contact: str = Field(..., description="Designated coordinator / helpline contact")
    has_medical_supply: bool = True
    has_backup_power: bool = True
    wheelchair_accessible: bool = True
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 7. EmergencyProcedure
class EmergencyProcedure(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Procedure SOP identifier")
    title: str = Field(..., description="Standard Operating Procedure title")
    section: str = Field(..., description="Chapter / Section name")
    page_number: int = Field(..., ge=1)
    publication_date: str = Field(..., description="YYYY-MM-DD")
    jurisdiction: str = Field(..., description="National / State / District Authority")
    content_hash: str = Field(..., description="SHA-256 hash of official document text")
    content: str = Field(..., description="Authorized procedure text excerpt")
    applicable_severity: List[SeverityLevel]
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 8. ResponseBrief
class ResponseBrief(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Response Brief unique identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "BoundedResponseAgent"
    data_category: DataSourceCategory = DataSourceCategory.SIMULATED
    target_zone_id: str
    target_zone_name: str
    current_risk_score: float = Field(..., ge=0.0, le=100.0)
    severity: SeverityLevel
    uncertainty_score: float = Field(..., ge=0.0, le=1.0)
    evidence_summary: List[str] = Field(default_factory=list)
    affected_assets: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_shelters: List[Dict[str, Any]] = Field(default_factory=list)
    policy_citations: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    human_approval_required: bool = True
    approval_status: ApprovalStatus = ApprovalStatus.PENDING_HUMAN_APPROVAL
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 9. ApprovalRequest
class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Approval request identifier")
    brief_id: str = Field(..., description="Associated response brief ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requested_by: str = "BoundedResponseAgent"
    decision: ApprovalStatus = ApprovalStatus.PENDING_HUMAN_APPROVAL
    operator_id: Optional[str] = None
    operator_role: Optional[str] = None
    operator_comments: Optional[str] = None
    mock_notification_dispatched: bool = False
    mock_notification_payload: Optional[Dict[str, Any]] = None
    version: str = "1.0.0"
    provenance: ProvenanceRecord


# 10. AuditEvent
class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="Audit event identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: str = Field(..., description="User ID or Agent System name")
    actor_role: str = Field(..., description="COMMANDER, ANALYST, AUDITOR, SYSTEM")
    action: str = Field(..., description="e.g. REPORT_VERIFIED, BRIEF_GENERATED, ACTION_APPROVED, POLICY_QUERIED")
    resource_type: str = Field(..., description="REPORT, BRIEF, SENSOR, APPROVAL, AUDIT")
    resource_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    provenance_hash: str = Field(..., description="SHA-256 tamper-evident integrity hash")
    previous_event_hash: Optional[str] = None
    version: str = "1.0.0"
