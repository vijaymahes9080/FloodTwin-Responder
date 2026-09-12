# Safety Limitations & Operational Boundaries

## 1. Advisory Decision-Support Scope
- **Non-Autonomous Operations:** FloodTwin Responder is strictly an advisory decision-support system. It does not replace certified incident commanders, meteorologists, or hydrological authorities.
- **No Operational Flood Forecasting Guarantee:** Unless validated against real-time calibrated hydrodynamic models, risk scores represent observational evidence and spatial estimations, not deterministic predictions.

## 2. Telemetry & Sensor Sparsity
- In regions with missing stream gauge telemetry or sparse rainfall radar coverage, the risk engine outputs elevated uncertainty scores ($>40\%$) and prompts field verification rather than asserting certainty.
- Physical sensor hardware may experience power failure, silt clogging, or telecommunications outages during severe cyclones.

## 3. Ground Report Uncertainty
- Citizen-submitted reports are treated as untrusted. Reported water depths are considered unverified observations until corroborated by multiple reports within a 100-meter radius or verified by municipal field personnel.

## 4. Emergency Communications Boundary
- The platform contains zero production cellular broadcast hooks or public siren actuation triggers. All outbound dispatch flows are permanently routed to sandbox simulation sinks.
