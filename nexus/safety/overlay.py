"""Compatibility shim for the root safety overlay."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_root = Path(__file__).resolve().parents[2] / "safety" / "overlay.py"
_spec = spec_from_file_location("nexus_asset_cousin_safety_overlay", _root)
assert _spec and _spec.loader is not None
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

SafetyOverlay = _module.SafetyOverlay
restricted_zone_breach = _module.restricted_zone_breach
cert_expired = _module.cert_expired

__all__ = ["SafetyOverlay", "restricted_zone_breach", "cert_expired"]
