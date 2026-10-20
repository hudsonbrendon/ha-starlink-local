"""Shared coordinator entity with device grouping."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, dig


class StarlinkEntity(CoordinatorEntity):
    """Base entity bound to a dish/router coordinator and a device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, kind: str, description) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._kind = kind  # "dish" or "router"
        self._attr_unique_id = f"{kind}_{description.key}"
        self._attr_translation_key = description.key  # name from translations/*.json
        name = "Starlink Dish" if kind == "dish" else "Starlink Router"
        sw_path = "deviceInfo.softwareVersion"
        hw_path = "deviceInfo.hardwareVersion"
        data = coordinator.data or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, kind)},
            name=name,
            manufacturer="SpaceX",
            model=dig(data, hw_path),
            sw_version=dig(data, sw_path),
        )

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None
