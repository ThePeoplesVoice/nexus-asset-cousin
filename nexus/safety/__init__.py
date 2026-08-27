"""Compatibility wrapper for the safety package."""

try:
    from safety.overlay import SafetyOverlay, cert_expired, restricted_zone_breach
except ImportError:  # pragma: no cover
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    _root = Path(__file__).resolve().parents[2] / "safety" / "overlay.py"
    _spec = spec_from_file_location("compat_safety_overlay", _root)
    _module = module_from_spec(_spec)
    assert _spec and _spec.loader is not None
    _spec.loader.exec_module(_module)
    SafetyOverlay = _module.SafetyOverlay
    restricted_zone_breach = _module.restricted_zone_breach
    cert_expired = _module.cert_expired

__all__ = ["SafetyOverlay", "restricted_zone_breach", "cert_expired"]
