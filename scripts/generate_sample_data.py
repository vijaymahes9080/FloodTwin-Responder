"""
Generates comprehensive, realistic sample geospatial datasets for FLOODTWIN RESPONDER.
Operational Zone: Chennai Metropolitan Flood Basin (Cooum and Adyar river corridors).
CRS: EPSG:4326 (WGS 84).
"""

import json
import os
from datetime import datetime, timezone

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample-data")
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Administrative Boundary (4 flood management zones in Chennai)
admin_boundary = {
    "type": "FeatureCollection",
    "name": "Chennai_Flood_Management_Zones",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_01_CENTRAL",
                "name": "Central Chennai - Cooum Basin",
                "ward_numbers": [109, 110, 111, 112, 113],
                "population_estimate": 420000,
                "flood_risk_baseline": "HIGH",
                "drainage_basin": "Cooum River"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.220, 13.060], [80.280, 13.060],
                    [80.280, 13.095], [80.220, 13.095],
                    [80.220, 13.060]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_02_SOUTH",
                "name": "South Chennai - Adyar Basin",
                "ward_numbers": [170, 171, 172, 173, 174],
                "population_estimate": 380000,
                "flood_risk_baseline": "CRITICAL",
                "drainage_basin": "Adyar River"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.210, 13.000], [80.270, 13.000],
                    [80.270, 13.055], [80.210, 13.055],
                    [80.210, 13.000]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_03_WEST",
                "name": "West Chennai - Chembarambakkam Runoff",
                "ward_numbers": [140, 141, 142, 143],
                "population_estimate": 310000,
                "flood_risk_baseline": "HIGH",
                "drainage_basin": "Porur Lake Outfall"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.150, 13.020], [80.210, 13.020],
                    [80.210, 13.080], [80.150, 13.080],
                    [80.150, 13.020]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "zone_id": "ZONE_04_NORTH",
                "name": "North Chennai - Buckingham Canal North",
                "ward_numbers": [45, 46, 47, 48],
                "population_estimate": 290000,
                "flood_risk_baseline": "MODERATE",
                "drainage_basin": "Otteri Nullah"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [80.220, 13.100], [80.280, 13.100],
                    [80.280, 13.150], [80.220, 13.150],
                    [80.220, 13.100]
                ]]
            }
        }
    ]
}

# 2. Roads and Evacuation Arterials
roads = {
    "type": "FeatureCollection",
    "name": "Chennai_Key_Corridors",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "road_id": "ROAD_01",
                "name": "Anna Salai (Mount Road)",
                "category": "PRIMARY_ARTERIAL",
                "elevation_m": 8.5,
                "flood_susceptibility": "LOW"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[80.270, 13.080], [80.250, 13.060], [80.220, 13.020], [80.200, 13.005]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "road_id": "ROAD_02",
                "name": "Poonamallee High Road",
                "category": "PRIMARY_ARTERIAL",
                "elevation_m": 6.2,
                "flood_susceptibility": "MODERATE"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[80.280, 13.080], [80.230, 13.075], [80.170, 13.065]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "road_id": "ROAD_03",
                "name": "Inner Ring Road (100ft Road)",
                "category": "SECONDARY_ARTERIAL",
                "elevation_m": 4.8,
                "flood_susceptibility": "HIGH"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[80.205, 13.085], [80.210, 13.045], [80.215, 13.005]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "road_id": "ROAD_04",
                "name": "Adyar Bridge - Rajiv Gandhi Salai (OMR)",
                "category": "COASTAL_EXPRESSWAY",
                "elevation_m": 3.9,
                "flood_susceptibility": "CRITICAL"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[80.255, 13.010], [80.250, 12.980], [80.245, 12.950]]
            }
        }
    ]
}

