"""Config, reconfigure and options flows."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback

from .api import StarlinkDevice
from .const import (
    CONF_DISH_HOST,
    CONF_ROUTER_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_DISH_HOST,
    DEFAULT_ROUTER_HOST,
    DOMAIN,
    SCAN_INTERVAL_SECONDS,
)


def _hosts_schema(dish: str, router: str) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_DISH_HOST, default=dish): str,
            vol.Optional(CONF_ROUTER_HOST, default=router): str,
        }
    )


class StarlinkLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        return await self._hosts_step("user", user_input)

    async def async_step_reconfigure(self, user_input=None) -> ConfigFlowResult:
        return await self._hosts_step("reconfigure", user_input)

    async def _hosts_step(self, step_id, user_input) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        reconfigure = step_id == "reconfigure"
        current = self._get_reconfigure_entry() if reconfigure else None

        if user_input is not None:
            dish = user_input.get(CONF_DISH_HOST, "").strip()
            router = user_input.get(CONF_ROUTER_HOST, "").strip()
            if not dish and not router:
                errors["base"] = "need_one_host"
            elif not await self.hass.async_add_executor_job(
                _probe, dish or None, router or None
            ):
                errors["base"] = "cannot_connect"
            else:
                data = {CONF_DISH_HOST: dish, CONF_ROUTER_HOST: router}
                unique = f"{dish}|{router}"
                if reconfigure:
                    await self.async_set_unique_id(unique)
                    return self.async_update_reload_and_abort(current, data=data)
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Starlink Local", data=data)

        if user_input:
            dish_def, router_def = user_input.get(CONF_DISH_HOST, ""), user_input.get(
                CONF_ROUTER_HOST, ""
            )
        elif current:
            dish_def = current.data.get(CONF_DISH_HOST, DEFAULT_DISH_HOST)
            router_def = current.data.get(CONF_ROUTER_HOST, DEFAULT_ROUTER_HOST)
        else:
            dish_def, router_def = DEFAULT_DISH_HOST, DEFAULT_ROUTER_HOST

        return self.async_show_form(
            step_id=step_id,
            data_schema=_hosts_schema(dish_def, router_def),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return StarlinkLocalOptionsFlow()


class StarlinkLocalOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, SCAN_INTERVAL_SECONDS
        )
        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=3600)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


def _probe(dish: str | None, router: str | None) -> bool:
    """True if at least one configured host answers get_device_info."""
    for host in (dish, router):
        if not host:
            continue
        try:
            StarlinkDevice(host).call("get_device_info", timeout=8)
            return True
        except Exception:  # noqa: BLE001, S112
            continue
    return False
