# Product Requirements Document (PRD) — FloodTwin Responder

## 1. Executive Summary
**FloodTwin Responder** is an open-source, human-supervised flood intelligence and disaster-response planning platform. It ingests multi-source inputs (citizen ground reports, IoT stream gauges, rainfall radar, and synthetic satellite SAR masks), computes explainable risk indices across standardized spatial grids, detects critical asset vulnerabilities, retrieves policy-grounded SOPs with strict cryptographic citations, and synthesizes structured **Response Briefs** for emergency commanders.

## 2. Guiding Principles & Invariants
1. **Decision Support, Not Autonomy:** The platform NEVER dispatches live public alerts, calls emergency services, or orders mandatory evacuations autonomously.
2. **Mandatory Human-in-the-Loop (HITL):** High-impact actions are staged as `PENDING_HUMAN_APPROVAL` and require authenticated commander sign-off.
3. **Data State Transparency:** Every telemetry point, citizen input, and computational output must explicitly state its provenance category: `MEASURED`, `OBSERVED`, `ESTIMATED`, or `SIMULATED`.
4. **No Hallucinated Infrastructure:** Shelters, rescue contacts, hospitals, and operational guidelines must strictly originate from verified databases and validated SOP repositories with exact chapter/page citations.
5. **Untrusted Input Assumption:** All citizen reports, uploaded media, and external webhooks are treated as inherently untrusted, requiring bounding-box validation, PII redaction, duplicate suppression, and prompt-injection filtering.

## 3. Core Functional Capabilities
- **Report Ingestion & Quality Control (QC):**
  - Text, image metadata, and audio dispatch adapters.
  - Lat/Lon bounds validation against district boundaries (Chennai / Cooum River pilot).
  - Duplicate detection combining Haversine spatial proximity (<100m) and temporal clustering (<30 min).
  - Automated regex and entity PII redaction for phone numbers, emails, personal IDs.
  - Safe wording enforcement ("possible waterlogging", "likely duplicate").
- **Explainable Multi-Factor Risk Engine:**
  - Multi-variable synthesis: rainfall intensity, stream gauge water levels, citizen reported depths, topography/elevation vulnerabilities, and critical asset proximity.
  - Transparent factor weight breakdown with uncertainty scoring.
  - Explicit missing-data warnings and suggested field verification actions.
- **Geospatial Processing Engine:**
  - Standardized CRS: EPSG:4326 (WGS 84) output in GeoJSON.
  - Point-in-polygon containment, spatial joins, buffer analysis along drainage corridors.
  - Spatial indexing for fast radial search of nearby hospitals, schools, power stations, and relief shelters.
- **Grounded Policy Retrieval (RAG):**
  - Embedding and BM25 hybrid semantic search over disaster management authority SOPs (NDMA, TNSDMA).
  - Verified citation generation: Document Title, Section, Page Number, Publication Date, Jurisdiction, SHA-256 Content Hash.
- **Bounded Response Agent (8-State Deterministic FSM):**
  - `COLLECT_EVIDENCE` $\to$ `VERIFY` $\to$ `ASSESS` $\to$ `PRIORITIZE` $\to$ `RETRIEVE_POLICY` $\to$ `DRAFT_BRIEF` $\to$ `REQUEST_APPROVAL` $\to$ `RECORD_DECISION`.
  - Compile comprehensive response briefs.
- **Interoperability & Integration:**
  - Model Context Protocol (MCP) JSON-RPC tool endpoints with strict RBAC.
  - n8n Community Edition workflow with webhook trigger, idempotency keys, dead-letter retry logic, and mock notification dispatch.
- **Supervisory Command Dashboard:**
  - 11 dedicated operational views (Map, Reports, Risk Tiles, Sensors, Assets, Shelters, Briefs, Approvals, Citations, Audit Log, Benchmark).
  - High aesthetic design with dark glassmorphism, accessible contrasts, and bilingual English/Tamil layout.

## 4. User Personas & Permissions
| Persona | Role Key | Permissions |
| :--- | :--- | :--- |
| **Disaster Commander** | `DISASTER_COMMANDER` | Full system access; authorize/reject response briefs; approve mock dispatch; configure risk thresholds. |
| **Field Analyst** | `FIELD_ANALYST` | Submit verified ground observations; inspect sensor health; view risk tiles; query RAG procedures. |
| **Emergency Auditor** | `AUDITOR` | Read-only inspection of immutable audit trails, provenance hashes, decision rationales, and benchmark logs. |
