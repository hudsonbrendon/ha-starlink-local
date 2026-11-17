"""Data update coordinators for the dish and the router."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import StarlinkDevice
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DishCoordinator(DataUpdateCoordinator[dict]):
    """Polls dish get_status + get_diagnostics into one flat dict."""

    def __init__(self, hass: HomeAssistant, host: str, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} dish",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.device = StarlinkDevice(host)

    def _fetch(self) -> dict:
        status = self.device.call("get_status")
        try:
            diag = self.device.call("get_diagnostics")
            status["_hardwareSelfTest"] = diag.get("hardwareSelfTest")
        except Exception:  # noqa: BLE001 - diagnostics is optional enrichment
            status.setdefault("_hardwareSelfTest", None)
        return status

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except Exception as err:
            raise UpdateFailed(f"dish poll failed: {err}") from err


class RouterCoordinator(DataUpdateCoordinator[dict]):
    """Polls router get_status + get_radio_stats, indexing radios by band."""

    def __init__(self, hass: HomeAssistant, host: str, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} router",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.device = StarlinkDevice(host)

    def _fetch(self) -> dict:
        status = self.device.call("get_status")
        try:
            radio = self.device.call("get_radio_stats")
            for entry in radio.get("radioStats", []):
                # band is RF_2GHZ / RF_5GHZ / RF_5GHZ_HIGH
                status[f"_radio_{entry.get('band')}"] = entry
        except Exception:  # noqa: BLE001, S110
            pass
        return status

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except Exception as err:
            raise UpdateFailed(f"router poll failed: {err}") from err
