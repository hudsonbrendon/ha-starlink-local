"""Binary sensors for dish/router boolean health states."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import dig
from .entity import StarlinkEntity

_UNRESTRICTED = {None, "", "NO_LIMIT", "BANDWIDTH_RESTRICTED_REASON_UNSPECIFIED"}


@dataclass(frozen=True, kw_only=True)
class StarlinkBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict], bool | None]


DISH_BINARY: tuple[StarlinkBinaryDescription, ...] = (
    StarlinkBinaryDescription(
        key="bandwidth_restricted",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda d: dig(d, "dlBandwidthRestrictedReason") not in _UNRESTRICTED
        or dig(d, "ulBandwidthRestrictedReason") not in _UNRESTRICTED,
    ),
    StarlinkBinaryDescription(
        key="snr_above_noise_floor",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda d: dig(d, "isSnrAboveNoiseFloor"),
    ),
    StarlinkBinaryDescription(
        key="gps_valid",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "gpsStats.gpsValid"),
    ),
    StarlinkBinaryDescription(
        key="has_alerts",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda d: bool(dig(d, "alerts")),
    ),
)

ROUTER_BINARY: tuple[StarlinkBinaryDescription, ...] = (
    StarlinkBinaryDescription(
        key="setup_complete",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "config.setupComplete"),
    ),
    StarlinkBinaryDescription(
        key="outdoor_mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "config.outdoorMode"),
    ),
)


class StarlinkBinarySensor(StarlinkEntity, BinarySensorEntity):
    entity_description: StarlinkBinaryDescription

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data or {})


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    data = entry.runtime_data
    entities: list[StarlinkBinarySensor] = []
    if "dish" in data:
        entities += [
            StarlinkBinarySensor(data["dish"], "dish", d) for d in DISH_BINARY
        ]
    if "router" in data:
        entities += [
            StarlinkBinarySensor(data["router"], "router", d) for d in ROUTER_BINARY
        ]
    async_add_entities(entities)
