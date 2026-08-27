"""Decision graph — the kinetic layer that makes the Ontology actually move.

Palantir models nouns (objects) + verbs (actions). We add the decision graph:
every decision is data + logic + action + security, wired into a closed loop
with human-in-the-loop gates for the 20% that needs a brain.

This is NOT a copy of their slide deck. It's the same physics, pointed at
assets, built on the Nexus event bus, and it runs in seconds not slide-decks.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .asset_bus import AssetBus, AssetEvent
from .safety.overlay import SafetyOverlay

ROOT = Path(__file__).resolve().parent.parent
DECISION_LOG = ROOT / "config" / "decision_graph.jsonl"


@dataclass
class DecisionNode:
    """A single node in the decision graph."""
    node_id: str
    decision_type: str  # dispatch, reroute, maintain, flag, escalate
    data_inputs: list[str] = field(default_factory=list)   # which asset props feed it
    logic: str = ""                                       # rule or model ref
    action: str = ""                                      # write-back verb
    security_gate: str = "auto"                          # auto | human | kill
    priority: int = 50
    last_fired: str | None = None


class DecisionGraph:
    """Wires objects -> logic -> actions with governance.

    Every node is a typed decision. Agents fire nodes autonomously for the
    boring 80%. Humans only see nodes gated as 'human' or 'kill'.
    """

    def __init__(self, bus: AssetBus, safety: SafetyOverlay | None = None):
        self.bus = bus
        self.safety = safety or SafetyOverlay()
        self.nodes: dict[str, DecisionNode] = {}
        self._seed_default_nodes()

    def _seed_default_nodes(self) -> None:
        defaults = [
            DecisionNode("D-DISPATCH", "dispatch", ["status", "zone"],
                         "worker idle -> open work order", "dispatch", "auto", 60),
            DecisionNode("D-MAINTAIN", "maintain", ["fuel", "maintenance_due"],
                         "fuel < 20 OR cert expired", "schedule_maintenance", "auto", 70),
            DecisionNode("D-REROUTE", "reroute", ["zone", "hazard"],
                         "hazard in current zone", "reassign", "auto", 80),
            DecisionNode("D-EFFICIENCY", "flag", ["efficiency_score"],
                         "score < 40", "flag_hazard", "human", 40),
            DecisionNode("D-KILL", "escalate", ["in_restricted_zone"],
                         "restricted zone breach", "EMERGENCY_STOP", "kill", 100),
        ]
        for n in defaults:
            self.nodes[n.node_id] = n

    def add_node(self, node: DecisionNode) -> None:
        self.nodes[node.node_id] = node

    def evaluate(self, event: AssetEvent) -> list[dict[str, Any]]:
        """Run the graph against an incoming event. Returns fired decisions."""
        asset = self.bus.assets.get(event.asset_id)
        fired: list[dict[str, Any]] = []
        if not asset:
            return fired

        for node in sorted(self.nodes.values(), key=lambda n: -n.priority):
            if self._matches(node, asset, event):
                gate = node.security_gate
                if gate == "kill" or self.safety.kill_switch_active:
                    gate = "kill"
                record = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "node": node.node_id,
                    "asset": event.asset_id,
                    "decision": node.decision_type,
                    "action": node.action,
                    "gate": gate,
                    "human_required": gate in ("human", "kill"),
                }
                fired.append(record)
                node.last_fired = record["ts"]
                self._persist(record)
                # auto nodes execute immediately; human/kill nodes escalate
                if gate == "auto":
                    self.bus.dispatch_action(event.asset_id, node.action,
                                            reason=f"graph:{node.node_id}")
                else:
                    event.human_required = True
                    event.actions_taken.append(f"escalated:{node.node_id}")
        return fired

    def _matches(self, node: DecisionNode, asset, event: AssetEvent) -> bool:
        props = asset.properties
        if node.node_id == "D-DISPATCH":
            return asset.type == "worker" and props.get("status") == "idle"
        if node.node_id == "D-MAINTAIN":
            return asset.type == "machine" and (props.get("fuel", 100) < 20 or props.get("cert_expired"))
        if node.node_id == "D-REROUTE":
            return event.event_type == "hazard"
        if node.node_id == "D-EFFICIENCY":
            return asset.efficiency_score < 40 and asset.type == "worker"
        if node.node_id == "D-KILL":
            return props.get("in_restricted_zone", False)
        return False

    def _persist(self, record: dict[str, Any]) -> None:
        DECISION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DECISION_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def summary(self) -> dict[str, Any]:
        auto = sum(1 for n in self.nodes.values() if n.security_gate == "auto")
        human = sum(1 for n in self.nodes.values() if n.security_gate == "human")
        kill = sum(1 for n in self.nodes.values() if n.security_gate == "kill")
        return {"total_nodes": len(self.nodes), "auto": auto, "human": human, "kill": kill}
