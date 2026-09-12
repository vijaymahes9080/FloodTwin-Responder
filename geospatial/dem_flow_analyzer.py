"""
Digital Elevation Model (DEM) Hydrological & Flow Accumulation Analyzer.
Calculates D8 flow direction, upstream flow accumulation, terrain slope,
and Topographic Wetness Index (TWI) for physical flood susceptibility modeling.
"""

from typing import List, Dict, Any, Tuple
import math


class DEMFlowAnalyzer:
    """
    Computes topographic hydrologic indices from raster digital elevation matrices.
    TWI = ln(a / tan(beta)), where 'a' is specific catchment area and 'beta' is slope.
    """

    # D8 Direction encoding: 1=E, 2=SE, 4=S, 8=SW, 16=W, 32=NW, 64=N, 128=NE
    D8_OFFSETS = [
        (0, 1, 1),    # E
        (1, 1, 2),    # SE
        (1, 0, 4),    # S
        (1, -1, 8),   # SW
        (0, -1, 16),  # W
        (-1, -1, 32), # NW
        (-1, 0, 64),  # N
        (-1, 1, 128)  # NE
    ]

    @staticmethod
    def calculate_slopes(elevation_grid: List[List[float]], cell_size_m: float = 10.0) -> List[List[float]]:
        """
        Computes maximum downward slope (radians) for each cell using Zevenbergen-Thorne / Horn gradient.
        Clamps minimum slope to 0.001 rad to prevent division by zero in flat sinks.
        """
        rows = len(elevation_grid)
        cols = len(elevation_grid[0]) if rows > 0 else 0
        slopes = [[0.001 for _ in range(cols)] for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                elev = elevation_grid[r][c]
                max_gradient = 0.0

                for dr, dc, _ in DEMFlowAnalyzer.D8_OFFSETS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        dist = math.sqrt(dr*dr + dc*dc) * cell_size_m
                        drop = elev - elevation_grid[nr][nc]
                        if drop > 0:
                            grad = drop / dist
                            if grad > max_gradient:
                                max_gradient = grad

                # Slope angle in radians: beta = arctan(gradient)
                slopes[r][c] = max(0.001, math.atan(max_gradient))

        return slopes

    @staticmethod
    def calculate_d8_flow_direction(elevation_grid: List[List[float]], cell_size_m: float = 10.0) -> List[List[int]]:
        """
        Computes D8 flow direction raster. Each cell points to neighbor with steepest descent.
        Pits/sinks with no descent are assigned 0.
        """
        rows = len(elevation_grid)
        cols = len(elevation_grid[0]) if rows > 0 else 0
        flow_dirs = [[0 for _ in range(cols)] for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                elev = elevation_grid[r][c]
                max_slope = 0.0
                best_code = 0

                for dr, dc, code in DEMFlowAnalyzer.D8_OFFSETS:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        dist = math.sqrt(dr*dr + dc*dc) * cell_size_m
                        drop = elev - elevation_grid[nr][nc]
                        if drop > 0:
                            slope = drop / dist
                            if slope > max_slope:
                                max_slope = slope
                                best_code = code

                flow_dirs[r][c] = best_code

        return flow_dirs

    @staticmethod
    def calculate_flow_accumulation(flow_dirs: List[List[int]]) -> List[List[int]]:
        """
        Computes the number of upstream cells draining into each cell based on D8 directions.
        Every cell has a baseline contribution of 1 (itself).
        """
        rows = len(flow_dirs)
        cols = len(flow_dirs[0]) if rows > 0 else 0
        acc = [[1 for _ in range(cols)] for _ in range(rows)]

        # Code to coordinate delta map
        code_map = {code: (dr, dc) for dr, dc, code in DEMFlowAnalyzer.D8_OFFSETS}

        # Iterative accumulation until topological convergence
        changed = True
        iterations = 0
        max_iter = rows * cols

        while changed and iterations < max_iter:
            changed = False
            iterations += 1
            for r in range(rows):
                for c in range(cols):
                    code = flow_dirs[r][c]
                    if code in code_map:
                        dr, dc = code_map[code]
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            # In-flow accumulation will propagate downstream
                            pass

        # Exact topological sort accumulation:
        # 1. Compute in-degrees
        in_degree = [[0 for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                code = flow_dirs[r][c]
                if code in code_map:
                    dr, dc = code_map[code]
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        in_degree[nr][nc] += 1

        # 2. Queue sources (in-degree == 0)
        queue = [(r, c) for r in range(rows) for c in range(cols) if in_degree[r][c] == 0]

        while queue:
            curr_r, curr_c = queue.pop(0)
            code = flow_dirs[curr_r][curr_c]
            if code in code_map:
                dr, dc = code_map[code]
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    acc[nr][nc] += acc[curr_r][curr_c]
                    in_degree[nr][nc] -= 1
                    if in_degree[nr][nc] == 0:
                        queue.append((nr, nc))

        return acc

    @classmethod
    def compute_topographic_wetness_index(
        cls,
        elevation_grid: List[List[float]],
        cell_size_m: float = 10.0
    ) -> Dict[str, Any]:
        """
        Computes full hydrologic package: Slopes, D8 Flow Directions, Flow Accumulation,
        and Topographic Wetness Index (TWI). High TWI (>8.0) signals high waterlogging susceptibility.
        """
        rows = len(elevation_grid)
        cols = len(elevation_grid[0]) if rows > 0 else 0

        slopes = cls.calculate_slopes(elevation_grid, cell_size_m)
        flow_dirs = cls.calculate_d8_flow_direction(elevation_grid, cell_size_m)
        flow_acc = cls.calculate_flow_accumulation(flow_dirs)

        twi_grid = [[0.0 for _ in range(cols)] for _ in range(rows)]
        hotspots = []

        for r in range(rows):
            for c in range(cols):
                # Specific catchment area a = (FlowAcc * cell_size)
                # TWI = ln( a / tan(slope) )
                sca = flow_acc[r][c] * cell_size_m
                tan_slope = max(0.001, math.tan(slopes[r][c]))
                twi = math.log(sca / tan_slope)
                twi_grid[r][c] = round(twi, 2)

                if twi >= 8.5:
                    hotspots.append({
                        "row": r,
                        "col": c,
                        "twi": round(twi, 2),
                        "flow_accumulation": flow_acc[r][c],
                        "elevation_m": elevation_grid[r][c]
                    })

        return {
            "cell_size_m": cell_size_m,
            "twi_grid": twi_grid,
            "flow_accumulation_grid": flow_acc,
            "slopes_rad": slopes,
            "hotspot_count": len(hotspots),
            "top_hotspots": sorted(hotspots, key=lambda x: x["twi"], reverse=True)[:5]
        }
