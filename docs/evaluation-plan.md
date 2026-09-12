# Evaluation Plan & Benchmark Harness — FloodTwin Responder

## 1. Objectives
The FloodTwin Responder evaluation framework quantitatively evaluates system performance across nine key disaster-response metrics using curated, realistic synthetic testbeds and adversarial scenarios.

## 2. Evaluation Metrics & Formal Targets

| Metric | Target | Description & Formula |
| :--- | :--- | :--- |
| **Hotspot Classification Accuracy** | $\ge 80\%$ | Accuracy of risk engine in classifying ground truth flood severity (Low, Mod, High, Critical). |
| **Duplicate Detection Precision** | $\ge 85\%$ | True Positives / (True Positives + False Positives) for spatial-temporal duplicate reports. |
| **Duplicate Detection Recall** | $\ge 85\%$ | True Positives / (True Positives + False Negatives) for identifying clustered reports. |
| **Asset Prioritization Accuracy** | $\ge 85\%$ | Correct ranking of high-vulnerability facilities (ICU hospitals, power stations) in flood zones. |
| **Policy Citation Coverage** | $\ge 90\%$ | Percentage of generated brief recommendations backed by verified SOP section & page citations. |
| **Unsupported Claim Rate** | $0.0\%$ | Frequency of AI recommendations lacking verified empirical evidence or official SOP backing. |
| **False-Alert Reduction** | $\ge 70\%$ | Rejection rate of anomalous single-sensor spikes or uncorroborated adversarial reports. |
| **Approval Logging Completeness**| $100.0\%$ | Every state change, brief generation, and approval decision cryptographically logged in audit trail. |
| **Median Response Brief Latency** | $< 2.0\text{ sec}$ | End-to-end latency from evidence collection to generated draft brief. |

## 3. Evaluation Dataset Composition
The benchmark evaluation dataset (`benchmarks/dataset.json`) includes 220+ curated records:
- **100 Synthetic Standard Flood Reports:** Varying depths, rainfalls, and flood stages across Chennai urban zones.
- **20 Duplicate Report Pairs:** Collocated coordinates ($\Delta d < 100\text{m}$) and temporal window ($\Delta t < 30\text{min}$).
- **20 Contradictory Reports:** Contradictory reports submitted in the same grid tile (e.g. "dry road" vs "4ft submerged").
- **20 Low-Confidence Reports:** Vague, uncorroborated, single-word submissions.
- **20 Multilingual Reports:** Tamil and bilingual Tamil-English submissions (`"சென்னையில் மழை வெள்ளம் ரோட்டில் 2 அடி தண்ணீர்"`).
- **20 Adversarial & Prompt-Injection Cases:** Exploits containing instruction override payloads, system prompt leakage attempts, and fake siren triggers.
- **20 Sensor Outage & Telemetry Failure Cases:** Hardware sensors with stale timestamps, 0V battery, or negative water stages.

## 4. Benchmark Execution Command
```bash
python benchmarks/run_benchmarks.py
```
Outputs empirical JSON and tabular markdown performance reports.
