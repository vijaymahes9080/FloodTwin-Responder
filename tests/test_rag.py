"""
RAG Knowledge Base and Policy Citation Tests for FLOODTWIN RESPONDER.
"""

import pytest
from rag.knowledge_base import PolicyKnowledgeBase, SOPDocument


def test_sop_retrieval_and_citation_integrity():
    kb = PolicyKnowledgeBase()
    results = kb.search("hospital diesel generator elevation rooftop flood SOP", top_k=1)
    assert len(results) == 1
    citation = results[0]
    assert citation["page"] == 82
    assert "Section 6.4" in citation["section"]
    assert "National Disaster Management Guidelines" in citation["source_title"]
    assert len(citation["content_hash"]) == 64


def test_category_filter():
    kb = PolicyKnowledgeBase()
    results = kb.search("water supply drinking", category_filter="SHELTER_MANAGEMENT")
    for r in results:
        assert "Relief Center" in r["section"] or "Shelter" in r["source_title"]


def test_fallback_on_unrelated_query():
    kb = PolicyKnowledgeBase()
    results = kb.search("quantum mechanics superconductivity black holes", min_score=0.25)
    assert len(results) == 0
