"""Sensors — the telemetry the official integration does not expose."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfDataRate,
    UnitOfTemperature,
    UnitOfTime,
    DEGREE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import dig
from .entity import StarlinkEntity


@dataclass(frozen=True, kw_only=True)
class StarlinkSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict], object]
    attrs_fn: Callable[[dict], dict] | None = None


def _wifi_clients_attrs(data: dict) -> dict:
    clients = dig(data, "clients") or []
    return {
        "clients": [
            {k: c.get(k) for k in ("name", "macAddress", "iface", "role")}
            for c in clients
        ]
    }


DISH_SENSORS: tuple[StarlinkSensorDescription, ...] = (
    StarlinkSensorDescription(
        key="dl_restricted_reason",
        value_fn=lambda d: dig(d, "dlBandwidthRestrictedReason") or "NONE",
    ),
    StarlinkSensorDescription(
        key="ul_restricted_reason",
        value_fn=lambda d: dig(d, "ulBandwidthRestrictedReason") or "NONE",
    ),
    StarlinkSensorDescription(
        key="azimuth",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "boresightAzimuthDeg"),
    ),
    StarlinkSensorDescription(
        key="elevation",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "boresightElevationDeg"),
    ),
    StarlinkSensorDescription(
        key="desired_azimuth",
        native_unit_of_measurement=DEGREE,
        value_fn=lambda d: dig(d, "alignmentStats.desiredBoresightAzimuthDeg"),
    ),
    StarlinkSensorDescription(
        key="desired_elevation",
        native_unit_of_measurement=DEGREE,
        value_fn=lambda d: dig(d, "alignmentStats.desiredBoresightElevationDeg"),
    ),
    StarlinkSensorDescription(
        key="tilt_angle",
        native_unit_of_measurement=DEGREE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "alignmentStats.tiltAngleDeg"),
    ),
    StarlinkSensorDescription(
        key="attitude_uncertainty",
        native_unit_of_measurement=DEGREE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "alignmentStats.attitudeUncertaintyDeg"),
    ),
    StarlinkSensorDescription(
        key="obstruction",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda d: (dig(d, "obstructionStats.fractionObstructed") or 0) * 100,
    ),
    StarlinkSensorDescription(
        key="signal_quality",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: (dig(d, "signalQuality") or 0) * 100,
    ),
    StarlinkSensorDescription(
        key="gps_sats",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "gpsStats.gpsSats"),
    ),
    StarlinkSensorDescription(
        key="downlink",
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "downlinkThroughputBps"),
    ),
    StarlinkSensorDescription(
        key="uplink",
        native_unit_of_measurement=UnitOfDataRate.BITS_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "uplinkThroughputBps"),
    ),
    StarlinkSensorDescription(
        key="pop_ping",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "popPingLatencyMs"),
    ),
    StarlinkSensorDescription(
        key="uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "deviceState.uptimeS"),
    ),
    StarlinkSensorDescription(
        key="mobility_class",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "mobilityClass"),
    ),
    StarlinkSensorDescription(
        key="class_of_service",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "classOfService"),
    ),
    StarlinkSensorDescription(
        key="disablement_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "disablementCode"),
    ),
    StarlinkSensorDescription(
        key="software_update_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "softwareUpdateState"),
    ),
    StarlinkSensorDescription(
        key="hardware_self_test",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "_hardwareSelfTest"),
    ),
    StarlinkSensorDescription(
        key="bootcount",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "deviceInfo.bootcount"),
    ),
)

ROUTER_SENSORS: tuple[StarlinkSensorDescription, ...] = (
    StarlinkSensorDescription(
        key="public_ip",
        value_fn=lambda d: dig(d, "publicIpv4"),
    ),
    StarlinkSensorDescription(
        key="wan_ping",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "pingLatencyMs"),
    ),
    StarlinkSensorDescription(
        key="pop_ping",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "popPingLatencyMs"),
    ),
    StarlinkSensorDescription(
        key="dish_ping",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: dig(d, "dishPingLatencyMs"),
    ),
    StarlinkSensorDescription(
        key="clients",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: len(dig(d, "clients") or []),
        attrs_fn=_wifi_clients_attrs,
    ),
    StarlinkSensorDescription(
        key="radio_2ghz_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "_radio_RF_2GHZ.thermalStatus.temp2"),
    ),
    StarlinkSensorDescription(
        key="radio_5ghz_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "_radio_RF_5GHZ.thermalStatus.temp2"),
    ),
    StarlinkSensorDescription(
        key="dish_disablement_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "dishDisablementCode"),
    ),
    StarlinkSensorDescription(
        key="software_update_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "softwareUpdateStats.state"),
    ),
    StarlinkSensorDescription(
        key="uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "deviceState.uptimeS"),
    ),
    StarlinkSensorDescription(
        key="bootcount",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: dig(d, "deviceInfo.bootcount"),
    ),
)


class StarlinkSensor(StarlinkEntity, SensorEntity):
    entity_description: StarlinkSensorDescription

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self):
        fn = self.entity_description.attrs_fn
        return fn(self.coordinator.data or {}) if fn else None


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    data = entry.runtime_data
    entities: list[StarlinkSensor] = []
    if "dish" in data:
        entities += [StarlinkSensor(data["dish"], "dish", d) for d in DISH_SENSORS]
    if "router" in data:
        entities += [
            StarlinkSensor(data["router"], "router", d) for d in ROUTER_SENSORS
        ]
    async_add_entities(entities)
