export type SeverityLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export interface FloodReport {
  id: string;
  timestamp: string;
  source: string;
  data_category: string;
  confidence: number;
  coordinates: {
    latitude: number;
    longitude: number;
    altitude_m?: number;
    crs: string;
  };
  reported_depth_cm?: number;
  description: string;
  water_flow?: string;
  image_url?: string;
  verification_status: string;
  duplicate_of?: string;
  provenance: {
    source_system: string;
    ingested_at: string;
    sanitization_applied: string[];
  };
}

export interface SensorReading {
  sensor_id: string;
  sensor_name?: string;
  timestamp: string;
  latitude?: number;
  longitude?: number;
  water_level_m: number;
  warning_threshold_m?: number;
  danger_threshold_m?: number;
  battery_percentage?: number;
  quality_flag: string;
  data_category: string;
}

export interface RainfallStation {
  station_id: string;
  station_name: string;
  latitude: number;
  longitude: number;
  rain_last_1h_mm: number;
  rain_last_3h_mm: number;
  rain_last_24h_mm: number;
  intensity_classification: string;
  timestamp: string;
}

export interface RiskTile {
  tile_id: string;
  zone_name: string;
  bbox: number[];
  risk_score: number;
  severity: SeverityLevel;
  uncertainty_score: number;
  factors: {
    rainfall_contribution: number;
    sensor_water_level_contribution: number;
    citizen_reports_contribution: number;
    elevation_vulnerability_contribution: number;
    critical_asset_density_contribution: number;
  };
  missing_data: string[];
  recommended_step: string;
}

export interface CriticalAsset {
  id: string;
  name: string;
  category: string;
  distance_km: number;
  elevation_m: number;
  exposure_tier: string;
  latitude: number;
  longitude: number;
  emergency_contact?: string;
}

export interface Shelter {
  id: string;
  name: string;
  distance_km: number;
  total_capacity: number;
  current_occupancy: number;
  available_capacity: number;
  operational_status: string;
  emergency_contact: string;
  latitude: number;
  longitude: number;
  has_medical_supply?: boolean;
}

export interface PolicyCitation {
  source_title: string;
  section: string;
  page: number;
  publication_date: string;
  jurisdiction: string;
  content_hash: string;
  relevance_score: number;
  excerpt: string;
  full_content: string;
}

export interface ResponseBrief {
  id: string;
  created_at: string;
  target_zone_id: string;
  target_zone_name: string;
  current_risk_score: number;
  severity: SeverityLevel;
  uncertainty_score: number;
  evidence_summary: string[];
  affected_assets: any[];
  recommended_shelters: any[];
  policy_citations: PolicyCitation[];
  recommended_actions: string[];
  human_approval_required: boolean;
  approval_status: string;
  approved_by?: string;
  commander_comments?: string;
  mock_dispatch_payload?: any;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  actor_id: string;
  actor_role: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, any>;
  provenance_hash: string;
  previous_event_hash?: string;
}
