<p align="center">
  <img src="https://raw.githubusercontent.com/hudsonbrendon/ha-starlink-local/main/custom_components/starlink_local/brand/logo%402x.png" alt="Starlink Local" width="300">
</p>

<h1 align="center">Starlink Local for Home Assistant</h1>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS Custom"></a>
  <a href="https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/validate.yml"><img src="https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/validate.yml/badge.svg" alt="Validate"></a>
  <a href="https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/hassfest.yml"><img src="https://github.com/hudsonbrendon/ha-starlink-local/actions/workflows/hassfest.yml/badge.svg" alt="hassfest"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

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
[Starlink animated Lovelace card](https://github.com/hudsonbrendon/starlink-card).

## License

MIT
