# System Architecture — FloodTwin Responder

## 1. High-Level Component Topology

```
+-----------------------------------------------------------------------------------+
|                            OPERATIONAL FRONTEND (Vite / React)                     |
|  - Map Overview (Leaflet)     - Reports QC Feed          - Explainable Risk Tiles |
|  - Telemetry Gauges           - Critical Assets Map       - Shelter Routing Locator|
|  - Brief Approval Console     - Verified SOP Explorer    - Audit Verification Log  |
+------------------------------------------+----------------------------------------+
                                           | HTTP REST / SSE
                                           v
+-----------------------------------------------------------------------------------+
|                            FASTAPI SERVICE GATEWAY                                 |
|  - Rate Limiting Middleware   - Role-Based Auth (JWT)    - Structured JSON Logger  |
|  - Request ID Propagation     - PII Sanitization Filter   - Security Headers (CSP) |
+----+--------------------+--------------------+--------------------+---------------+
     |                    |                    |                    |
     v                    v                    v                    v
+-----------+       +-----------+       +-----------+       +---------------+
| INGESTION |       | GEOSPATIAL|       | RISK      |       | BOUNDED AGENT |
| & QC      |       | ENGINE    |       | ENGINE    |       | & RAG ENGINE  |
| - Dup-Det |       | - PiP     |       | - Factor  |       | - 8-State FSM |
| - BBox Chk|       | - Spatial |       |   Weights |       | - SOP Embeds  |
| - Content |       |   Joins   |       | - Fresh   |       | - Cryptograph |
|   Sanitize|       | - Buffers |       |   Decay   |       |   Citations   |
+-----+-----+       +-----+-----+       +-----+-----+       +-------+-------+
      |                   |                   |                     |
      +-------------------+-------------------+---------------------+
                                  |
                                  v
+-----------------------------------------------------------------------------------+
|                            INTEGRATION & EXTERNAL INTERFACES                      |
|  - Model Context Protocol (MCP) Server (JSON-RPC stdio/HTTP)                      |
|  - n8n Community Edition Webhook Automation & Dead-Letter Queue Pipeline          |
|  - Mock Notification Broadcast Service (Sandbox SMS, Siren Simulation)           |
+-----------------------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------------------+
|                            PERSISTENCE & AUDIT STORE                              |
|  - SQLite (Local Embedded) / PostGIS (Containerized Production)                   |
|  - Cryptographic SHA-256 Chained Immutable Audit Log                             |
|  - Geospatial Vector Indices (EPSG:4326)                                          |
+-----------------------------------------------------------------------------------+
```

## 2. Ingestion & Quality Control Subsystem
1. **Endpoint:** `POST /reports`
2. **Sanitization Filter:**
   - Evaluates coordinate within operational envelope: `[12.80 <= lat <= 13.30, 79.90 <= lon <= 80.40]` (Chennai Metropolitan Region).
   - Timestamp verification: `(now - 48h) <= timestamp <= (now + 5min)`.
   - Text scrubbed via regex matching Indian phone numbers `(\+91[\s-]?[6-9]\d{9}|0?[6-9]\d{9})`, emails, Aadhaar/PAN formats.
   - Spatial duplicate search: compares with all reports submitted within past 30 minutes in a 100-meter radius. If match found, flagged as `LIKELY_DUPLICATE` referencing parent ID.

## 3. Geospatial Engine (`geospatial/spatial_engine.py`)
- Standardized Coordinate Reference System: **EPSG:4326** (WGS 84).
- Point-in-Polygon (Ray casting + Shapely accelerated geometry) for administrative ward boundaries.
- Haversine radial distance lookup with $O(\log N)$ spatial indexing.
- Drainage corridor buffer generation (50m, 100m, 200m buffer envelopes around waterways).

## 4. Multi-Factor Explainable Risk Engine (`risk-engine/engine.py`)
Composite score calculation:
$$R = \min\left(100, \; \left(w_r \cdot \hat{R}_{rain} + w_s \cdot \hat{S}_{sensor} + w_d \cdot \hat{D}_{depth} + w_e \cdot \hat{E}_{elev} + w_v \cdot \hat{A}_{asset}\right) \times \Phi(\Delta t)\right)$$
Where:
- $\hat{R}_{rain}$: Normalized 3-hour rainfall intensity ($0 \dots 100 \text{ mm/hr} \to 0 \dots 1$).
- $\hat{S}_{sensor}$: Water level relative to flood warning threshold ($\max(0, \frac{h - h_{base}}{h_{warn} - h_{base}})$).
- $\hat{D}_{depth}$: Average verified citizen report water depth in the grid tile ($0 \dots 150 \text{ cm} \to 0 \dots 1$).
- $\hat{E}_{elev}$: Topographic vulnerability penalty based on digital elevation model ($1 - \frac{\text{elev}}{30\text{m}}$ for lowlands).
- $\hat{A}_{asset}$: Vulnerability density multiplier based on nearby hospitals, schools, elderly care centers.
- $\Phi(\Delta t) = \exp(-\Delta t / \tau)$: Temporal freshness decay where half-life $\tau = 6 \text{ hours}$.

## 5. Bounded Response Agent FSM (`agent/response_fsm.py`)
Deterministic finite state machine ensuring compliance with safety invariant:
1. `COLLECT_EVIDENCE`
2. `VERIFY`
3. `ASSESS`
4. `PRIORITIZE`
5. `RETRIEVE_POLICY`
6. `DRAFT_BRIEF`
7. `REQUEST_APPROVAL`
8. `RECORD_DECISION`

## 6. Audit Logging & Provenance
Every state mutation generates an `AuditEvent` with:
- `actor_id` & `actor_role`
- `action` (e.g., `REPORT_INGESTED`, `RISK_EVALUATED`, `BRIEF_APPROVED`)
- `resource_id`
- `details` (payload or parameter delta)
- `previous_event_hash` (block-chained SHA-256 ensuring append-only tamper evidence).
