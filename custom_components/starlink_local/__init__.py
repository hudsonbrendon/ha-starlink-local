"""Starlink Local — richer local telemetry for the dish and WiFi router."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DISH_HOST,
    CONF_ROUTER_HOST,
    CONF_SCAN_INTERVAL,
    SCAN_INTERVAL_SECONDS,
)
from .coordinator import DishCoordinator, RouterCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CAMERA]

type StarlinkConfigEntry = ConfigEntry[dict]


async def async_setup_entry(hass: HomeAssistant, entry: StarlinkConfigEntry) -> bool:
    scan = entry.options.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL_SECONDS)
    data: dict = {}

    dish_host = entry.data.get(CONF_DISH_HOST)
    if dish_host:
        dish = DishCoordinator(hass, dish_host, scan)
        await dish.async_config_entry_first_refresh()
        data["dish"] = dish

    router_host = entry.data.get(CONF_ROUTER_HOST)
    if router_host:
        router = RouterCoordinator(hass, router_host, scan)
        await router.async_config_entry_first_refresh()
        data["router"] = router

    entry.runtime_data = data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload_on_update))
    return True


async def _reload_on_update(hass: HomeAssistant, entry: StarlinkConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: StarlinkConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
