"""AI agent handlers for the asset bus.

These are the autonomous decision-makers that eat the boring 80%.
Dispatch, routing, maintenance triggers, efficiency nudges.
Human-in-the-loop only for the 20% that needs a brain.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .asset_bus import AssetBus, AssetEvent
from .efficiency import score_efficiency
from .safety.overlay import SafetyOverlay

ROOT = Path(__file__).resolve().parent.parent
DECISION_LOG = ROOT / "config" / "agent_decisions.jsonl"


def _log_decision(decision: dict[str, Any]) -> None:
    DECISION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DECISION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(decision, default=str) + "\n")


def dispatch_handler(event: AssetEvent, bus: AssetBus) -> None:
    """Auto-dispatch idle workers/machines to open work orders."""
    asset = bus.assets.get(event.asset_id)
    if not asset:
        return
    if asset.type == "worker" and asset.properties.get("status") == "idle":
        action = bus.dispatch_action(event.asset_id, "dispatch", reason="auto-dispatch idle worker")
        if action.get("ok"):
            event.actions_taken.append("auto_dispatched")
            _log_decision({"ts": datetime.now(timezone.utc).isoformat(), "asset": event.asset_id, "action": "dispatch", "reason": "idle"})


def maintenance_handler(event: AssetEvent, bus: AssetBus) -> None:
    """Trigger maintenance when fuel low or cert expiring."""
    asset = bus.assets.get(event.asset_id)
    if not asset:
        return
    if asset.type == "machine" and asset.properties.get("fuel", 100) < 20:
        action = bus.dispatch_action(event.asset_id, "schedule_maintenance", reason="low fuel auto-trigger")
        if action.get("ok"):
            event.actions_taken.append("maintenance_scheduled")
            _log_decision({"ts": datetime.now(timezone.utc).isoformat(), "asset": event.asset_id, "action": "schedule_maintenance", "reason": "low_fuel"})


def routing_handler(event: AssetEvent, bus: AssetBus) -> None:
    """Re-route around hazards."""
    if event.event_type == "hazard":
        for aid, a in bus.assets.items():
            if a.type == "worker" and a.properties.get("zone") == event.payload.get("zone"):
                bus.dispatch_action(aid, "reassign", reason=f"hazard in {event.payload.get('zone')}")
                event.actions_taken.append(f"rerouted_{aid}")


def efficiency_nudge_handler(event: AssetEvent, bus: AssetBus) -> None:
    """Score and nudge low performers."""
    asset = bus.assets.get(event.asset_id)
    if not asset:
        return
    score = score_efficiency(asset)
    asset.efficiency_score = score
    if score < 40 and asset.type == "worker":
        bus.dispatch_action(event.asset_id, "flag_hazard", reason=f"efficiency {score} below threshold")
        event.actions_taken.append("efficiency_flagged")


def register_default_handlers(bus: AssetBus) -> None:
    """Wire the agents onto the bus."""
    bus.register_handler(lambda e: dispatch_handler(e, bus))
    bus.register_handler(lambda e: maintenance_handler(e, bus))
    bus.register_handler(lambda e: routing_handler(e, bus))
    bus.register_handler(lambda e: efficiency_nudge_handler(e, bus))
