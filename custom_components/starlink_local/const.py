"""Constants and entity descriptions for Starlink Local."""
from __future__ import annotations

DOMAIN = "starlink_local"

CONF_DISH_HOST = "dish_host"
CONF_ROUTER_HOST = "router_host"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_DISH_HOST = "192.168.100.1:9200"
DEFAULT_ROUTER_HOST = "192.168.1.1:9000"

SCAN_INTERVAL_SECONDS = 30
MAP_SCAN_INTERVAL_SECONDS = 300  # obstruction map is ~85 KB, poll it slowly


def dig(data: dict | None, path: str):
    """Walk a dotted path through nested dicts, returning None on any miss."""
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur
