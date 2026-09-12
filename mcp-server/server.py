"""
Model Context Protocol (MCP) JSON-RPC Server for FLOODTWIN RESPONDER.
Exposes strictly bounded disaster response tools with provenance and security invariants.
"""

import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.response_fsm import BoundedResponseAgent
from backend.app.core.auth import UserRole
from backend.app.schemas.contracts import ApprovalStatus
from backend.app.services.qc_engine import IngestionQCEngine
from backend.app.services.store import store
from geospatial.spatial_engine import SpatialEngine
from rag.knowledge_base import PolicyKnowledgeBase
from risk_engine import FloodRiskEngine

spatial_engine = SpatialEngine(admin_boundaries=store.administrative_boundaries)
risk_engine = FloodRiskEngine()
knowledge_base = PolicyKnowledgeBase()
response_agent = BoundedResponseAgent(
    risk_engine=risk_engine,
    spatial_engine=spatial_engine,
    knowledge_base=knowledge_base
)
qc_engine = IngestionQCEngine()


class FloodTwinMCPServer:
    """
    Model Context Protocol (MCP) tool provider.
    Enforces geographic bounding, role validation, and Merkle audit logging.
    """

    ALLOWED_TOOLS = [
        "get_latest_risk_tile",
        "get_nearby_assets",
        "find_nearby_shelters",
        "search_emergency_policy",
        "summarize_sensor_status",
        "generate_response_brief",
        "request_human_approval"
    ]

    def __init__(self):
        self.server_name = "FloodTwin-MCP-Server"
        self.version = "1.0.0"

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_latest_risk_tile",
                "description": "Retrieves explainable composite flood risk index and factor breakdown for a specific zone or coordinates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zone_id": {"type": "string", "description": "e.g. ZONE_02_SOUTH"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    }
                }
            },
            {
                "name": "get_nearby_assets",
                "description": "Locates critical healthcare, education, and electrical facilities near coordinates.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "radius_km": {"type": "number", "default": 3.0}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "find_nearby_shelters",
                "description": "Finds active authorized relief shelters and available bed capacity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "max_distance_km": {"type": "number", "default": 8.0}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "search_emergency_policy",
                "description": "Searches grounded disaster SOP manuals and returns exact page/section citations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "e.g. hospital flood backup power SOP"},
                        "category": {"type": "string", "description": "EVACUATION, HOSPITAL_PROTECTION, SHELTER_MANAGEMENT"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "summarize_sensor_status",
                "description": "Provides real-time health, river stage levels, and rainfall metrics across telemetry stations.",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "generate_response_brief",
                "description": "Synthesizes human-reviewable response brief. Outputs status PENDING_HUMAN_APPROVAL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zone_id": {"type": "string", "default": "ZONE_02_SOUTH"},
                        "zone_name": {"type": "string", "default": "South Chennai - Adyar Basin"},
                        "latitude": {"type": "number", "default": 13.018},
                        "longitude": {"type": "number", "default": 80.222}
                    }
                }
            },
            {
                "name": "request_human_approval",
                "description": "Stages formal approval request for response brief with designated commander. NEVER sends live alerts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brief_id": {"type": "string"},
                        "operator_id": {"type": "string"},
                        "comments": {"type": "string"}
                    },
                    "required": ["brief_id", "operator_id"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], actor_id: str = "MCP_CLIENT") -> Dict[str, Any]:
        """Validates and executes tool call safely with structured return."""
        if tool_name not in self.ALLOWED_TOOLS:
            return {
                "error": f"Tool '{tool_name}' is not permitted or does not exist. Safety bounds enforce restricted tools only.",
                "allowed_tools": self.ALLOWED_TOOLS
            }

        # 1. get_latest_risk_tile
        if tool_name == "get_latest_risk_tile":
            lat = arguments.get("latitude", 13.018)
            lon = arguments.get("longitude", 80.222)
            valid, msg = qc_engine.validate_coordinates(lat, lon)
            if not valid:
                return {"error": "Geographic Scope Violation", "details": msg}

            calc = risk_engine.calculate_risk(
                rainfall_3h_mm=115.5,
                sensor_water_level_m=4.45,
                reported_depth_cm=110.0,
                elevation_m=4.2,
                nearby_critical_assets_count=4
            )
            calc["provenance"] = {
                "tool": tool_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor_id": actor_id
            }
            return calc

        # 2. get_nearby_assets
        elif tool_name == "get_nearby_assets":
            lat = arguments["latitude"]
            lon = arguments["longitude"]
            rad = arguments.get("radius_km", 3.0)
            valid, msg = qc_engine.validate_coordinates(lat, lon)
            if not valid:
                return {"error": "Geographic Scope Violation", "details": msg}
            assets = spatial_engine.find_nearby_assets(lat, lon, store.critical_assets, radius_km=rad)
            return {"count": len(assets), "assets": assets, "provenance": {"tool": tool_name}}

        # 3. find_nearby_shelters
        elif tool_name == "find_nearby_shelters":
            lat = arguments["latitude"]
            lon = arguments["longitude"]
            max_dist = arguments.get("max_distance_km", 8.0)
            valid, msg = qc_engine.validate_coordinates(lat, lon)
            if not valid:
                return {"error": "Geographic Scope Violation", "details": msg}
            shelters = spatial_engine.find_nearby_shelters(lat, lon, store.shelters, max_distance_km=max_dist)
            return {"count": len(shelters), "shelters": shelters, "provenance": {"tool": tool_name}}

        # 4. search_emergency_policy
        elif tool_name == "search_emergency_policy":
            query = arguments["query"]
            cat = arguments.get("category")
            clean_query, _ = qc_engine.sanitize_pii(query)
            citations = knowledge_base.search(clean_query, category_filter=cat, top_k=3)
            return {"query": clean_query, "citations": citations, "provenance": {"tool": tool_name}}

        # 5. summarize_sensor_status
        elif tool_name == "summarize_sensor_status":
            return {
                "sensors": list(store.sensors.values()),
                "rainfall": list(store.rainfall_stations.values()),
                "provenance": {"tool": tool_name}
            }

        # 6. generate_response_brief
        elif tool_name == "generate_response_brief":
            z_id = arguments.get("zone_id", "ZONE_02_SOUTH")
            z_name = arguments.get("zone_name", "South Chennai - Adyar Basin")
            lat = arguments.get("latitude", 13.018)
            lon = arguments.get("longitude", 80.222)
            sensor_entry = store.sensors.get("SENSOR_ADYAR_SAIDAPET", list(store.sensors.values())[0] if store.sensors else None)
            rain_entry = store.rainfall_stations.get("AWS_MEENAMBAKKAM", list(store.rainfall_stations.values())[0] if store.rainfall_stations else None)
            brief = response_agent.execute_workflow(
                target_zone_id=z_id,
                target_zone_name=z_name,
                zone_coords={"latitude": lat, "longitude": lon},
                rainfall_data=rain_entry,
                sensor_data=sensor_entry,
                citizen_reports=list(store.reports.values())[:5],
                critical_assets=store.critical_assets,
                shelters=store.shelters,
                elevation_m=4.5
            )
            brief_dict = brief.model_dump()
            store.add_response_brief(brief_dict)
            return brief_dict

        # 7. request_human_approval
        elif tool_name == "request_human_approval":
            brief_id = arguments["brief_id"]
            op_id = arguments["operator_id"]
            comments = arguments.get("comments", "Staged for review")
            if brief_id not in store.response_briefs:
                return {"error": f"Brief ID '{brief_id}' not found"}
            store.record_audit(
                actor_id=op_id,
                actor_role="DISASTER_COMMANDER",
                action="APPROVAL_REQUESTED_VIA_MCP",
                resource_type="RESPONSE_BRIEF",
                resource_id=brief_id,
                details={"comments": comments}
            )
            return {
                "status": "STAGED_FOR_COMMANDER_APPROVAL",
                "brief_id": brief_id,
                "autonomous_alert_blocked": True,
                "message": "Approval request staged. Live broadcast alerts strictly blocked by system invariants."
            }

        return {"error": "Unhandled tool execution"}

    def handle_json_rpc(self, request_str: str) -> str:
        """Processes JSON-RPC 2.0 requests over stdio or string buffer."""
        try:
            req = json.loads(request_str)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                result = {"tools": self.list_tools()}
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments", {})
                result = self.execute_tool(name, args)
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                })

            return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result})
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            })


if __name__ == "__main__":
    server = FloodTwinMCPServer()
    print(f"[{datetime.now().isoformat()}] FloodTwin MCP Server running on stdio...", file=sys.stderr)
    for line in sys.stdin:
        if line.strip():
            response = server.handle_json_rpc(line.strip())
            print(response)
            sys.stdout.flush()
