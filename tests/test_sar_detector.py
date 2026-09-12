import pytest
from geospatial.sar_water_detector import SARWaterDetector


def test_lee_filter_smoothing():
    # 5x5 noisy matrix
    noisy_grid = [
        [-15.0, -14.0, -16.0, -15.0, -14.0],
        [-14.0, -10.0, -15.0, -14.0, -15.0],  # -10.0 is a bright speckle outlier
        [-16.0, -15.0, -15.5, -16.0, -15.0],
        [-15.0, -16.0, -15.0, -14.0, -15.0],
        [-14.0, -15.0, -16.0, -15.0, -14.0],
    ]
    filtered = SARWaterDetector.lee_filter(noisy_grid, window_size=3)
    assert len(filtered) == 5
    assert len(filtered[0]) == 5
    # The center speckle outlier (-10.0) should be smoothed down towards -14 / -15 dB
    assert filtered[1][1] < -11.0


def test_otsu_threshold_computation():
    # Bimodal matrix: water (-22 dB) vs land (-10 dB)
    grid = [
        [-22.0, -21.0, -23.0, -10.0, -9.0],
        [-22.5, -21.5, -22.0, -9.5, -10.5],
        [-21.0, -22.0, -20.5, -11.0, -10.0],
    ]
    threshold = SARWaterDetector.compute_otsu_threshold(grid)
    # The threshold should be somewhere between water (-22) and land (-10)
    assert -21.0 <= threshold <= -12.0


def test_sar_inundation_change_detection():
    # Pre-event (dry land, ~ -10 dB)
    pre_event = [
        [-10.0, -11.0, -10.0],
        [-10.5, -10.0, -11.0],
        [-9.5,  -10.0, -10.5],
    ]
    # Post-event: center and bottom-right flooded (-22 dB)
    post_event = [
        [-10.0, -11.0, -10.0],
        [-10.5, -22.0, -11.0],
        [-9.5,  -10.0, -22.5],
    ]

    res = SARWaterDetector.detect_inundation(
        post_event_grid=post_event,
        pre_event_grid=pre_event,
        pixel_spacing_m=10.0,
        custom_threshold=-18.0,
        apply_filter=False
    )

    assert res["water_pixels"] == 2
    assert res["newly_flooded_pixels"] == 2
    assert res["total_pixels"] == 9
    assert res["total_water_hectares"] == 0.02  # 2 * 100m2 = 200m2 = 0.02 ha
    assert res["water_mask"][1][1] == 1
    assert res["water_mask"][2][2] == 1
    assert res["water_mask"][0][0] == 0
