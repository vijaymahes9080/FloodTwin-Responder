"""
Python module import adapter for 'mcp-server'.
"""

import importlib

_mod = importlib.import_module("mcp-server.server")
FloodTwinMCPServer = _mod.FloodTwinMCPServer

__all__ = ["FloodTwinMCPServer"]
