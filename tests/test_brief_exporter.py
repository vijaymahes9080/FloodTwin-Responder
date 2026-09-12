import pytest
from backend.app.services.brief_exporter import BriefExporter


def test_brief_markdown_generation():
    sample_brief = {
        "id": "BRIEF-TEST-101",
        "risk_score": 78.5,
        "severity": "high",
        "timestamp": "2026-09-12T07:30:00Z",
        "affected_assets": ["Singanallur Lake Bund", "Valankulam Cause-way"],
        "recommended_actions": [
            "Deploy mobile de-watering pump units to Valankulam Cause-way.",
            "Verify relief center readiness at Govt Higher Secondary School."
        ],
        "policy_citations": [
            {
                "title": "Tamil Nadu State Disaster Management Plan",
                "section": "4.2 Flood Evacuation",
                "page": 45,
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            }
        ],
        "uncertainty_score": 0.08
    }

    md = BriefExporter.generate_markdown(sample_brief)
    assert "BRIEF-TEST-101" in md
    assert "78.5/100.0" in md
    assert "Singanallur Lake Bund" in md
    assert "Tamil Nadu State Disaster Management Plan" in md
    assert "SHA256-" in md
    assert "autonomous emergency order" in md


def test_brief_html_generation():
    sample_brief = {
        "id": "BRIEF-HTML-001",
        "risk_score": 50.0,
        "severity": "moderate",
        "timestamp": "2026-09-12T07:35:00Z"
    }
    html = BriefExporter.generate_html_printable(sample_brief)
    assert "<!DOCTYPE html>" in html
    assert "BRIEF-HTML-001" in html
    assert "FLOODTWIN RESPONDER" in html
