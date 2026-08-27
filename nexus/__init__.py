"""Nexus Asset Cousin core — ported from Grok GitHub Nexus.

Self-measuring, self-auditing, self-growing loop pointed at physical assets.
"""

__version__ = "0.1.0-asset"

from .runtime import after_successful_analysis, log_success
from .providers import call_grok, call_claude, format_api_error, ARA_SYSTEM
from .audit import structural_health, alignment_signals, build_self_audit_prompt
from .reputation import compute_reputation, refresh_reputation, load_reputation
from .presence import load_presence, format_presence_for_prompt
from .asset_bus import AssetBus, AssetEvent
from .ingestion import IngestionAdapter, RFIDAdapter, GPSAdapter, CameraAdapter, ERPAdapter
from .efficiency import EfficiencyScorer
from .ontology.asset_schema import Asset, Worker, Machine, create_asset, ALLOWED_ACTIONS
from .safety.overlay import SafetyOverlay

__all__ = [
    "after_successful_analysis",
    "log_success",
    "call_grok",
    "call_claude",
    "format_api_error",
    "ARA_SYSTEM",
    "structural_health",
    "alignment_signals",
    "build_self_audit_prompt",
    "compute_reputation",
    "refresh_reputation",
    "load_reputation",
    "load_presence",
    "format_presence_for_prompt",
    "AssetBus",
    "AssetEvent",
    "IngestionAdapter",
    "RFIDAdapter",
    "GPSAdapter",
    "CameraAdapter",
    "ERPAdapter",
    "EfficiencyScorer",
    "Asset",
    "Worker",
    "Machine",
    "create_asset",
    "ALLOWED_ACTIONS",
    "SafetyOverlay",
]
