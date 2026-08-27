"""Compatibility shim for the root ontology asset schema."""

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

_root = Path(__file__).resolve().parents[2] / "ontology" / "asset_schema.py"
_spec = spec_from_file_location("nexus_asset_cousin_ontology_asset_schema", _root)
_module = module_from_spec(_spec)
assert _spec and _spec.loader is not None
_spec.loader.exec_module(_module)

Asset = _module.Asset
Worker = _module.Worker
Machine = _module.Machine
ALLOWED_ACTIONS = _module.ALLOWED_ACTIONS
create_asset = _module.create_asset

__all__ = ["Asset", "Worker", "Machine", "create_asset", "ALLOWED_ACTIONS"]
