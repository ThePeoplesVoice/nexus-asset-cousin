"""Minimal context helpers used by the self-audit workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PROGRESSIVE_PATH = ROOT / "config" / "progressive.json"
USAGE_PATH = ROOT / "config" / "usage_stats.json"


def _default_progressive() -> dict[str, Any]:
    return {
        "version": "0.1.0-asset",
        "phase": "bootstrap",
        "layer1_enabled": True,
        "mission": "Turn physical asset operations into a living, self-auditing closed loop.",
    }


def load_progressive(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else PROGRESSIVE_PATH
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else _default_progressive()
    except Exception:
        return _default_progressive()


def load_usage_stats(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else USAGE_PATH
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {
        "version": "0.1.0-asset",
        "total_successful_analyses": 0,
        "by_type": {},
        "last_updated": None,
    }


def layer1_enabled(progressive: dict[str, Any] | None = None) -> bool:
    data = progressive if progressive is not None else load_progressive()
    return bool(data.get("layer1_enabled", True))


def current_phase(progressive: dict[str, Any] | None = None) -> str:
    data = progressive if progressive is not None else load_progressive()
    return str(data.get("phase") or "bootstrap")


def load_context() -> str:
    prog = load_progressive()
    return (
        "Nexus Asset Cousin operating context\n"
        f"- phase: {current_phase(prog)}\n"
        f"- layer1_enabled: {layer1_enabled(prog)}\n"
        f"- version: {prog.get('version', '0.1.0-asset')}\n"
        f"- mission: {prog.get('mission', 'Operational continuity for physical assets.') }\n"
        "- constraint: prioritize truth, high signal, maintainability, and safety over novelty."
    )
