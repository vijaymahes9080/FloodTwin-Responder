"""
Python module import adapter for 'risk-engine'.
"""

import importlib

_mod = importlib.import_module("risk-engine.engine")
FloodRiskEngine = _mod.FloodRiskEngine

__all__ = ["FloodRiskEngine"]
