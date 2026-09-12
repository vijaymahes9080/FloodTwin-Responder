"""
Sentinel-1 Synthetic Aperture Radar (SAR) Water and Inundation Detection Engine.
Implements Lee speckle reduction, Otsu automatic binarization, and dual-temporal
backscatter difference (-dB) change detection for flood extent mapping.
"""

from typing import List, Dict, Any, Tuple, Optional
import math


class SARWaterDetector:
    """
    Analyzes Sentinel-1 C-band SAR backscatter matrices (expressed in decibels, dB)
    to identify permanent water bodies and newly inundated flood extents.
    """

    DEFAULT_WATER_THRESHOLD_DB = -17.5  # Typical C-band VV/VH water backscatter threshold in dB
    CHANGE_THRESHOLD_DB = -3.5          # Relative drop in backscatter indicating flood inundation

    @staticmethod
    def lee_filter(matrix: List[List[float]], window_size: int = 3) -> List[List[float]]:
        """
        Applies Lee adaptive speckle filter to radar raster grid in dB domain.
        Preserves edges while smoothing multiplicative speckle noise in homogeneous regions.
        """
        rows = len(matrix)
        if rows == 0:
            return []
        cols = len(matrix[0])
        half_w = window_size // 2
        filtered = [[0.0 for _ in range(cols)] for _ in range(rows)]

        # In log/dB domain, SAR speckle noise variance is approximately constant (~1.5 dB^2)
        noise_var_db = 1.5

        for r in range(rows):
            for c in range(cols):
                vals = []
                for dr in range(-half_w, half_w + 1):
                    for dc in range(-half_w, half_w + 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            vals.append(matrix[nr][nc])

                mean_val = sum(vals) / len(vals)
                var_val = sum((x - mean_val) ** 2 for x in vals) / len(vals)

                if var_val > noise_var_db:
                    weight = min(1.0, (var_val - noise_var_db) / max(var_val, 1e-4))
                else:
                    weight = 0.0

                filtered[r][c] = round(mean_val + weight * (matrix[r][c] - mean_val), 3)

        return filtered

    @staticmethod
    def compute_otsu_threshold(matrix: List[List[float]], min_val: float = -30.0, max_val: float = 0.0) -> float:
        """
        Computes Otsu's optimal bimodal threshold over SAR backscatter distribution.
        Separates specular reflector water pixels (dark mode) from textured land (bright mode).
        """
        flat = [val for row in matrix for val in row if min_val <= val <= max_val]
        if not flat:
            return SARWaterDetector.DEFAULT_WATER_THRESHOLD_DB

        num_bins = 60
        bin_width = (max_val - min_val) / num_bins
        hist = [0] * num_bins

        for val in flat:
            b = int((val - min_val) / bin_width)
            b = max(0, min(num_bins - 1, b))
            hist[b] += 1

        total_pixels = len(flat)
        sum_total = sum(i * hist[i] for i in range(num_bins))

        weight_bg = 0
        sum_bg = 0
        max_variance = -1.0
        best_bin = 0

        for t in range(num_bins):
            weight_bg += hist[t]
            if weight_bg == 0:
                continue
            weight_fg = total_pixels - weight_bg
            if weight_fg == 0:
                break

            sum_bg += t * hist[t]
            mean_bg = sum_bg / weight_bg
            mean_fg = (sum_total - sum_bg) / weight_fg

            between_var = weight_bg * weight_fg * ((mean_bg - mean_fg) ** 2)
            if between_var > max_variance:
                max_variance = between_var
                best_bin = t

        optimal_db = min_val + (best_bin + 0.5) * bin_width
        return round(optimal_db, 2)

    @classmethod
    def detect_inundation(
        cls,
        post_event_grid: List[List[float]],
        pre_event_grid: Optional[List[List[float]]] = None,
        pixel_spacing_m: float = 10.0,
        custom_threshold: Optional[float] = None,
        apply_filter: bool = True
    ) -> Dict[str, Any]:
        """
        Detects flood water pixels using post-event SAR backscatter and optional pre-event baseline.
        Returns pixel metrics, water area in hectares, and flood mask grid (1=water, 0=land).
        """
        filtered_post = cls.lee_filter(post_event_grid) if apply_filter else post_event_grid
        threshold_db = custom_threshold or cls.compute_otsu_threshold(filtered_post)

        rows = len(post_event_grid)
        cols = len(post_event_grid[0]) if rows > 0 else 0
        total_pixels = rows * cols

        water_mask = [[0 for _ in range(cols)] for _ in range(rows)]
        newly_flooded_pixels = 0
        total_water_pixels = 0

        has_pre = (pre_event_grid is not None and len(pre_event_grid) == rows and len(pre_event_grid[0]) == cols)
        filtered_pre = (cls.lee_filter(pre_event_grid) if apply_filter else pre_event_grid) if has_pre else None

        for r in range(rows):
            for c in range(cols):
                is_water = filtered_post[r][c] <= threshold_db
                if is_water:
                    water_mask[r][c] = 1
                    total_water_pixels += 1

                    if has_pre:
                        # If pre-event was land (backscatter was higher by change threshold)
                        db_drop = filtered_post[r][c] - filtered_pre[r][c]
                        if db_drop <= cls.CHANGE_THRESHOLD_DB:
                            newly_flooded_pixels += 1
                    else:
                        newly_flooded_pixels += 1

        pixel_area_m2 = pixel_spacing_m * pixel_spacing_m
        total_water_ha = round((total_water_pixels * pixel_area_m2) / 10000.0, 2)
        newly_flooded_ha = round((newly_flooded_pixels * pixel_area_m2) / 10000.0, 2)

        return {
            "applied_threshold_db": threshold_db,
            "total_pixels": total_pixels,
            "water_pixels": total_water_pixels,
            "newly_flooded_pixels": newly_flooded_pixels,
            "total_water_hectares": total_water_ha,
            "newly_flooded_hectares": newly_flooded_ha,
            "flood_fraction": round(total_water_pixels / max(1, total_pixels), 4),
            "water_mask": water_mask
        }
