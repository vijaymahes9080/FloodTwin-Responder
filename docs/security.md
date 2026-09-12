# Security Architecture & Controls — FloodTwin Responder

## 1. Input Sanitization & Untrusted Ingest Defense
FloodTwin Responder implements defense-in-depth on all external inputs:
- **Geographic Bounding Box Filter:** Rejects coordinates outside authorized disaster zones (`[12.80 <= lat <= 13.30, 79.90 <= lon <= 80.40]`) and flags marine coordinates in open ocean.
- **PII Scrubbing:** Automated regex redactors eliminate phone numbers, email addresses, and Aadhaar identity numbers prior to database storage or vector embedding.
- **Adversarial Prompt-Injection Defense:** Filters keywords designed to override system constraints (`ignore previous instructions`, `bypass approval`, `trigger siren`).

## 2. Server-Side Request Forgery (SSRF) Protection
All external webhook endpoints and image URLs are strictly validated:
- Rejects non-HTTP/HTTPS protocols (e.g. `file://`, `gopher://`).
- Blocks loopback IPs (`127.0.0.1`, `::1`) and cloud metadata endpoints (`169.254.169.254`).
- Drops private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).

## 3. Cryptographic Merkle-Chained Audit Trail
Every system decision, report ingestion, risk evaluation, and human commander approval is hashed and linked:
$$\text{Hash}_n = \text{SHA256}\left(\text{ActorID} \parallel \text{Action} \parallel \text{ResourceID} \parallel \text{DetailsJSON} \parallel \text{Hash}_{n-1}\right)$$
This ensures forward-secure, tamper-evident audit logging for post-disaster judicial and legislative inquiries.

## 4. Role-Based Access Control (RBAC)
| Role | Capabilities |
| :--- | :--- |
| `DISASTER_COMMANDER` | Full administrative oversight; authorize/reject response briefs; sign off on mock dispatch. |
| `FIELD_ANALYST` | Ingest ground observations; view telemetry; run risk engine; query SOP RAG. |
| `AUDITOR` | Read-only inspection of immutable audit records, provenance hashes, and benchmark logs. |
