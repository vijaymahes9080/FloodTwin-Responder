# n8n Disaster Automation Pipeline — FloodTwin Responder

## Overview
This directory provides an importable n8n workflow (`floodtwin_responder_workflow.json`) that automates end-to-end disaster report triage while strictly honoring human-in-the-loop safety constraints.

## Workflow Nodes & Architecture
1. **Webhook Trigger (`POST /webhook/flood-report-webhook`):** Ingests incoming citizen or field observations.
2. **Idempotency & Coordinate Filter:** Rejects out-of-bounds coordinates and deduplicates requests using `X-Idempotency-Key`.
3. **Branching Logic:**
   - *Valid:* Submits report to `POST /api/v1/reports`.
   - *Invalid:* Routes to **Dead-Letter Queue (DLQ)** node for forensic triage without dropping data.
4. **Risk Calculation Node:** Calls `POST /api/v1/risk/analyze` with telemetry streams.
5. **Grounded Policy Retrieval:** Queries `GET /api/v1/policy/search` for verifiable SOP citations.
6. **Bounded Response Agent:** Synthesizes draft brief via `POST /api/v1/response-briefs`.
7. **Human Approval Gate & Mock Dispatch:** Enforces `PENDING_HUMAN_APPROVAL` status and triggers simulated notification sandbox.

## How to Import into n8n
1. Open your n8n Community Edition instance (default: `http://localhost:5678`).
2. Click **Workflows** > **Import from File**.
3. Select `n8n/floodtwin_responder_workflow.json`.
4. Update the `backend:8000` host URL if running outside Docker bridge network.
5. Click **Activate**.

## Safety Invariant Notice
> [!IMPORTANT]
> The n8n workflow executes in **MOCK MODE**. No public sirens or cellular alerts are triggered. All notifications are written to simulated sandbox logs.