# 3. Hospitals
hospitals = {
    "type": "FeatureCollection",
    "name": "Critical_Healthcare_Facilities",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": "HOSP_01",
                "name": "Rajiv Gandhi Government General Hospital (RGGGH)",
                "category": "HOSPITAL",
                "capacity_beds": 2700,
                "icu_capacity": 220,
                "elevation_m": 6.5,
                "flood_protection_tier_cm": 50.0,
                "generator_backup": "ROOFTOP_INSTALLED",
                "emergency_contact": "+91-44-25305000",
                "zone_id": "ZONE_01_CENTRAL"
            },
            "geometry": {"type": "Point", "coordinates": [80.278, 13.082]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "HOSP_02",
                "name": "Government Royapettah Hospital",
                "category": "HOSPITAL",
                "capacity_beds": 712,
                "icu_capacity": 60,
                "elevation_m": 7.2,
                "flood_protection_tier_cm": 40.0,
                "generator_backup": "GROUND_ELEVATED",
                "emergency_contact": "+91-44-28481400",
                "zone_id": "ZONE_01_CENTRAL"
            },
            "geometry": {"type": "Point", "coordinates": [80.262, 13.054]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "HOSP_03",
                "name": "MIOT International Manapakkam",
                "category": "HOSPITAL",
                "capacity_beds": 1000,
                "icu_capacity": 150,
                "elevation_m": 3.8,
                "flood_protection_tier_cm": 35.0,
                "generator_backup": "REINFORCED_ENCLOSURE",
                "emergency_contact": "+91-44-42002288",
                "zone_id": "ZONE_02_SOUTH"
            },
            "geometry": {"type": "Point", "coordinates": [80.187, 13.023]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "HOSP_04",
                "name": "Kalyani Multi-Specialty Hospital Mylapore",
                "category": "HOSPITAL",
                "capacity_beds": 220,
                "icu_capacity": 30,
                "elevation_m": 6.1,
                "flood_protection_tier_cm": 30.0,
                "generator_backup": "GROUND_LEVEL",
                "emergency_contact": "+91-44-28472480",
                "zone_id": "ZONE_02_SOUTH"
            },
            "geometry": {"type": "Point", "coordinates": [80.266, 13.037]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "HOSP_05",
                "name": "KMC Hospital Kilpauk",
                "category": "HOSPITAL",
                "capacity_beds": 850,
                "icu_capacity": 90,
                "elevation_m": 8.0,
                "flood_protection_tier_cm": 45.0,
                "generator_backup": "ROOFTOP_INSTALLED",
                "emergency_contact": "+91-44-28364950",
                "zone_id": "ZONE_01_CENTRAL"
            },
            "geometry": {"type": "Point", "coordinates": [80.243, 13.079]}
        }
    ]
}

# 4. Schools and Relief Staging Grounds
schools = {
    "type": "FeatureCollection",
    "name": "Educational_Institutions_and_Staging_Centers",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": "SCH_01",
                "name": "Presidency Girls Higher Secondary School Egmore",
                "category": "SCHOOL",
                "capacity": 800,
                "elevation_m": 7.5,
                "has_large_courtyard": True,
                "zone_id": "ZONE_01_CENTRAL"
            },
            "geometry": {"type": "Point", "coordinates": [80.258, 13.076]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "SCH_02",
                "name": "St. Bede's Anglo Indian School Santhome",
                "category": "SCHOOL",
                "capacity": 1200,
                "elevation_m": 5.8,
                "has_large_courtyard": True,
                "zone_id": "ZONE_02_SOUTH"
            },
            "geometry": {"type": "Point", "coordinates": [80.278, 13.034]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "SCH_03",
                "name": "Kendriya Vidyalaya CLRI Adyar",
                "category": "SCHOOL",
                "capacity": 950,
                "elevation_m": 6.8,
                "has_large_courtyard": True,
                "zone_id": "ZONE_02_SOUTH"
            },
            "geometry": {"type": "Point", "coordinates": [80.245, 13.007]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "SCH_04",
                "name": "Corporation Boys Higher Sec School Saidapet",
                "category": "SCHOOL",
                "capacity": 650,
                "elevation_m": 4.5,
                "has_large_courtyard": False,
                "zone_id": "ZONE_02_SOUTH"
            },
            "geometry": {"type": "Point", "coordinates": [80.221, 13.018]}
        }
    ]
}

