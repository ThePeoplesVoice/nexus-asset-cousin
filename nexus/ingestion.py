"""Data ingestion adapters — swallow whatever the customer already owns.

No new hardware. No cell towers. No Bluetooth mind-reading. No nano-chip routers.
Just normalize RFID, GPS, camera, ERP, PLC streams into AssetEvents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from .asset_bus import AssetEvent


class IngestionAdapter(ABC):
    """Base adapter. Every customer stream gets one."""

    source: str = "unknown"

    @abstractmethod
    def normalize(self, raw: dict[str, Any]) -> AssetEvent:
        ...

    def stamp(self, event: AssetEvent) -> AssetEvent:
        event.timestamp = datetime.now(timezone.utc).isoformat()
        event.source = self.source
        return event


class RFIDAdapter(IngestionAdapter):
    source = "rfid"

    def normalize(self, raw: dict[str, Any]) -> AssetEvent:
        return self.stamp(AssetEvent(
            event_id=raw.get("badge_id", "rfid-unknown"),
            asset_id=raw.get("asset_id", raw.get("badge_id", "unknown")),
            asset_type=raw.get("asset_type", "worker"),
            event_type="location_update",
            payload={
                "zone": raw.get("zone"),
                "in_restricted_zone": raw.get("zone") in (raw.get("restricted_zones") or []),
                "reader": raw.get("reader_id"),
            },
        ))


class GPSAdapter(IngestionAdapter):
    source = "gps"

    def normalize(self, raw: dict[str, Any]) -> AssetEvent:
        return self.stamp(AssetEvent(
            event_id=raw.get("device_id", "gps-unknown"),
            asset_id=raw.get("asset_id", raw.get("device_id", "unknown")),
            asset_type=raw.get("asset_type", "machine"),
            event_type="location_update",
            payload={
                "lat": raw.get("lat"),
                "lon": raw.get("lon"),
                "speed": raw.get("speed", 0),
                "heading": raw.get("heading"),
            },
        ))


class CameraAdapter(IngestionAdapter):
    source = "camera"

    def normalize(self, raw: dict[str, Any]) -> AssetEvent:
        return self.stamp(AssetEvent(
            event_id=raw.get("camera_id", "cam-unknown"),
            asset_id=raw.get("asset_id", "unknown"),
            asset_type=raw.get("asset_type", "zone"),
            event_type="status_change",
            payload={
                "detected_objects": raw.get("objects", []),
                "ppe_violation": raw.get("ppe_violation", False),
                "zone": raw.get("zone"),
            },
        ))


class ERPAdapter(IngestionAdapter):
    source = "erp"

    def normalize(self, raw: dict[str, Any]) -> AssetEvent:
        return self.stamp(AssetEvent(
            event_id=raw.get("work_order_id", "erp-unknown"),
            asset_id=raw.get("asset_id", "unknown"),
            asset_type=raw.get("asset_type", "worker"),
            event_type=raw.get("event_type", "dispatch"),
            payload={
                "work_order": raw.get("work_order_id"),
                "priority": raw.get("priority", "normal"),
                "assigned_to": raw.get("assigned_to"),
                "due": raw.get("due"),
            },
        ))
