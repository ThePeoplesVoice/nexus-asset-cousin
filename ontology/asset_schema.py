"""Asset Ontology schema — the typed objects Palantir charges billions for.

Every asset becomes a living object with properties, relationships, and allowed actions.
Copied from Nexus config/state pattern, pointed at physical/digital assets.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Asset:
    """Base asset object."""
    id: str
    type: str  # worker, forklift, truck, sensor, machine, zone
    properties: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    allowed_actions: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    safety_status: str = "clear"  # clear, warning, critical
    efficiency_score: float = 0.0


@dataclass
class Worker(Asset):
    type: str = "worker"
    cert_expiry: datetime | None = None


@dataclass
class Machine(Asset):
    type: str = "machine"
    fuel: float = 100.0
    maintenance_due: datetime | None = None


# Allowed actions example — the "write-back" layer
ALLOWED_ACTIONS = {
    "worker": ["dispatch", "reassign", "flag_hazard", "request_break"],
    "machine": ["dispatch", "slowdown", "shutdown", "schedule_maintenance"],
    "zone": ["restrict", "clear", "alert"],
}


def create_asset(asset_type: str, asset_id: str, **props) -> Asset:
    """Factory. Returns typed object ready for the event bus."""
    if asset_type == "worker":
        return Worker(id=asset_id, properties=props)
    if asset_type == "machine":
        return Machine(id=asset_id, properties=props)
    return Asset(id=asset_id, type=asset_type, properties=props)
