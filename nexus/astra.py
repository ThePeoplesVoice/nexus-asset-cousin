"""Minimal Astra compatibility shim for the runtime post-success flow."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ASTRA_PATH = ROOT / "config" / "astra.json"


def _default_astra(reputation: dict[str, Any] | None = None) -> dict[str, Any]:
    rep = reputation or {}
    score = float(rep.get("score", 0.0) or 0.0)
    return {
        "balance": max(0, int(score * 10)),
        "score": score,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "stable",
    }


def load_astra(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else ASTRA_PATH
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else _default_astra()
    except Exception:
        return _default_astra()


def save_astra(data: dict[str, Any], path: str | Path | None = None) -> Path:
    target = Path(path) if path is not None else ASTRA_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def refresh_astra(*, persist: bool = True, reputation: dict[str, Any] | None = None) -> dict[str, Any]:
    data = _default_astra(reputation)
    if persist:
        save_astra(data)
    return data
