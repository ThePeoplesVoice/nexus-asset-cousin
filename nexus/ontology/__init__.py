"""Compatibility wrapper for the ontology package."""

try:
    from ontology.asset_schema import ALLOWED_ACTIONS, Asset, Machine, Worker, create_asset
except ImportError:  # pragma: no cover
    from importlib.util import module_from_spec, spec_from_file_location
    from pathlib import Path

    _root = Path(__file__).resolve().parents[2] / "ontology" / "asset_schema.py"
    _spec = spec_from_file_location("compat_ontology_asset_schema", _root)
    _module = module_from_spec(_spec)
    assert _spec and _spec.loader is not None
    _spec.loader.exec_module(_module)
    ALLOWED_ACTIONS = _module.ALLOWED_ACTIONS
    Asset = _module.Asset
    Machine = _module.Machine
    Worker = _module.Worker
    create_asset = _module.create_asset

__all__ = ["Asset", "Worker", "Machine", "create_asset", "ALLOWED_ACTIONS"]
