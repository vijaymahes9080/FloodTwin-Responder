import pytest
from geospatial.drainage_graph import DrainageNetworkGraph


def test_drainage_graph_capacity_and_choke():
    graph = DrainageNetworkGraph()
    # Inflow node at elevation 10m, outfall at 5m
    graph.add_node("INLET_A", elevation_m=10.0, node_type="inlet")
    graph.add_node("OUTFALL_B", elevation_m=5.0, node_type="outfall")

    # 100m long canal, 2m wide, 1m deep
    graph.add_conduit(
        edge_id="C_MAIN",
        from_node="INLET_A",
        to_node="OUTFALL_B",
        length_m=100.0,
        width_m=2.0,
        depth_m=1.0,
        mannings_n=0.015,
        siltation_percent=0.0
    )

    cap = graph.edges["C_MAIN"]["design_capacity_m3s"]
    assert cap > 5.0  # reasonable Manning gravity discharge

    # Normal simulation
    sim1 = graph.simulate_storm_inflow(inflows_m3s={"INLET_A": 2.0})
    assert sim1["choke_point_count"] == 0

    # Overload simulation
    sim2 = graph.simulate_storm_inflow(inflows_m3s={"INLET_A": cap * 1.1})
    assert sim2["choke_point_count"] == 1
    assert sim2["choke_points"][0]["edge_id"] == "C_MAIN"


def test_drainage_graph_backflow_condition():
    graph = DrainageNetworkGraph()
    graph.add_node("JUNCTION_1", elevation_m=6.0, node_type="junction")
    graph.add_node("RIVER_OUTFALL", elevation_m=5.0, node_type="outfall")

    graph.add_conduit(
        edge_id="CANAL_OUTFALL",
        from_node="JUNCTION_1",
        to_node="RIVER_OUTFALL",
        length_m=50.0,
        width_m=2.0,
        depth_m=1.0
    )

    # If river flood level rises to 8.0m (exceeding junction at 6.0m)
    sim = graph.simulate_storm_inflow(
        inflows_m3s={"JUNCTION_1": 1.0},
        tailwater_elevations_m={"RIVER_OUTFALL": 8.0}
    )

    assert sim["backflow_count"] == 1
    assert sim["backflows"][0]["edge_id"] == "CANAL_OUTFALL"
    assert sim["backflows"][0]["water_level_differential_m"] == 2.0
