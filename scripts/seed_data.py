"""
Seed script for FLOODTWIN RESPONDER.
Populates datastore with initial flood reports, river sensors, rainfall stations,
critical assets, and shelters.
"""

import os
import sys

# Ensure root directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.store import store


def seed_all():
    print("==================================================================")
    print("Seeding FloodTwin Responder Data Store...")
    print("==================================================================")
    store.load_initial_data()
    print(f"[OK] Ingested {len(store.reports)} initial ground flood reports.")
    print(f"[OK] Ingested {len(store.sensors)} river stage telemetry sensors.")
    print(f"[OK] Ingested {len(store.rainfall_stations)} Automated Weather Stations (AWS).")
    print(f"[OK] Ingested {len(store.critical_assets)} critical healthcare & infrastructure assets.")
    print(f"[OK] Ingested {len(store.shelters)} designated disaster relief shelters.")
    print(f"[OK] Merkle Audit Log Genesis Root: {store._last_audit_hash}")
    print("==================================================================")
    print("Seeding completed successfully!")


if __name__ == "__main__":
    seed_all()
