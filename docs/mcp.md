# Model Context Protocol (MCP) Server Specification

## 1. Overview
The FloodTwin MCP Server implements the JSON-RPC 2.0 protocol over stdio and HTTP SSE, exposing strictly vetted disaster response tools to external agentic orchestrators while maintaining safety invariants.

## 2. Permitted MCP Tools

| Tool Name | Scope & Parameters | Safety Constraints |
| :--- | :--- | :--- |
| `get_latest_risk_tile` | `zone_id`, `latitude`, `longitude` | Validates coordinate bounds. Returns explainable factors and uncertainty. |
| `get_nearby_assets` | `latitude`, `longitude`, `radius_km` | Radial search of hospitals, schools, power stations. |
| `find_nearby_shelters` | `latitude`, `longitude`, `max_distance_km` | Queries active shelters with available capacity. |
| `search_emergency_policy` | `query`, `category` | Grounded SOP search. Returns title, section, page, SHA-256 hash. |
| `summarize_sensor_status` | No parameters required | Real-time river stages, battery percentage, quality flags. |
| `generate_response_brief` | `zone_id`, `latitude`, `longitude` | Invokes 8-state FSM. Outputs `PENDING_HUMAN_APPROVAL`. |
| `request_human_approval` | `brief_id`, `operator_id`, `comments` | Stages approval. Live broadcasts strictly blocked. |

## 3. Disallowed Tools & Safety Enforcements
Attempts to invoke `send_live_alert`, `trigger_siren`, or `issue_evacuation_order` are intercepted immediately with error code `-32601` and logged to the Merkle audit trail.
