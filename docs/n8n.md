# n8n Automation Engine Specification — FloodTwin Responder

## 1. Pipeline Overview
The n8n automation pipeline provides automated workflow triage connecting citizen reports to the FloodTwin risk engine and bounded agent while enforcing human approval.

```
[Citizen Webhook]
       │
       ▼
[Validate & Deduplicate] ──(Invalid)──► [Dead-Letter Queue (DLQ)]
       │ (Valid)
       ▼
[Store Report in PostGIS]
       │
       ▼
[Execute Explainable Risk Engine]
       │
       ▼
[Retrieve Grounded SOP Citations]
       │
       ▼
[Bounded Response Agent: Draft Brief]
       │
       ▼
[Human Commander Approval Gate] ──► [Mock Notification Sandbox]
```

## 2. Dead-Letter Queue (DLQ) & Resilience
- Any report with coordinates outside the operational district or corrupted schema is diverted to the Dead-Letter Queue node.
- HTTP requests to backend endpoints employ exponential backoff retry policies (3 attempts, 5-second timeouts).
- Webhook headers require `X-Idempotency-Key` to prevent duplicate ingest under unstable network conditions.