# 5. Designated Relief Shelters
shelters = {
    "type": "FeatureCollection",
    "name": "Authorized_Disaster_Relief_Shelters",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": "SHELTER_01",
                "name": "Jawaharlal Nehru Indoor Stadium Relief Hub",
                "total_capacity": 3500,
                "current_occupancy": 320,
                "operational_status": "OPEN",
                "emergency_contact": "+91-44-25361234",
                "has_medical_supply": True,
                "has_backup_power": True,
                "wheelchair_accessible": True,
                "elevation_m": 8.0,
                "zone_id": "ZONE_01_CENTRAL"
            },
            "geometry": {"type": "Point", "coordinates": [80.274, 13.084]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "SHELTER_02",
                "name": "Saidapet Community Center & Multipurpose Hall",
                "total_capacity": 850,
                "current_occupancy": 150,
                "operational_status": "OPEN",
                "emergency_contact": "+91-44-24355512",
                "has_medical_supply": True,
                "has_backup_power": True,
                "wheelchair_accessible": True,
                "elevation_m": 5.2,
                "zone_id": "ZONE_02_SOUTH"
            },
            "geometry": {"type": "Point", "coordinates": [80.224, 13.022]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "SHELTER_03",
                "name": "Adyar Corporation Community Hall",
                "total_capacity": 600,
                "current_occupancy": 80,
                "operational_status": "OPEN",
                "emergency_contact": "+91-44-24419876",
                "has_medical_supply": True,
                "has_backup_power": True,
                "wheelchair_accessible": True,
                "elevation_m": 6.9,
                "zone_id": "ZONE_02_SOUTH"
            },
            "geometry": {"type": "Point", "coordinates": [80.252, 13.006]}
        },
        {
            "type": "Feature",
            "properties": {
                "id": "SHELTER_04",
                "name": "Koyambedu Wholesale Market Complex Safe Haven",
                "total_capacity": 2200,
                "current_occupancy": 0,
                "operational_status": "STANDBY",
                "emergency_contact": "+91-44-24792345",
                "has_medical_supply": False,
                "has_backup_power": True,
                "wheelchair_accessible": False,
                "elevation_m": 7.8,
                "zone_id": "ZONE_03_WEST"
            },
            "geometry": {"type": "Point", "coordinates": [80.191, 13.071]}
        }
    ]
}

# 6. Drainage and River Flood Corridor Buffers
drainage_zones = {
    "type": "FeatureCollection",
    "name": "Chennai_Major_Waterways_and_Drainage_Corridors",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": [
        {
            "type": "Feature",
            "properties": {
                "corridor_id": "CORRIDOR_COOUM",
                "name": "Cooum River Natural Flood Plain",
                "flood_carry_capacity_cusecs": 25000,
                "spillway_buffer_meters": 100
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [80.170, 13.072], [80.210, 13.075], [80.245, 13.078],
                    [80.265, 13.073], [80.285, 13.069]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "corridor_id": "CORRIDOR_ADYAR",
                "name": "Adyar River Natural Flood Plain",
                "flood_carry_capacity_cusecs": 55000,
                "spillway_buffer_meters": 150
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [80.180, 13.018], [80.215, 13.015], [80.240, 13.011],
                    [80.260, 13.008], [80.278, 13.005]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "corridor_id": "CORRIDOR_BUCKINGHAM",
                "name": "Buckingham Canal Tidal Reach",
                "flood_carry_capacity_cusecs": 12000,
                "spillway_buffer_meters": 50
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [80.278, 13.120], [80.275, 13.080], [80.265, 13.040],
                    [80.260, 13.000]
                ]
            }
        }
    ]
}

