"""
Model Context Protocol (MCP) Server Tests for FLOODTWIN RESPONDER.
"""

import json
import pytest
from mcp_server import FloodTwinMCPServer


def test_mcp_list_tools():
    server = FloodTwinMCPServer()
    req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    res_str = server.handle_json_rpc(req)
    res = json.loads(res_str)
    assert "result" in res
    tools = res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "get_latest_risk_tile" in tool_names
    assert "generate_response_brief" in tool_names
    assert "request_human_approval" in tool_names


def test_mcp_execute_risk_tile():
    server = FloodTwinMCPServer()
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_latest_risk_tile",
            "arguments": {"latitude": 13.018, "longitude": 80.222}
        }
    })
    res_str = server.handle_json_rpc(req)
    res = json.loads(res_str)
    assert "result" in res
    assert "score" in res["result"]


def test_mcp_reject_banned_tool():
    server = FloodTwinMCPServer()
    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "dispatch_real_siren_alarm",
            "arguments": {}
        }
    })
    res_str = server.handle_json_rpc(req)
    res = json.loads(res_str)
    assert "error" in res["result"]
