"""
Policy and SOP Knowledge Base endpoints for FLOODTWIN RESPONDER.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from rag.knowledge_base import PolicyKnowledgeBase

router = APIRouter(prefix="/policy", tags=["Policy & RAG"])
kb = PolicyKnowledgeBase()


@router.get("/search")
def search_policy_guidelines(
    query: str = Query(..., min_length=2, description="Disaster response or SOP query"),
    category: Optional[str] = Query(None, description="EVACUATION, HOSPITAL_PROTECTION, SHELTER_MANAGEMENT"),
    top_k: int = Query(3, ge=1, le=10)
):
    """
    Queries grounded emergency SOP knowledge base.
    Returns verifiable citations (title, section, page, jurisdiction, hash).
    """
    citations = kb.search(query=query, category_filter=category, top_k=top_k)
    return {
        "query": query,
        "category_filter": category,
        "count": len(citations),
        "citations": citations,
        "fallback_triggered": len(citations) == 0
    }


@router.get("/all")
def list_all_sops():
    """Lists all standard operating procedures currently indexed in the knowledge base."""
    return {
        "count": len(kb.documents),
        "documents": [doc.to_dict() for doc in kb.documents]
    }
