"""
Automated Triage Script for 20-Record Coimbatore / Noyyal Pilot Dataset.
Loads records, validates coordinates, identifies duplicate clusters, suppresses adversarial injections,
filters stale/outdated records, computes transparent risk scores, and outputs top 5 human inspection targets.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

# Path resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from geospatial.spatial_engine import haversine_distance_km
from risk_engine import FloodRiskEngine

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "benchmarks", "coimbatore_pilot_dataset.json")

# Operational bounding box for Coimbatore Urban & Noyyal Catchment
COIMBATORE_BBOX = (10.85, 11.15, 76.85, 77.10)  # [min_lat, max_lat, min_lon, max_lon]


def triage_pilot_data():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at {DATASET_PATH}")
        sys.exit(1)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    print("==================================================================")
    print("FLOODTWIN RESPONDER — COIMBATORE PILOT INCIDENT TRIAGE ENGINE")
    print(f"Ingested {len(records)} ground records from Noyyal River Basin")
    print("==================================================================")

    now = datetime(2026, 9, 12, 7, 0, 0, tzinfo=timezone.utc)
    risk_engine = FloodRiskEngine()

    processed = []
    duplicate_clusters = {}
    suppressed_adversarial = []
    stale_records = []
    contradictory_flags = []

    # Step 1: Filter adversarial and outdated
    for r in records:
        r_id = r["report_id"]
        notes = r.get("notes", "")

        # Check adversarial payload
        if "ignore previous instructions" in notes.lower() or "system override" in notes.lower() or r["water_depth_cm"] > 300:
            suppressed_adversarial.append(r_id)
            continue

        # Check timestamp staleness (>48h)
        try:
            ts = datetime.fromisoformat(r["report_time"])
            if (now - ts) > timedelta(hours=48):
                stale_records.append(r_id)
                continue
        except Exception:
            pass

        # Validate coordinates within Coimbatore bounds
        lat, lon = r["latitude"], r["longitude"]
        min_lat, max_lat, min_lon, max_lon = COIMBATORE_BBOX
        if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
            continue

        processed.append(r)

    # Step 2: Identify Duplicate Clusters (distance < 100m, group together)
    primary_records = []
    for r in processed:
        is_dup = False
        for parent in primary_records:
            dist_km = haversine_distance_km(r["latitude"], r["longitude"], parent["latitude"], parent["longitude"])
            if (dist_km * 1000.0) <= 80.0:  # within 80m
                cluster_id = parent["report_id"]
                if cluster_id not in duplicate_clusters:
                    duplicate_clusters[cluster_id] = [cluster_id]
                duplicate_clusters[cluster_id].append(r["report_id"])
                is_dup = True
                break
        if not is_dup:
            primary_records.append(r)

    # Step 3: Identify Contradictory pairs
    for i, r1 in enumerate(primary_records):
        for r2 in primary_records[i+1:]:
            dist_m = haversine_distance_km(r1["latitude"], r1["longitude"], r2["latitude"], r2["longitude"]) * 1000.0
            if dist_m <= 150.0 and abs(r1["water_depth_cm"] - r2["water_depth_cm"]) >= 50.0:
                contradictory_flags.append((r1["report_id"], r2["report_id"]))

    # Step 4: Calculate Transparent Risk Scores for Primaries
    scored_candidates = []
    for r in primary_records:
        cluster_size = len(duplicate_clusters.get(r["report_id"], [r["report_id"]]))
        calc = risk_engine.calculate_risk(
            rainfall_3h_mm=r["rainfall_mm_6h"] * 0.6,
            sensor_water_level_m=r["sensor_level_cm"] / 25.0,  # convert cm stage to normalized meter ratio
            reported_depth_cm=r["water_depth_cm"],
            elevation_m=5.0,
            nearby_critical_assets_count=2 if "Hospital" in r["nearby_asset"] else 1
        )

        # Corroboration boost if clustered by multiple callers
        final_score = min(100.0, calc["score"] + (cluster_size - 1) * 3.5)

        scored_candidates.append({
            "report_id": r["report_id"],
            "asset": r["nearby_asset"],
            "depth_cm": r["water_depth_cm"],
            "rainfall_6h": r["rainfall_mm_6h"],
            "sensor_cm": r["sensor_level_cm"],
            "risk_score": round(final_score, 1),
            "severity": calc["severity"],
            "uncertainty": calc["uncertainty_score"],
            "cluster_count": cluster_size,
            "coords": (r["latitude"], r["longitude"]),
            "factors": calc["factors"],
            "recommended_action": calc["recommended_next_verification_step"]
        })

    # Sort descending by risk score
    scored_candidates.sort(key=lambda x: x["risk_score"], reverse=True)

    # Output Summary
    print(f"\n[TRIAGE SUMMARY]")
    print(f"  • Total Ingested: {len(records)}")
    print(f"  • Adversarial Injections Suppressed: {len(suppressed_adversarial)} ({suppressed_adversarial})")
    print(f"  • Outdated / Stale Observations Dropped: {len(stale_records)} ({stale_records})")
    print(f"  • Duplicate Clusters Detected: {len(duplicate_clusters)}")
    for k, v in duplicate_clusters.items():
        print(f"      - Cluster {k}: {v}")
    if contradictory_flags:
        print(f"  • Contradictory Evidence Pairs Flagged for Field Inspection: {contradictory_flags}")

    print("\n==================================================================")
    print("TOP 5 PRIORITY LOCATIONS REQUIRING HUMAN FIELD INSPECTION")
    print("==================================================================")
    for idx, cand in enumerate(scored_candidates[:5], 1):
        print(f"RANK {idx}: [{cand['severity']}] Score: {cand['risk_score']}/100.0 (Uncertainty: {cand['uncertainty']*100:.0f}%)")
        print(f"  • Report: {cand['report_id']} | Cluster Callers: {cand['cluster_count']}")
        print(f"  • Critical Asset: {cand['asset']}")
        print(f"  • Telemetry: Depth={cand['depth_cm']}cm | Rain(6h)={cand['rainfall_6h']}mm | SensorStage={cand['sensor_cm']}cm")
        print(f"  • Coordinates: {cand['coords'][0]:.4f}, {cand['coords'][1]:.4f}")
        print(f"  • Recommended Protocol: {cand['recommended_action']}")
        print("------------------------------------------------------------------")

    return scored_candidates[:5]


if __name__ == "__main__":
    triage_pilot_data()
