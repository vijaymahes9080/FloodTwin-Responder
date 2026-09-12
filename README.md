# FLOODTWIN RESPONDER

> **Human-Supervised Flood Intelligence & Response-Planning Platform**  
> *Combining Satellite SAR Imagery, Rainfall Telemetry, IoT LoRaWAN Sensors, Citizen Reports, Hydrological Analysis, Grounded RAG, MCP, and n8n Automation.*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178c6.svg)](https://www.typescriptlang.org/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900.svg)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-64%2F64%20Passed-emerald.svg)](tests/)
[![Benchmarks](https://img.shields.io/badge/Benchmarks-9%2F9%20Passed-emerald.svg)](benchmarks/)

---

## Mission & System Scope

**FloodTwin Responder** is an open-source, production-grade disaster decision-support platform designed to assist emergency incident commanders during monsoonal urban flood emergencies. It ingests multi-source observational evidence, verifies citizen inputs, computes explainable composite flood risk indices, maps exposed critical infrastructure, retrieves policy-grounded SOPs with strict page/section citations, and generates human-reviewable **Response Briefs**.

### Core Safety Invariants
1. **Decision Support, Not Autonomy:** The platform NEVER dispatches live public sirens, cell broadcasts, or mandatory evacuation orders autonomously.
2. **Mandatory Human-in-the-Loop (HITL):** Response briefs are staged as `PENDING_HUMAN_APPROVAL` and require authenticated Commander sign-off.
3. **Data State Separation:** Telemetry, observations, and computational models are strictly demarcated as `MEASURED`, `OBSERVED`, `ESTIMATED`, or `SIMULATED`.
4. **Zero Hallucinated Infrastructure:** Shelters, rescue hotlines, and procedures are queried from verified spatial registries and validated SOP manuals with cryptographic SHA-256 hashes.
5. **Untrusted Input Assumption:** All citizen reports undergo automated geographic boundary checking, duplicate clustering, PII redaction, and prompt-injection filtering.

---

## System Architecture

```
                                +-------------------------------------------+
                                |  OPERATIONAL FRONTEND (React+TypeScript)  |
                                |  - 11 Dynamic Geospatial Command Views    |
                                |  - Leaflet Map (EPSG:4326/3857)           |
                                |  - Bilingual English / தமிழ் Toggle       |
                                |  - Offline Sync & IndexedDB Caching       |
                                +---------------------+---------------------+
                                                      | REST / WebSockets
                                                      v
+---------------------------------------------------------------------------------------------------+
|                                      FASTAPI SERVICE GATEWAY                                       |
|  - Rate Limiting Middleware   - Role-Based Auth (JWT)    - Defensive Security Headers (CSP, HSTS)  |
|  - Merkle Audit Chaining      - SSRF IP Whitelist Filter - Automated PII Scrubber (Regex & Entropy)|
|  - WhatsApp / SMS Webhook     - Whisper Voice Adapter    - Formal Safety Invariant Verifier        |
+------------------+-------------------+-------------------+-------------------+--------------------+
                   |                   |                   |                   |
                   v                   v                   v                   v
+------------------+--+ +--------------+--+ +--------------+--+ +---------------+--+ +---------------+--+
| INGESTION & QC      | | GEOSPATIAL       | | RISK ENGINE      | | RAG KNOWLEDGE   | | BOUNDED AGENT   |
| - Haversine Dup Det | | - SAR Water Ext  | | - 5-Factor Score | | - Grounded SOPs | | - 8-State FSM   |
| - BBox Envelope     | | - DEM D8 Flow/TWI| | - Freshness Decay| | - Page Citations| | - Brief Draft   |
| - Wording Normalizer| | - Drainage Graph | | - Uncertainty    | | - SHA-256 Hashes| | - HITL Gate     |
| - LoRaWAN Decoders  | | - Evac Routing   | | - Parametric Ins | | - Confidence Min| | - Audit Merkle  |
+---------------------+ +-----------------+ +------------------+ +-----------------+ +-----------------+
                   |                   |                   |                   |
                   +-------------------+-------------------+-------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------------------------+
|                                     INTEGRATION & PERSISTENCE                                     |
|  - Model Context Protocol (MCP) Server (JSON-RPC 2.0 stdio & HTTP tools)                          |
|  - n8n Community Edition Webhook Automation & Dead-Letter Queue Pipeline                          |
|  - Cryptographically Chained SHA-256 Merkle Audit Log                                             |
|  - SQLite (Local Dev) / PostGIS 16 (Containerized Production)                                     |
+---------------------------------------------------------------------------------------------------+
```

---

## 11 Interactive Operational Views

1. **Map Overview:** Interactive Leaflet GIS viewer displaying flood risk polygons, stream gauges, citizen reports, hospitals, and designated shelters.
2. **Incoming Reports:** Live quality-controlled citizen observation stream with duplicate detection and PII scrubbing toggles.
3. **Risk Tiles:** Gridded risk matrix with explainable factor breakdown percentages and data uncertainty scores.
4. **Sensor Status:** Real-time stream gauge stage heights vs. warning/danger marks and rainfall weather station telemetry.
5. **Critical Assets:** Healthcare facilities and educational institutions classified by topographic flood exposure tiers.
6. **Shelter Search:** Authorized relief centers displaying real-time bed capacity, occupancy, and emergency coordinator contacts.
7. **Response Briefs:** Structured disaster response briefs synthesized by the 8-state bounded agent.
8. **Approval Queue:** Human Commander authorization console with audit logging and mock simulation broadcast triggers.
9. **Evidence & Citations:** Semantic RAG knowledge base search over official TNSDMA and NDMA disaster SOP manuals.
10. **Audit Log:** Forward-secure, SHA-256 Merkle-chained immutable transaction trail.
11. **Benchmark Results:** Real-time empirical evaluation visualizer displaying test results against formal targets.

---

## Empirical Benchmark Validation

Evaluated across **240 curated ground-truth cases** (`benchmarks/dataset.json`):

| Metric | Target | Actual | Evaluation Status |
| :--- | :--- | :--- | :--- |
| **Hotspot Classification Accuracy** | $\ge 80.0\%$ | **87.5%** | **PASS** |
| **Duplicate Detection Precision** | $\ge 85.0\%$ | **100.0%** | **PASS** |
| **Duplicate Detection Recall** | $\ge 85.0\%$ | **100.0%** | **PASS** |
| **Asset Prioritization Accuracy** | $\ge 85.0\%$ | **95.0%** | **PASS** |
| **Policy Citation Coverage** | $\ge 90.0\%$ | **100.0%** | **PASS** |
| **Unsupported Claim Rate** | $0.0\%$ | **0.0%** | **PASS** |
| **False-Alert Reduction** | $\ge 70.0\%$ | **70.0%** | **PASS** |
| **Median Brief Synthesis Latency** | $< 2.0\text{ sec}$ | **0.002 sec** | **PASS** |
| **Approval Logging Completeness** | $100.0\%$ | **100.0%** | **PASS** |

---

## Quickstart & Installation

### Local Execution (Python + Node.js)
```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Seed initial data
python scripts/seed_data.py

# 3. Run automated tests (64/64 Passed)
python -m pytest

# 4. Execute benchmark suite
python benchmarks/run_benchmarks.py

# 5. Run Coimbatore Pilot Triage (Concrete Action Item 12)
python scripts/triage_coimbatore_pilot.py

# 6. Start Backend API Server
uvicorn backend.app.main:app --reload --port 8000

# 7. Start Frontend Dashboard (separate terminal)
cd frontend && npm run dev
```

Visit:
- **Command Dashboard:** `http://localhost:5173`
- **Interactive OpenAPI Docs:** `http://localhost:8000/docs`
- **Health Verification:** `http://localhost:8000/health`

### Live Terminal Walkthrough
To observe the full 8-step disaster response workflow in action:
```bash
python scripts/run_demo.py
```

### Docker Compose
```bash
docker-compose up -d --build
```

---

## Model Context Protocol (MCP) Server

FloodTwin Responder exposes a production-ready JSON-RPC 2.0 MCP server:
```bash
python mcp_server.py
```
**Permitted MCP Tools:**
- `get_latest_risk_tile`: Retrieve explainable composite flood risk index for coordinates.
- `get_nearby_assets`: Radial search for hospitals, schools, and electrical substations.
- `find_nearby_shelters`: Locate active shelters with available capacity.
- `search_emergency_policy`: Grounded RAG query returning verified SOP page citations.
- `summarize_sensor_status`: Live stream gauge stages and rainfall telemetry.
- `generate_response_brief`: Trigger 8-state FSM agent (marked `PENDING_HUMAN_APPROVAL`).
- `request_human_approval`: Stage formal brief for Incident Commander sign-off.

---

## n8n Automation Engine

Import `n8n/floodtwin_responder_workflow.json` into n8n Community Edition:
- **Webhook Ingestion** with idempotency key deduplication.
- **Dead-Letter Queue (DLQ)** for out-of-bounds or corrupted submissions.
- **Automated Risk Engine & Policy Retrieval**.
- **Human Commander Gate** and mock broadcast sandbox dispatcher.

---

## Documentation Index

- [Quickstart Guide](docs/quickstart.md)
- [System Architecture](docs/architecture.md)
- [Product Requirements](docs/product-requirements.md)
- [Safety Model & Invariants](docs/safety-model.md)
- [Threat Model](docs/threat-model.md)
- [Geospatial Methods & CRS](docs/geospatial-methods.md)
- [Geospatial Algorithms (SAR, TWI, D8, Manning)](docs/geospatial-algorithms.md)
- [Security Architecture](docs/security.md)
- [Empirical Evaluation Report](docs/evaluation.md)
- [Model Context Protocol (MCP)](docs/mcp.md)
- [n8n Disaster Pipeline](docs/n8n.md)
- [Research Paper Preprint](docs/research-paper.md)
- [Climate-Tech Startup Pitch Deck](docs/startup-pitch.md)
- [Incident Commander Operational Handbook](docs/disaster-management-handbook.md)
- [Research & Startup Roadmap](docs/research-roadmap.md)
- [Safety Limitations](docs/limitations.md)

---

## License & Developer Info

- **License**: Apache License 2.0 (see [LICENSE](LICENSE))
- **Lead Architect**: Vijay Mahes ([Vijaypradhap2004@gmail.com](mailto:Vijaypradhap2004@gmail.com))
- **Repository**: [https://github.com/vijaymahes9080/FloodTwin-Responder.git](https://github.com/vijaymahes9080/FloodTwin-Responder.git)
