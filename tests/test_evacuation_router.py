import pytest
from geospatial.evacuation_router import EvacuationRouter


def test_evacuation_routing_clear_path():
    router = EvacuationRouter()
    # A -> B -> C (Shelter)
    router.add_node("A", lat=11.00, lon=76.95, name="Residential Locality")
    router.add_node("B", lat=11.01, lon=76.96, name="Main Junction")
    router.add_node("S1", lat=11.02, lon=76.97, name="Government College Relief Shelter", is_shelter=True)

    router.add_road_segment("R1", "A", "B", distance_km=2.0, water_depth_cm=0.0)
    router.add_road_segment("R2", "B", "S1", distance_km=3.0, water_depth_cm=0.0)

    res = router.find_safe_route("A", "S1")
    assert res["found"] is True
    assert res["total_distance_km"] == 5.0
    assert res["path_nodes"] == ["A", "B", "S1"]


def test_evacuation_rerouting_around_submerged_segment():
    router = EvacuationRouter()
    # Path 1: A -> B -> S1 (Direct, but B is submerged)
    # Path 2: A -> D -> S1 (Detour, but dry)
    router.add_node("A", lat=11.00, lon=76.95)
    router.add_node("B", lat=11.01, lon=76.96)
    router.add_node("D", lat=10.99, lon=76.97)
    router.add_node("S1", lat=11.02, lon=76.97, is_shelter=True, name="High School Shelter")

    # Short direct route (submerged with 70cm water)
    router.add_road_segment("R_SUBWAY", "A", "B", distance_km=1.5, water_depth_cm=70.0)
    router.add_road_segment("R_TO_SHELTER", "B", "S1", distance_km=1.5, water_depth_cm=0.0)

    # Detour route (dry, 4km total)
    router.add_road_segment("R_DETOUR1", "A", "D", distance_km=2.0, water_depth_cm=0.0)
    router.add_road_segment("R_DETOUR2", "D", "S1", distance_km=2.0, water_depth_cm=0.0)

    # Standard vehicle with 30cm clearance limit
    res = router.find_nearest_safe_shelter("A", vehicle_clearance_cm=30.0)

    assert res["found"] is True
    assert res["target_node"] == "S1"
    # The router MUST divert through D and avoid the submerged road R_SUBWAY
    assert "D" in res["path_nodes"]
    assert "B" not in res["path_nodes"]
    assert "R_SUBWAY" not in res["edges_traversed"]
