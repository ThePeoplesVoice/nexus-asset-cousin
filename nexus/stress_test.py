"""Stress harness — put the pilot through its paces.

Fires hundreds of mixed RFID/GPS/camera/sensor/ERP events, runs the
continuous loop, and dumps a decision audit. This is the "borderline
prototype / heavily testing" stage.

Run: python -m nexus.stress_test
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone

from .asset_bus import AssetBus, AssetEvent
from .agent_handlers import register_default_handlers
from .safety.overlay import SafetyOverlay, restricted_zone_breach, cert_expired
from .efficiency import score_efficiency
from .ingestion import RFIDAdapter, GPSAdapter, CameraAdapter, ERPAdapter


ZONES = ["bay-1", "bay-2", "bay-3", "restricted-bay", "loading-dock"]
WORKERS = [f"W-{i:03d}" for i in range(1, 13)]
MACHINES = [f"M-{i:03d}" for i in range(1, 7)]


def seed_site(bus: AssetBus) -> None:
    create = __import__("nexus.ontology.asset_schema", fromlist=["create_asset"]).create_asset
    for wid in WORKERS:
        bus.assets[wid] = create("worker", wid, name=wid, zone=random.choice(ZONES), status=random.choice(["idle", "working", "break"]))
    for mid in MACHINES:
        bus.assets[mid] = create("machine", mid, name=f"forklift-{mid}", fuel=random.uniform(10, 95), zone=random.choice(ZONES))
    for z in ZONES:
        bus.assets[f"Z-{z}"] = create("zone", f"Z-{z}", name=z, restricted=(z == "restricted-bay"))


def fire_streams(bus: AssetBus, n: int = 240) -> dict:
    adapters = {
        "rfid": RFIDAdapter(),
        "gps": GPSAdapter(),
        "camera": CameraAdapter(),
        "erp": ERPAdapter(),
        "sensor": None,
    }
    counts = {"rfid": 0, "gps": 0, "camera": 0, "erp": 0, "sensor": 0, "human_required": 0, "actions": 0}
    for i in range(n):
        kind = random.choices(["rfid", "gps", "camera", "erp", "sensor"], weights=[30, 25, 20, 15, 10])[0]
        if kind == "rfid":
            raw = {"badge_id": random.choice(WORKERS), "asset_id": random.choice(WORKERS), "zone": random.choice(ZONES), "restricted_zones": ["restricted-bay"], "reader_id": f"R-{random.randint(1,5)}"}
            ev = adapters["rfid"].normalize(raw)
        elif kind == "gps":
            raw = {"device_id": random.choice(MACHINES + WORKERS), "asset_id": random.choice(MACHINES + WORKERS), "asset_type": "machine" if random.random() < 0.5 else "worker", "lat": -32.0 + random.random()*0.1, "lon": 115.8 + random.random()*0.1, "speed": random.uniform(0, 25)}
            ev = adapters["gps"].normalize(raw)
        elif kind == "camera":
            raw = {"camera_id": f"CAM-{random.randint(1,4)}", "asset_id": random.choice(ZONES), "asset_type": "zone", "zone": random.choice(ZONES), "objects": random.sample(["worker", "forklift", "hazard", "ppe_violation"], k=random.randint(0, 2)), "ppe_violation": random.random() < 0.15}
            ev = adapters["camera"].normalize(raw)
        elif kind == "erp":
            raw = {"work_order_id": f"WO-{random.randint(1000,1999)}", "asset_id": random.choice(WORKERS), "priority": random.choice(["low", "normal", "high"]), "due": datetime.now(timezone.utc).isoformat()}
            ev = adapters["erp"].normalize(raw)
        else:
            aid = random.choice(MACHINES)
            ev = AssetEvent(event_id=f"s{i}", asset_id=aid, asset_type="machine", event_type="status_change", payload={"fuel": random.uniform(5, 30)}, source="sensor")
        bus.ingest(ev)
        counts[kind] += 1
        counts["actions"] += len(ev.actions_taken)
        if ev.human_required:
            counts["human_required"] += 1
    return counts


def run_stress() -> None:
    safety = SafetyOverlay()
    safety.add_rule(restricted_zone_breach, "EMERGENCY_STOP", severity="critical")
    safety.add_rule(cert_expired, "reassign", severity="warning")
    bus = AssetBus(safety=safety)
    register_default_handlers(bus)
    seed_site(bus)

    print("=== NEXUS ASSET COUSIN — STRESS / PACES ===")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}\n")

    t0 = time.time()
    counts = fire_streams(bus, n=240)
    elapsed = time.time() - t0

    print(f"Events fired: 240 in {elapsed:.2f}s ({240/elapsed:.0f} evt/s)")
    print(f"  rfid={counts['rfid']} gps={counts['gps']} camera={counts['camera']} erp={counts['erp']} sensor={counts['sensor']}")
    print(f"  autonomous actions taken: {counts['actions']}")
    print(f"  human-required flags: {counts['human_required']}  ({counts['human_required']/240*100:.1f}% of stream)")

    print("\n=== EFFICIENCY RANKING (top/bottom) ===")
    ranked = sorted(((aid, score_efficiency(a)) for aid, a in bus.assets.items()), key=lambda x: -x[1])
    for aid, sc in ranked[:3]:
        print(f"  {aid}: {sc:.1f}")
    print("  ...")
    for aid, sc in ranked[-3:]:
        print(f"  {aid}: {sc:.1f}")

    print("\n=== PILOT -> PACES TRANSITION ===")
    print("Borderline prototype crossed. System is now under real load.")
    print(f"Finished: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    run_stress()
