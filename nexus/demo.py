"""Simulated site demo — the pilot version.

Seeds assets, fires fake RFID/GPS/camera streams, runs the bus,
shows agents eating the 80%, humans only touching the 20%.
Run: python -m nexus.demo
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from .asset_bus import AssetBus, AssetEvent
from .agent_handlers import register_default_handlers
from .safety.overlay import SafetyOverlay, restricted_zone_breach, cert_expired
from .efficiency import score_efficiency


def seed_site(bus: AssetBus) -> None:
    bus.assets["W-001"] = bus.assets.get("W-001") or __import__("nexus.ontology.asset_schema", fromlist=["create_asset"]).create_asset("worker", "W-001", name="Jack Jack", zone="bay-3", status="idle")
    bus.assets["M-001"] = bus.assets.get("M-001") or __import__("nexus.ontology.asset_schema", fromlist=["create_asset"]).create_asset("machine", "M-001", name="forklift-7", fuel=87.0, zone="bay-3")
    bus.assets["Z-001"] = bus.assets.get("Z-001") or __import__("nexus.ontology.asset_schema", fromlist=["create_asset"]).create_asset("zone", "Z-001", name="restricted-bay", restricted=True)


def run_demo() -> None:
    safety = SafetyOverlay()
    safety.add_rule(restricted_zone_breach, "EMERGENCY_STOP", severity="critical")
    safety.add_rule(cert_expired, "reassign", severity="warning")
    bus = AssetBus(safety=safety)
    register_default_handlers(bus)
    seed_site(bus)

    print("=== NEXUS ASSET COUSIN — PILOT DEMO ===")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}\n")

    # Stream 1: worker goes idle -> auto-dispatch
    e1 = AssetEvent(event_id="e1", asset_id="W-001", asset_type="worker", event_type="status_change", payload={"status": "idle"}, source="manual")
    bus.ingest(e1)
    print(f"[RFID] W-001 idle -> actions: {e1.actions_taken}")

    # Stream 2: forklift fuel drops -> maintenance
    e2 = AssetEvent(event_id="e2", asset_id="M-001", asset_type="machine", event_type="status_change", payload={"fuel": 15.0}, source="sensor")
    bus.ingest(e2)
    print(f"[SENSOR] M-001 fuel 15% -> actions: {e2.actions_taken}")

    # Stream 3: hazard in zone -> reroute
    e3 = AssetEvent(event_id="e3", asset_id="Z-001", asset_type="zone", event_type="hazard", payload={"zone": "restricted-bay", in_restricted_zone: True}, source="camera")
    bus.ingest(e3)
    print(f"[CAMERA] hazard in restricted-bay -> actions: {e3.actions_taken}")

    # Stream 4: worker breaches restricted zone -> kill switch
    e4 = AssetEvent(event_id="e4", asset_id="W-001", asset_type="worker", event_type="location_update", payload={"in_restricted_zone": True}, source="gps")
    bus.ingest(e4)
    print(f"[GPS] W-001 in restricted zone -> actions: {e4.actions_taken} human_required={e4.human_required}")

    print("\n=== EFFICIENCY SCORES ===")
    for aid, a in bus.assets.items():
        print(f"  {aid}: {score_efficiency(a):.1f}")

    print("\n=== PILOT COMPLETE ===")
    print("Agents handled dispatch, maintenance, routing, kill switch.")
    print("Humans only needed for the critical breach. 80/20 delivered.")
    print(f"Finished: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    run_demo()