# 7. Rainfall Telemetry Points (Radar & Automated Weather Stations)
rainfall_points = [
    {
        "station_id": "AWS_NUNGAMBAKKAM",
        "station_name": "Regional Meteorological Centre Nungambakkam",
        "latitude": 13.061,
        "longitude": 80.242,
        "rain_last_1h_mm": 42.5,
        "rain_last_3h_mm": 98.0,
        "rain_last_24h_mm": 184.2,
        "intensity_classification": "VERY_HEAVY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "OPERATIONAL"
    },
    {
        "station_id": "AWS_MEENAMBAKKAM",
        "station_name": "Airport Meteorological Station Meenambakkam",
        "latitude": 12.994,
        "longitude": 80.181,
        "rain_last_1h_mm": 51.0,
        "rain_last_3h_mm": 115.5,
        "rain_last_24h_mm": 210.0,
        "intensity_classification": "EXTREMELY_HEAVY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "OPERATIONAL"
    },
    {
        "station_id": "AWS_ADYAR_ESTUARY",
        "station_name": "Adyar Estuary Coastal Gauge",
        "latitude": 13.007,
        "longitude": 80.271,
        "rain_last_1h_mm": 34.0,
        "rain_last_3h_mm": 72.0,
        "rain_last_24h_mm": 145.0,
        "intensity_classification": "HEAVY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "OPERATIONAL"
    },
    {
        "station_id": "AWS_CHEMBARAMBAKKAM",
        "station_name": "Chembarambakkam Reservoir Basin AWS",
        "latitude": 13.011,
        "longitude": 80.058,
        "rain_last_1h_mm": 68.0,
        "rain_last_3h_mm": 142.0,
        "rain_last_24h_mm": 265.0,
        "intensity_classification": "EXTREMELY_HEAVY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "OPERATIONAL"
    }
]

