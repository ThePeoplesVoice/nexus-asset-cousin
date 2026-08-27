"""Efficiency scoring — the part that makes middle management redundant.

Scores assets on throughput, idle time, safety compliance, and task completion.
Feeds the 80/20 split: agents handle the boring 80, humans get the 20 that needs a brain.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .ontology.asset_schema import Asset


class EfficiencyScorer:
    """Compute a live efficiency score for an asset."""

    def score(self, asset: Asset, recent_events: list[dict] | None = None) -> float:
        events = recent_events or []
        base = 50.0

        # Throughput: more completed tasks = higher
        completed = sum(1 for e in events if e.get("event_type") == "task_complete")
        base += min(completed * 5, 30)

        # Idle penalty
        idle = sum(1 for e in events if e.get("event_type") == "idle")
        base -= min(idle * 3, 20)

        # Safety compliance bonus/penalty
        if asset.safety_status == "clear":
            base += 10
        elif asset.safety_status == "warning":
            base -= 15
        elif asset.safety_status == "critical":
            base -= 40

        # Fuel / maintenance health
        fuel = asset.properties.get("fuel", 100.0)
        if fuel < 20:
            base -= 10
        maint = asset.properties.get("maintenance_due")
        if maint and maint < datetime.now(timezone.utc):
            base -= 15

        asset.efficiency_score = round(max(0.0, min(100.0, base)), 2)
        return asset.efficiency_score

    def rank_assets(self, assets: list[Asset]) -> list[tuple[Asset, float]]:
        scored = [(a, self.score(a)) for a in assets]
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def needs_human(self, asset: Asset, score: float) -> bool:
        """The 20% that actually needs a brain."""
        if asset.safety_status == "critical":
            return True
        if score < 30:
            return True
        if asset.properties.get("fuel", 100) < 10:
            return True
        return False
