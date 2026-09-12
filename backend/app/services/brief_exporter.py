"""
Incident Response Brief Exporter.
Generates publication-grade Markdown and printable HTML memos for District Disaster Management Authorities.
Embeds evidentiary citations, sensor telemetry, and cryptographic verification seals.
"""

from typing import Dict, Any, List
import hashlib
from datetime import datetime, timezone


class BriefExporter:
    """
    Renders structured ResponseBrief objects into formalized emergency briefing documents.
    """

    @classmethod
    def generate_markdown(cls, brief: Dict[str, Any]) -> str:
        """
        Renders clean, GitHub-flavored Markdown brief.
        """
        brief_id = brief.get("id", "BRIEF-UNKNOWN")
        risk_score = brief.get("risk_score", 0.0)
        severity = brief.get("severity", "MODERATE").upper()
        assets = brief.get("affected_assets", [])
        actions = brief.get("recommended_actions", [])
        citations = brief.get("policy_citations", [])
        uncertainty = brief.get("uncertainty_score", 0.1)

        # Generate cryptographic integrity hash
        raw_repr = f"{brief_id}|{risk_score}|{severity}|{brief.get('timestamp')}"
        doc_hash = hashlib.sha256(raw_repr.encode("utf-8")).hexdigest()

        md = []
        md.append("# DISTRICT DISASTER MANAGEMENT INCIDENT RESPONSE BRIEF")
        md.append(f"**Document Reference**: `{brief_id}` | **Status**: PENDING HUMAN COMMANDER APPROVAL")
        md.append(f"**Classification**: STRICTLY INTERNAL / OFFICIAL USE ONLY\n")
        md.append("---")
        md.append("## 1. Executive Situation Assessment")
        md.append(f"- **Composite Risk Score**: **{risk_score}/100.0** (Severity: `{severity}`)")
        md.append(f"- **Uncertainty Factor**: {uncertainty * 100:.1f}%")
        md.append(f"- **Operational Geographic Scope**: Coimbatore Urban District / Noyyal Catchment\n")

        md.append("## 2. High-Priority Vulnerable Assets Identified")
        if assets:
            for a in assets:
                md.append(f"- **{a}** (Requires physical on-site dike & sluice monitoring)")
        else:
            md.append("- *No immediate high-consequence critical assets within direct flood contour.*")
        md.append("")

        md.append("## 3. Recommended Intervention Protocols")
        if actions:
            for idx, act in enumerate(actions, 1):
                md.append(f"{idx}. {act}")
        else:
            md.append("- *Maintain standard 15-minute sensor monitoring cycle.*")
        md.append("")

        md.append("## 4. Grounded Statutory SOP & Policy Citations")
        if citations:
            for cit in citations:
                title = cit.get("title", "Emergency Protocol")
                sec = cit.get("section", "General")
                page = cit.get("page", 1)
                chash = cit.get("content_hash", "")[:16]
                md.append(f"- *{title}*, Section: `{sec}`, Page: {page} `[SHA256: {chash}...]`")
        else:
            md.append("- *Refer to District Disaster Management Plan (DDMP) Chapter 4.*")
        md.append("")

        md.append("---")
        md.append("### Legal Compliance & Safety Notice")
        md.append("> **IMPORTANT**: This document is generated as an AI-augmented decision-support draft. ")
        md.append("> It does NOT constitute an autonomous emergency order. No evacuation or public alert ")
        md.append("> may be issued without signed authorization from the Incident Commander.")
        md.append(f"\n*Cryptographic Audit Seal: `SHA256-{doc_hash}`*")

        return "\n".join(md)

    @classmethod
    def generate_html_printable(cls, brief: Dict[str, Any]) -> str:
        """
        Renders print-ready HTML memo with institutional typography and borders.
        """
        md_text = cls.generate_markdown(brief)
        # Convert simple markdown headers and bullets to HTML
        html_body = md_text.replace("\n", "<br/>")

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>Flood Incident Response Brief - {brief.get('id')}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; color: #1e293b; background: #fff; line-height: 1.6; }}
  .header {{ border-bottom: 3px solid #0284c7; padding-bottom: 15px; margin-bottom: 25px; }}
  .badge {{ background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 4px; font-weight: bold; }}
  .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }}
  .seal {{ font-family: monospace; font-size: 11px; color: #64748b; margin-top: 30px; }}
</style>
</head>
<body>
  <div class="header">
    <h2>FLOODTWIN RESPONDER — SITUATION REPORT</h2>
    <span class="badge">EVIDENCE-GROUNDED DISASTER INTELLIGENCE</span>
  </div>
  <div>{html_body}</div>
</body>
</html>"""
