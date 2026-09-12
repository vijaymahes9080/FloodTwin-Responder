"""
Urban Stormwater & Drainage Network Graph Engine.
Models hydraulic capacities of stormwater conduits, open canals, and culverts.
Detects surcharge bottlenecks and hydraulic backflow risks when receiving waterbodies rise.
"""

from typing import List, Dict, Any, Optional
import math


class DrainageNetworkGraph:
    """
    Directed graph representation of urban drainage conduits.
    Supports hydraulic capacity analysis (Manning's open channel flow approximation)
    and tailwater backflow condition diagnostics.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Dict[str, Any]] = {}

    def add_node(self, node_id: str, elevation_m: float, node_type: str = "junction", lat: float = 0.0, lon: float = 0.0):
        """
        Adds a junction, inlet, or outfall node to the network.
        """
        self.nodes[node_id] = {
            "node_id": node_id,
            "elevation_m": elevation_m,
            "type": node_type,  # 'inlet', 'junction', 'outfall', 'pump_station'
            "lat": lat,
            "lon": lon,
            "head_m": elevation_m
        }

    def add_conduit(
        self,
        edge_id: str,
        from_node: str,
        to_node: str,
        length_m: float,
        width_m: float,
        depth_m: float,
        mannings_n: float = 0.015,
        siltation_percent: float = 0.0
    ):
        """
        Adds a directed conduit or canal segment from upstream to downstream.
        Calculates design gravity capacity using Manning's Equation:
        Q = (1 / n) * A * R^(2/3) * S^(1/2)
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError(f"Nodes {from_node} and {to_node} must exist in the drainage network.")

        elev_from = self.nodes[from_node]["elevation_m"]
        elev_to = self.nodes[to_node]["elevation_m"]
        slope = max(0.0005, (elev_from - elev_to) / max(1.0, length_m))

        effective_depth = depth_m * (1.0 - (siltation_percent / 100.0))
        area = width_m * effective_depth
        wetted_perimeter = width_m + 2.0 * effective_depth
        hydraulic_radius = area / max(0.1, wetted_perimeter)

        # Manning's discharge capacity in m3/s
        design_capacity = (1.0 / mannings_n) * area * (hydraulic_radius ** (2.0 / 3.0)) * math.sqrt(slope)

        self.edges[edge_id] = {
            "edge_id": edge_id,
            "from_node": from_node,
            "to_node": to_node,
            "length_m": length_m,
            "width_m": width_m,
            "depth_m": depth_m,
            "effective_depth_m": round(effective_depth, 2),
            "siltation_pct": siltation_percent,
            "slope": round(slope, 5),
            "design_capacity_m3s": round(design_capacity, 2),
            "current_flow_m3s": 0.0,
            "is_backflow": False
        }

    def simulate_storm_inflow(
        self,
        inflows_m3s: Dict[str, float],
        tailwater_elevations_m: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Simulates stormwater inflows and assesses surcharge and backflow conditions.
        If tailwater elevation at an outfall exceeds the upstream node, backflow is triggered.
        """
        tailwater = tailwater_elevations_m or {}
        choke_points = []
        backflows = []

        # Update heads with tailwater levels
        for node_id, tw_level in tailwater.items():
            if node_id in self.nodes:
                self.nodes[node_id]["head_m"] = max(self.nodes[node_id]["elevation_m"], tw_level)

        # Assign flow to edges
        edge_results = {}
        for edge_id, edge in self.edges.items():
            u, v = edge["from_node"], edge["to_node"]
            inflow = inflows_m3s.get(u, 0.0)

            # Check hydraulic gradient
            u_head = self.nodes[u]["head_m"]
            v_head = self.nodes[v]["head_m"]

            is_backflow = False
            if v_head > u_head:
                is_backflow = True
                backflows.append({
                    "edge_id": edge_id,
                    "downstream_node": v,
                    "upstream_node": u,
                    "water_level_differential_m": round(v_head - u_head, 2)
                })

            capacity = edge["design_capacity_m3s"]
            utilization = round((inflow / max(0.01, capacity)) * 100.0, 1)

            is_choked = utilization >= 85.0 or is_backflow
            if is_choked:
                choke_points.append({
                    "edge_id": edge_id,
                    "from_node": u,
                    "to_node": v,
                    "utilization_pct": utilization,
                    "is_backflow": is_backflow,
                    "capacity_m3s": capacity,
                    "inflow_m3s": inflow
                })

            edge_results[edge_id] = {
                "inflow_m3s": inflow,
                "capacity_m3s": capacity,
                "utilization_pct": utilization,
                "is_backflow": is_backflow
            }

        return {
            "total_conduits": len(self.edges),
            "choke_point_count": len(choke_points),
            "backflow_count": len(backflows),
            "choke_points": choke_points,
            "backflows": backflows,
            "edge_diagnostics": edge_results
        }
