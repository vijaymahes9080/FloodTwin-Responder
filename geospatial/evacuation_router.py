"""
Flood-Aware Evacuation & Emergency Routing Engine.
Calculates shortest safe routes to designated emergency shelters
while dynamically avoiding submerged causeways, railway subways, and impassable roads.
"""

from typing import List, Dict, Any, Optional, Tuple
import heapq
import math


class EvacuationRouter:
    """
    Graph-based pathfinding engine using modified Dijkstra algorithm with flood impedance weights.
    Impassable submerged road links are dynamically excised or given infinite cost.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, List[Tuple[str, float, str]]] = {}  # node -> [(neighbor, dist_km, edge_id)]
        self.edges: Dict[str, Dict[str, Any]] = {}

    def add_node(self, node_id: str, lat: float, lon: float, name: str = "", is_shelter: bool = False):
        self.nodes[node_id] = {
            "node_id": node_id,
            "lat": lat,
            "lon": lon,
            "name": name,
            "is_shelter": is_shelter
        }
        if node_id not in self.adj:
            self.adj[node_id] = []

    def add_road_segment(
        self,
        edge_id: str,
        u: str,
        v: str,
        distance_km: float,
        road_type: str = "arterial",
        water_depth_cm: float = 0.0,
        vehicle_clearance_limit_cm: float = 30.0
    ):
        """
        Adds bidirectional road connection between nodes.
        """
        is_blocked = water_depth_cm > vehicle_clearance_limit_cm
        self.edges[edge_id] = {
            "edge_id": edge_id,
            "u": u,
            "v": v,
            "distance_km": distance_km,
            "road_type": road_type,
            "water_depth_cm": water_depth_cm,
            "vehicle_clearance_limit_cm": vehicle_clearance_limit_cm,
            "is_blocked": is_blocked
        }
        self.adj[u].append((v, distance_km, edge_id))
        self.adj[v].append((u, distance_km, edge_id))

    def update_road_flood_status(self, edge_id: str, water_depth_cm: float):
        """
        Dynamically updates water depth from live sensor or citizen reports.
        """
        if edge_id in self.edges:
            e = self.edges[edge_id]
            e["water_depth_cm"] = water_depth_cm
            e["is_blocked"] = water_depth_cm > e["vehicle_clearance_limit_cm"]

    def find_safe_route(
        self,
        start_node: str,
        target_node: str,
        vehicle_max_wading_depth_cm: float = 30.0
    ) -> Dict[str, Any]:
        """
        Finds the shortest traversable route between two nodes avoiding blocked segments.
        Returns path sequence, distance in km, and list of traversed road IDs.
        """
        if start_node not in self.nodes or target_node not in self.nodes:
            return {"found": False, "error": "Start or target node not found."}

        # Dijkstra priority queue: (cumulative_distance, current_node, path_nodes, path_edges)
        pq = [(0.0, start_node, [start_node], [])]
        visited = set()

        while pq:
            dist, curr, path, edges_traversed = heapq.heappop(pq)

            if curr in visited:
                continue
            visited.add(curr)

            if curr == target_node:
                return {
                    "found": True,
                    "start_node": start_node,
                    "target_node": target_node,
                    "total_distance_km": round(dist, 2),
                    "path_nodes": path,
                    "edges_traversed": edges_traversed,
                    "is_direct_emergency_safe": True
                }

            for neighbor, edge_dist, edge_id in self.adj.get(curr, []):
                if neighbor in visited:
                    continue

                edge_info = self.edges[edge_id]
                # If water exceeds vehicle capability, skip road segment
                if edge_info["water_depth_cm"] > vehicle_max_wading_depth_cm:
                    continue

                # Water wading impedance penalty
                penalty = 1.0 + (edge_info["water_depth_cm"] / 20.0)
                effective_dist = edge_dist * penalty

                heapq.heappush(pq, (dist + effective_dist, neighbor, path + [neighbor], edges_traversed + [edge_id]))

        return {
            "found": False,
            "error": "No safe route available. All connecting paths are currently submerged or impassable."
        }

    def find_nearest_safe_shelter(self, origin_node: str, vehicle_clearance_cm: float = 30.0) -> Dict[str, Any]:
        """
        Evaluates routes to all available shelters and returns the closest safely accessible shelter.
        """
        shelters = [n for n, data in self.nodes.items() if data.get("is_shelter")]
        if not shelters:
            return {"found": False, "error": "No designated shelters in network."}

        best_route = None
        min_dist = float("inf")

        for shelter_id in shelters:
            route = self.find_safe_route(origin_node, shelter_id, vehicle_clearance_cm)
            if route.get("found") and route["total_distance_km"] < min_dist:
                min_dist = route["total_distance_km"]
                best_route = route
                best_route["shelter_name"] = self.nodes[shelter_id]["name"]

        if best_route:
            return best_route
        return {"found": False, "error": "All designated shelters are currently inaccessible by road."}
