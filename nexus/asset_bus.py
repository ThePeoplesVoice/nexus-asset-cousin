"""Asset event bus — the commit/branch/merge/action loop pointed at physical assets.

Every asset event is a typed commit. Agents branch on it, merge decisions,
write actions back. Same closed loop as Grok GitHub Nexus, just bleeding money instead of code.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .ontology.asset_schema import Asset, create_asset
from .safety.overlay import SafetyOverlay

ROOT = Path(__file__).resolve().parent.parent
EVENT_LOG = ROOT / "config" / "asset_events.jsonl"


@dataclass
class AssetEvent:
    """A single asset event — the unit of work."""
    event_id: str
    asset_id: str
    asset_type: str
    event_type: str  # location_update, status_change, hazard, cert_expiry, maintenance_due, dispatch
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "unknown"  # rfid, gps, camera, erp, manual
    safety_triggered: list[dict] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    human_required: bool = False


class AssetBus:
    """Central event bus. Ingest → evaluate safety → score efficiency → dispatch actions."""

    def __init__(self, safety: SafetyOverlay | None = None):
        self.safety = safety or SafetyOverlay()
        self.assets: dict[str, Asset] = {}
        self.handlers: list[Callable[[AssetEvent], None]] = []
        self._load_assets()

    def _load_assets(self) -> None:
        # Stub: in production this hydrates from ERP/DB. For now, seed examples.
        if not self.assets:
            self.assets["W-001"] = create_asset("worker", "W-001", name="Jack Jack", zone="bay-3")
            self.assets["M-001"] = create_asset("machine", "M-001", name="forklift-7", fuel=87.0)

    def register_handler(self, handler: Callable[[AssetEvent], None]) -> None:
        self.handlers.append(handler)

    def ingest(self, event: AssetEvent) -> AssetEvent:
        """Main entry: an asset event lands here."""
        asset = self.assets.get(event.asset_id)
        if asset is None:
            asset = create_asset(event.asset_type, event.asset_id, **event.payload)
            self.assets[event.asset_id] = asset

        # Update asset properties from payload
        asset.properties.update(event.payload)
        asset.last_updated = datetime.now(timezone.utc)

        # Safety evaluation — the kill switch lives here
        triggered = self.safety.evaluate(asset)
        event.safety_triggered = triggered
        for t in triggered:
            event.actions_taken.append(t["action"])
            if t["severity"] == "critical":
                event.human_required = True

        # Dispatch to handlers (efficiency scoring, AI agents, write-backs)
        for handler in self.handlers:
            try:
                handler(event)
            except Exception as e:
                event.actions_taken.append(f"handler_error:{str(e)[:60]}")

        self._persist_event(event)
        return event

    def _persist_event(self, event: AssetEvent) -> None:
        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with EVENT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), default=str) + "\n")

    def dispatch_action(self, asset_id: str, action: str, reason: str = "") -> dict[str, Any]:
        """Write-back layer. In production this hits the ERP/PLC. Here it logs."""
        asset = self.assets.get(asset_id)
        if not asset:
            return {"ok": False, "error": f"asset {asset_id} not found"}
        if action not in asset.allowed_actions and action not in ("EMERGENCY_STOP",):
            return {"ok": False, "error": f"action {action} not allowed for {asset.type}"}
        record = {
            "asset_id": asset_id,
            "action": action,
            "reason": reason,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        # TODO: actual write-back to customer ERP
        return {"ok": True, "record": record}
