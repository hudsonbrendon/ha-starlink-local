<p align="center">
  <img src="custom_components/starlink_local/brand/logo@2x.png" alt="Starlink Local" height="128">
</p>

# Starlink Local for Home Assistant

[![Tests](https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/tests.yml/badge.svg)](https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/tests.yml)
[![Hassfest](https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/hassfest.yml/badge.svg)](https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/hassfest.yml)
[![HACS](https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/validate.yml/badge.svg)](https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/hudsonbrendon/ha-starlink-local?sort=semver)](https://github.com/hudsonbrendon/ha-starlink-local/releases)
[![Downloads](https://img.shields.io/github/downloads/hudsonbrendon/ha-starlink-local/total)](https://github.com/hudsonbrendon/ha-starlink-local/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.10.0%2B-18BCF2?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/hudsonbrendon/ha-starlink-local)](LICENSE)

Richer **local** telemetry for your Starlink **dish and WiFi router**, straight from
their on-device gRPC API — no Starlink account, no cloud. It surfaces everything the
official Home Assistant `starlink` integration leaves out: antenna alignment, bandwidth
restriction reasons, WiFi clients, radio temperatures, router pings, and a rendered
obstruction map.

> Read-only. Starlink gates every write (config, stow, reboot) behind account auth,
> so this integration deliberately exposes **monitoring only**.

## Features

- 🛰️ **Alignment**: current azimuth/elevation vs. the dish's *desired* azimuth/elevation,
  tilt angle and attitude uncertainty — the numbers you need to aim a Mini by hand.
- 🐢 **Bandwidth restriction reason** (`LOW_SPEED_POLICY_LIMIT`, `POLICY_LIMIT`, …) as a
  sensor and a `Bandwidth restricted` binary sensor — the field that explains "slow but
  connected".
- 🗺️ **Obstruction map** rendered to a camera entity (clear/obstructed/unmapped).
- 📊 Dish sensors: downlink/uplink throughput, PoP ping, signal quality, fraction
  obstructed, GPS satellites, mobility class, class of service, disablement code,
  software-update state, hardware self-test, uptime, boot count.
- 📶 Router sensors: public IPv4, WAN/PoP/dish ping latency, WiFi client count (with the
  full client list as attributes), 2.4/5 GHz radio temperatures, dish disablement code,
  software-update state, uptime, boot count.
- 🔔 Binary sensors: bandwidth restricted, SNR above noise floor, GPS valid, has alerts,
  setup complete, outdoor mode.
- 🌐 Dish **and** router, each as its own device.
- ⚙️ Config, **reconfigure** and **options** (update interval) flows.
- 🌎 Translations: English, Português (Brasil), Español.

## How it works

The dish (`192.168.100.1:9200`) and the Starlink router (`192.168.1.1:9000`) both expose
the `SpaceX.API.Device.Device` gRPC service with reflection enabled. This integration
builds its request/stub classes from that reflection at runtime (via
[`yagrc`](https://pypi.org/project/yagrc/)), so there are no vendored protobufs to drift
against firmware updates. Home Assistant must have a network route to those addresses —
typically a Wi-Fi/LAN link into the Starlink router's subnet.

## Installation

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hudsonbrendon&repository=ha-starlink-local&category=integration)
[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=starlink_local)

### HACS (recommended)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/hudsonbrendon/ha-starlink-local`, category **Integration**.
2. Install **Starlink Local**, then restart Home Assistant.
3. **Settings → Devices & Services → Add Integration → Starlink Local**.

### Manual

Copy `custom_components/starlink_local` into your HA `config/custom_components/` and restart.

## Configuration

The config flow asks for two gRPC endpoints, pre-filled with the Starlink defaults:

| Field | Default |
|-------|---------|
| Dish (host:port) | `192.168.100.1:9200` |
| Router (host:port) | `192.168.1.1:9000` |

Leave a field empty to skip that device. After setup, use **Configure** to change the
update interval (5–3600 s, default 30), or **Reconfigure** to change the endpoints.

## Credits

Built by [@hudsonbrendon](https://github.com/hudsonbrendon). Pairs well with the
[Starlink Local Card](https://github.com/hudsonbrendon/ha-starlink-local-card).

## License

MIT
