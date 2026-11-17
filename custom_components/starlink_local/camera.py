"""Obstruction map rendered to a PNG camera entity.

Not exposed by the official integration. The dish returns a 123x123 SNR grid
(-1 = unmapped, 0 = obstructed, 1 = clear); we paint it green/red/transparent.
Polled on its own slow cadence because the payload is ~85 KB.
"""
from __future__ import annotations

import io
import time

from homeassistant.components.camera import Camera
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAP_SCAN_INTERVAL_SECONDS


class ObstructionMapCamera(Camera):
    _attr_has_entity_name = True
    _attr_translation_key = "obstruction_map"

    def __init__(self, device, host: str) -> None:
        super().__init__()
        self._device = device
        self._attr_unique_id = "dish_obstruction_map"
        self._cache: bytes | None = None
        self._cache_at = 0.0
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "dish")}, name="Starlink Dish"
        )

    def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        now = time.monotonic()
        if self._cache is not None and now - self._cache_at < MAP_SCAN_INTERVAL_SECONDS:
            return self._cache
        try:
            data = self._device.call("dish_get_obstruction_map")
            self._cache = _render(data)
            self._cache_at = now
        except Exception:  # noqa: BLE001, S110
            pass
        return self._cache


def _render(data: dict) -> bytes:
    from PIL import Image

    rows = int(data["numRows"])
    cols = int(data["numCols"])
    snr = data["snr"]
    img = Image.new("RGBA", (cols, rows))
    px = img.load()
    for i in range(rows):
        base = i * cols
        for j in range(cols):
            v = snr[base + j]
            if v < 0:  # unmapped sky
                px[j, i] = (0, 0, 0, 0)
            elif v == 0:  # obstructed
                px[j, i] = (220, 40, 40, 255)
            else:  # clear, brighter green with stronger signal
                g = 120 + int(min(max(v, 0), 1) * 135)
                px[j, i] = (30, g, 60, 255)
    img = img.resize((cols * 4, rows * 4), Image.NEAREST)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def async_setup_entry(
    hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback
) -> None:
    data = entry.runtime_data
    if "dish" in data:
        async_add_entities([ObstructionMapCamera(data["dish"].device, "dish")])
