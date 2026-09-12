# Incident Commander Operational Handbook

## FloodTwin Responder Field Deployment & Emergency Protocol Manual

---

## 1. Role & Command Hierarchy

FloodTwin Responder is structured around strictly defined role-based access control (RBAC):

1. **INCIDENT COMMANDER (District Collector / Municipal Commissioner)**:
   - Sole authority possessing cryptographic keys to approve `ResponseBrief` actions.
   - Authority to authorize de-watering pump deployments, shelter activation, and NDRF/SDRF mobilization requests.
2. **DISASTER ANALYST / GEOSPATIAL OPERATOR**:
   - Reviews satellite radar change tiles, examines Topographic Wetness Index (TWI) anomalies, and verifies automated duplicate clusters.
3. **FIELD INSPECTION OFFICER (Revenue Inspector / Fire & Rescue)**:
   - Receives prioritized triage targets (Top-5 list) on mobile dashboard.
   - Validates on-site physical stage gauges and road culvert blockage statuses.
4. **CIVILIAN / VOLUNTEER CORPS**:
   - Submits geotagged observations via WhatsApp or web portal. Unauthenticated submissions are treated as unverified evidence.

---

## 2. Standard Operating Procedure (SOP) Cycle

### Stage 1: Continuous Pre-Monsoon & Warning Phase
- **Sensor Telemetry Interval**: Every 15 minutes.
- **Pre-Event Satellite Baseline**: Sentinel-1 SAR acquisition stored in spatial cache.
- **Drainage Inspection**: Siltation levels checked across primary outfall channels.

### Stage 2: Inflow & Surcharge Alert Phase (Rainfall > 60mm / 6h)
- Telemetry interval accelerated to 5 minutes.
- Automated duplicate clustering and PII redaction active on incoming citizen reports.
- Discrepancy checks triggered between ultrasonic bridge sensors and downstream pressure transducers.

### Stage 3: Incident Triage & Brief Formulation
- System runs 5-factor explainable risk scoring.
- Bounded FSM retrieves grounded statutory protocols from Tamil Nadu State Disaster Management Plan (TNSDMP) and NDMA Guidelines.
- Generates draft `ResponseBrief` with citations and confidence metrics.
- Status locked at `PENDING_HUMAN_APPROVAL`.

### Stage 4: Commander Review & Decision Execution
- Incident Commander authenticates via token.
- Reviews affected critical assets (hospitals, schools, subway underpasses) and safest evacuation corridors.
- Approves or rejects intervention items.
- Upon approval, system signs audit trail event and triggers automated n8n notification dispatch.

---

## 3. Prohibited Actions & Safety Constraints
- **ZERO UNAPPROVED DISPATCH**: The AI engine shall under no circumstances publish public emergency alerts, sound sirens, or mandate residential evacuation orders without an authenticated human signature.
- **TAMPERED SENSOR OVERRIDE**: Any sensor telemetry reporting electrical fault or CRC-8 checksum discrepancy must be flagged as unverified and excluded from automated parametric insurance triggers.
- **GEO-FENCING BOUNDARY**: Reports originating outside the authorized district operational bounding box are quarantined.
