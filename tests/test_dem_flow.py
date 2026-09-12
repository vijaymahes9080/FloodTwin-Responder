import pytest
from geospatial.dem_flow_analyzer import DEMFlowAnalyzer


def test_d8_flow_direction_and_accumulation():
    # Simple 3x3 V-shaped valley sloping downwards to center-bottom [2, 1]
    # Row 0: 30m, 30m, 30m
    # Row 1: 20m, 15m, 20m
    # Row 2: 10m,  5m, 10m
    elev = [
        [30.0, 30.0, 30.0],
        [20.0, 15.0, 20.0],
        [10.0,  5.0, 10.0],
    ]

    slopes = DEMFlowAnalyzer.calculate_slopes(elev, cell_size_m=10.0)
    assert len(slopes) == 3
    # Center cell [1, 1] (15m) drops to [2, 1] (5m) over 10m -> slope ~ 1.0 grad
    assert slopes[1][1] > 0.5

    flow_dirs = DEMFlowAnalyzer.calculate_d8_flow_direction(elev, cell_size_m=10.0)
    # Cell [1, 1] must flow South (code 4) to [2, 1]
    assert flow_dirs[1][1] == 4

    acc = DEMFlowAnalyzer.calculate_flow_accumulation(flow_dirs)
    # Bottom center [2, 1] should accumulate flow from upstream cells
    assert acc[2][1] > acc[0][1]


def test_topographic_wetness_index_computation():
    elev = [
        [30.0, 25.0, 20.0],
        [22.0, 12.0, 18.0],
        [15.0,  5.0, 12.0],
    ]

    res = DEMFlowAnalyzer.compute_topographic_wetness_index(elev, cell_size_m=10.0)
    assert "twi_grid" in res
    assert "top_hotspots" in res
    assert len(res["twi_grid"]) == 3
    # Flat, low valley cell [2, 1] should have higher TWI than high ridge [0, 0]
    assert res["twi_grid"][2][1] > res["twi_grid"][0][0]
