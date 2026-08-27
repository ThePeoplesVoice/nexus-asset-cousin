"""Minimal usage accounting for successful analyses and asset events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
USAGE_PATH = ROOT / "config" / "usage_stats.json"


def _defaults() -> dict[str, Any]:
    return {
        "version": "0.1.0-asset",
        "total_successful_analyses": 0,
        "by_type": {},
        "last_updated": None,
    }


def load_usage_stats(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else USAGE_PATH
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else _defaults()
    except Exception:
        return _defaults()


def save_usage_stats(data: dict[str, Any], path: str | Path | None = None) -> Path:
    target = Path(path) if path is not None else USAGE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def record_successful_analysis(analysis_type: str, *, persist: bool = True) -> dict[str, Any]:
    stats = load_usage_stats()
    by_type = dict(stats.get("by_type") or {})
    by_type[analysis_type] = int(by_type.get(analysis_type, 0)) + 1
    stats["by_type"] = by_type
    stats["total_successful_analyses"] = int(stats.get("total_successful_analyses", 0)) + 1
    stats["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if persist:
        save_usage_stats(stats)
    return stats
