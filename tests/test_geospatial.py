"""
Geospatial Engine and Coordinate Tests for FLOODTWIN RESPONDER.
"""

import pytest
from geospatial.spatial_engine import (
    SpatialEngine,
    haversine_distance_km,
    point_in_polygon_ray_casting,
)


def test_haversine_known_distance():
    # Chennai Central to Saidapet Bridge is approx 8.0 - 8.5 km
    d = haversine_distance_km(13.0827, 80.2707, 13.0180, 80.2220)
    assert 7.5 < d < 9.5


def test_point_in_polygon_ray_casting():
    square = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0), (0.0, 0.0)]
    inside_pt = (2.0, 2.0)
    outside_pt = (5.0, 5.0)

    assert point_in_polygon_ray_casting(inside_pt, square) is True
    assert point_in_polygon_ray_casting(outside_pt, square) is False


def test_spatial_engine_nearby_assets():
    engine = SpatialEngine()
    sample_assets = [
        {
            "id": "HOSP_A",
            "properties": {"name": "General Hospital", "elevation_m": 4.0},
            "geometry": {"type": "Point", "coordinates": [80.225, 13.020]}
        },
        {
            "id": "HOSP_B",
            "properties": {"name": "Distant Hospital", "elevation_m": 12.0},
            "geometry": {"type": "Point", "coordinates": [80.500, 13.500]}
        }
    ]

    nearby = engine.find_nearby_assets(13.018, 80.222, sample_assets, radius_km=3.0)
    assert len(nearby) == 1
    assert nearby[0]["id"] == "HOSP_A"
    assert nearby[0]["exposure_tier"] == "CRITICAL"


def test_spatial_engine_water_spread_change():
    engine = SpatialEngine()
    poly_base = [(80.20, 13.00), (80.22, 13.00), (80.22, 13.02), (80.20, 13.02), (80.20, 13.00)]
    poly_curr = [(80.19, 12.99), (80.23, 12.99), (80.23, 13.03), (80.19, 13.03), (80.19, 12.99)]

    res = engine.compute_water_spread_change(poly_base, poly_curr)
    assert res["spread_status"] == "EXPANDING"
    assert res["area_change_sq_km"] > 0
