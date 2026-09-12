"""
Geospatial Asset and Shelter query endpoints for FLOODTWIN RESPONDER.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from geospatial.spatial_engine import SpatialEngine
from backend.app.services.store import store

router = APIRouter(tags=["Assets & Shelters"])
spatial_engine = SpatialEngine(admin_boundaries=store.administrative_boundaries)


@router.get("/assets/nearby")
def get_nearby_assets(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    radius_km: float = Query(3.0, ge=0.1, le=50.0)
):
    """Locates hospitals, schools, and essential infrastructure within radius_km."""
    results = spatial_engine.find_nearby_assets(
        lat=latitude,
        lon=longitude,
        assets=store.critical_assets,
        radius_km=radius_km
    )
    return {
        "query_point": {"latitude": latitude, "longitude": longitude, "crs": "EPSG:4326"},
        "radius_km": radius_km,
        "count": len(results),
        "assets": results
    }


@router.get("/shelters/nearby")
def get_nearby_shelters(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    max_distance_km: float = Query(8.0, ge=0.5, le=50.0)
):
    """Locates active disaster shelters with available beds within max_distance_km."""
    results = spatial_engine.find_nearby_shelters(
        lat=latitude,
        lon=longitude,
        shelters=store.shelters,
        max_distance_km=max_distance_km
    )
    return {
        "query_point": {"latitude": latitude, "longitude": longitude, "crs": "EPSG:4326"},
        "max_distance_km": max_distance_km,
        "count": len(results),
        "shelters": results
    }


@router.get("/assets/boundaries")
def get_admin_boundaries():
    """Returns official administrative flood management zones in GeoJSON."""
    return store.administrative_boundaries


@router.get("/assets/drainage")
def get_drainage_corridors():
    """Returns river flood carry corridors and spillway buffer geometries in GeoJSON."""
    return store.drainage_corridors
