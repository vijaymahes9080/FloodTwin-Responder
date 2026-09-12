import pytest
from agent.safety_invariant_verifier import SafetyInvariantVerifier


def test_invariant_no_unsupervised_states():
    res = SafetyInvariantVerifier.verify_no_unsupervised_states_reachable()
    assert res["invariant_holds"] is True
    assert len(res["unsupervised_states_leaked"]) == 0


def test_invariant_approval_gate_necessity():
    res = SafetyInvariantVerifier.verify_approval_gate_necessity()
    assert res["invariant_holds"] is True
    assert res["total_valid_execution_paths"] > 0


def test_invariant_acyclic_termination():
    res = SafetyInvariantVerifier.verify_acyclic_termination()
    assert res["invariant_holds"] is True
    assert res["has_cycles"] is False
