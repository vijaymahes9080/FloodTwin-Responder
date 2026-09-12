import pytest
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.triage_coimbatore_pilot import (
    load_pilot_dataset,
    triage_pilot_dataset
)


def test_pilot_dataset_loading():
    records = load_pilot_dataset()
    assert len(records) == 20
    assert any(r["report_id"] == "R001" for r in records)
    assert any(r["report_id"] == "R020" for r in records)


def test_pilot_triage_adversarial_and_stale_filtering():
    records = load_pilot_dataset()
    triage_result = triage_pilot_dataset(records)
    
    # 1 adversarial report R020 must be suppressed
    assert "R020" in triage_result["adversarial_ids"]
    assert len(triage_result["adversarial_ids"]) == 1
    
    # 2 stale reports (R017, R018) must be dropped
    assert "R017" in triage_result["stale_ids"]
    assert "R018" in triage_result["stale_ids"]
    assert len(triage_result["stale_ids"]) == 2


def test_pilot_duplicate_clustering():
    records = load_pilot_dataset()
    triage_result = triage_pilot_dataset(records)
    
    # Check that duplicate groups have mapped properly
    dup_clusters = triage_result["duplicate_clusters"]
    assert "R002" in dup_clusters
    assert "R003" in dup_clusters["R002"]
    assert "R004" in dup_clusters
    assert "R005" in dup_clusters["R004"]


def test_pilot_top5_ranking():
    records = load_pilot_dataset()
    triage_result = triage_pilot_dataset(records)
    top_5 = triage_result["top_5"]
    
    assert len(top_5) == 5
    # The highest priority is Valankulam Lake Bund (R014)
    assert top_5[0]["report_id"] == "R014"
    assert top_5[0]["score"] > 70.0
    
    # Ensure scores are strictly sorted descending
    scores = [item["score"] for item in top_5]
    assert scores == sorted(scores, reverse=True)
    
    # Ensure every recommendation contains safe, human-approved advisory
    for item in top_5:
        assert item["protocol"] is not None
        assert "evacuation" not in item["protocol"].lower() or "alert" not in item["protocol"].lower()