# 8. Water-Level Stream Gauge Telemetry
water_level_sensors = [
    {
        "sensor_id": "SENSOR_COOUM_CHETPET",
        "sensor_name": "Cooum River Stage Gauge - Chetpet Bridge",
        "latitude": 13.073,
        "longitude": 80.245,
        "water_level_m": 3.85,
        "baseline_normal_m": 1.20,
        "warning_threshold_m": 3.00,
        "danger_threshold_m": 3.60,
        "battery_percentage": 94.0,
        "quality_flag": "VALID",
        "timestamp": datetime.now(timezone.utc).isoformat()
    },
    {
        "sensor_id": "SENSOR_ADYAR_SAIDAPET",
        "sensor_name": "Adyar River Stage Gauge - Saidapet Causeway",
        "latitude": 13.018,
        "longitude": 80.222,
        "water_level_m": 4.45,
        "baseline_normal_m": 1.50,
        "warning_threshold_m": 3.20,
        "danger_threshold_m": 4.10,
        "battery_percentage": 88.5,
        "quality_flag": "VALID",
        "timestamp": datetime.now(timezone.utc).isoformat()
    },
    {
        "sensor_id": "SENSOR_ADYAR_KOTTURPURAM",
        "sensor_name": "Adyar Stage Gauge - Kotturpuram Bridge",
        "latitude": 13.016,
        "longitude": 80.241,
        "water_level_m": 4.15,
        "baseline_normal_m": 1.40,
        "warning_threshold_m": 3.10,
        "danger_threshold_m": 3.90,
        "battery_percentage": 92.0,
        "quality_flag": "VALID",
        "timestamp": datetime.now(timezone.utc).isoformat()
    },
    {
        "sensor_id": "SENSOR_BUCKINGHAM_SANTHOME",
        "sensor_name": "Buckingham Canal Lock Gauge - Santhome",
        "latitude": 13.033,
        "longitude": 80.276,
        "water_level_m": 2.95,
        "baseline_normal_m": 1.00,
        "warning_threshold_m": 2.50,
        "danger_threshold_m": 3.00,
        "battery_percentage": 97.0,
        "quality_flag": "VALID",
        "timestamp": datetime.now(timezone.utc).isoformat()
    },
    {
        "sensor_id": "SENSOR_PORUR_LAKE_WEIR",
        "sensor_name": "Porur Surplus Channel Weir",
        "latitude": 13.038,
        "longitude": 80.161,
        "water_level_m": 3.40,
        "baseline_normal_m": 1.10,
        "warning_threshold_m": 2.60,
        "danger_threshold_m": 3.20,
        "battery_percentage": 81.0,
        "quality_flag": "VALID",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
]

# 9. Synthetic Ground Reports (Citizen & Field Reports)
synthetic_flood_reports = [
    {
        "id": "REP_001_SAIDAPET",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "CITIZEN_MOBILE_APP",
        "data_category": "OBSERVED",
        "confidence": 0.88,
        "coordinates": {"latitude": 13.0175, "longitude": 80.2215, "altitude_m": 4.2},
        "reported_depth_cm": 95.0,
        "description": "Saidapet bazaar road submerged, water reaching hip height near causeway.",
        "water_flow": "rapid",
        "verification_status": "POSSIBLE_WATERLOGGING"
    },
    {
        "id": "REP_002_CHETPET",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "FIELD_VOLUNTEER",
        "data_category": "OBSERVED",
        "confidence": 0.92,
        "coordinates": {"latitude": 13.0725, "longitude": 80.2445, "altitude_m": 5.8},
        "reported_depth_cm": 60.0,
        "description": "Cooum overflow backflow into residential streets near Harrington road subways.",
        "water_flow": "moving",
        "verification_status": "POSSIBLE_WATERLOGGING"
    },
    {
        "id": "REP_003_KOTTURPURAM",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "EMERGENCY_HOTLINE",
        "data_category": "OBSERVED",
        "confidence": 0.85,
        "coordinates": {"latitude": 13.0155, "longitude": 80.2405, "altitude_m": 4.0},
        "reported_depth_cm": 110.0,
        "description": "Ground floor apartments inundated along River View Road. Power disconnected.",
        "water_flow": "standing",
        "verification_status": "POSSIBLE_WATERLOGGING"
    },
    {
        "id": "REP_004_MYLAPORE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "CITIZEN_MOBILE_APP",
        "data_category": "OBSERVED",
        "confidence": 0.78,
        "coordinates": {"latitude": 13.0360, "longitude": 80.2670, "altitude_m": 6.8},
        "reported_depth_cm": 25.0,
        "description": "Kutchery road storm drain overflowing, ankle deep water on roadway.",
        "water_flow": "moving",
        "verification_status": "POSSIBLE_WATERLOGGING"
    }
]

# 10. Sample Raster / Gridded Risk Tile Matrix (Metadata & Grid)
sample_raster_tiles = {
    "grid_metadata": {
        "crs": "EPSG:4326",
        "cell_size_deg": 0.02,
        "bbox": [80.15, 12.98, 80.29, 13.12],
        "rows": 7,
        "cols": 7,
        "source": "Sentinel-1_SAR_Synthetic_Water_Index"
    },
    "tiles": [
        {
            "tile_id": "TILE_ADYAR_LOWER",
            "bbox": [80.21, 13.00, 80.25, 13.04],
            "water_mask_coverage_pct": 68.4,
            "mean_elevation_m": 4.3,
            "estimated_inundation_depth_cm": 85.0
        },
        {
            "tile_id": "TILE_COOUM_CENTRAL",
            "bbox": [80.23, 13.06, 80.27, 13.10],
            "water_mask_coverage_pct": 54.2,
            "mean_elevation_m": 5.9,
            "estimated_inundation_depth_cm": 55.0
        },
        {
            "tile_id": "TILE_PORUR_RUNOFF",
            "bbox": [80.15, 13.02, 80.19, 13.06],
            "water_mask_coverage_pct": 49.0,
            "mean_elevation_m": 6.1,
            "estimated_inundation_depth_cm": 45.0
        },
        {
            "tile_id": "TILE_MYLAPORE_COASTAL",
            "bbox": [80.25, 13.02, 80.29, 13.06],
            "water_mask_coverage_pct": 18.5,
            "mean_elevation_m": 7.4,
            "estimated_inundation_depth_cm": 15.0
        }
    ]
}

# Write files
files = {
    "administrative_boundary.geojson": admin_boundary,
    "roads.geojson": roads,
    "hospitals.geojson": hospitals,
    "schools.geojson": schools,
    "shelters.geojson": shelters,
    "drainage_zones.geojson": drainage_zones,
    "rainfall_points.json": rainfall_points,
    "water_level_sensors.json": water_level_sensors,
    "synthetic_flood_reports.json": synthetic_flood_reports,
    "sample_raster_tiles.json": sample_raster_tiles
}

for filename, content in files.items():
    filepath = os.path.join(OUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)
    print(f"Generated {filepath}")

print("All sample geospatial data successfully generated!")
