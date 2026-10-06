"""Select already connected ESPHome water meter sensors in the UI."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector

from .const import CONF_COLD, CONF_HEAT, CONF_HOT, DOMAIN, HEAT_UNITS, NAME, UNIT_FACTORS


def _schema(values: dict[str, Any]) -> vol.Schema:
    """Offer water sensors; keep the hot meter optional during discovery."""
    entity_selector = selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class="water")
    )
    return vol.Schema(
        {
            vol.Required(
                CONF_COLD, description={"suggested_value": values.get(CONF_COLD)}
            ): entity_selector,
            vol.Optional(
                CONF_HOT, description={"suggested_value": values.get(CONF_HOT)}
            ): entity_selector,
            vol.Optional(
                CONF_HEAT, description={"suggested_value": values.get(CONF_HEAT, [])}
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=True)
            ),
        }
    )


def validate_sources(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Require cumulative water sensors and prevent circular subscriptions."""
    errors = {}
    if data.get(CONF_COLD) and data.get(CONF_COLD) == data.get(CONF_HOT):
        errors["base"] = "same_source"
    registry = er.async_get(hass)
    for key in (CONF_COLD, CONF_HOT):
        entity_id = data.get(key)
        if not entity_id:
            if key == CONF_COLD:
                errors[key] = "invalid_source"
            continue
        state = hass.states.get(entity_id)
        registered = registry.async_get(entity_id)
        if registered and registered.platform == DOMAIN:
            errors[key] = "circular_source"
        elif (
            not entity_id.startswith("sensor.")
            or state is None
            or state.attributes.get("device_class") != "water"
            or state.attributes.get("state_class") != "total_increasing"
            or state.attributes.get("unit_of_measurement") not in UNIT_FACTORS
        ):
            errors[key] = "invalid_source"
    heat_sources = data.get(CONF_HEAT, [])
    if len(heat_sources) != len(set(heat_sources)):
        errors[CONF_HEAT] = "duplicate_heat_source"
    for entity_id in heat_sources:
        state = hass.states.get(entity_id)
        registered = registry.async_get(entity_id)
        if registered and registered.platform == DOMAIN:
            errors[CONF_HEAT] = "circular_source"
        elif (
            not entity_id.startswith("sensor.")
            or state is None
            or state.attributes.get("device_class") is not None
            or state.attributes.get("state_class") != "total_increasing"
            or state.attributes.get("unit_of_measurement") not in HEAT_UNITS
        ):
            errors[CONF_HEAT] = "invalid_heat_source"
    return errors


class WaterMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Add one cold/hot meter group."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Configure the sources; unknown readings are allowed during startup."""
        errors = {}
        if user_input is not None:
            errors = validate_sources(self.hass, user_input)
            if not errors:
                await self.async_set_unique_id(user_input[CONF_COLD])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=NAME, data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=_schema(user_input or {}), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Permit adding the hot meter later or changing source entities."""
        return WaterMeterOptionsFlow()


class WaterMeterOptionsFlow(config_entries.OptionsFlow):
    """Change mappings without reflashing ESPHome."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Store the complete replacement mapping, including optional removal."""
        errors = {}
        if user_input is not None:
            errors = validate_sources(self.hass, user_input)
            if not errors:
                for entry in self.hass.config_entries.async_entries(DOMAIN):
                    sources = entry.options or entry.data
                    if (
                        entry.entry_id != self.config_entry.entry_id
                        and sources.get(CONF_COLD) == user_input[CONF_COLD]
                    ):
                        errors["base"] = "already_configured"
                        break
            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry, unique_id=user_input[CONF_COLD]
                )
                return self.async_create_entry(title="", data=user_input)
        values = (
            user_input
            if user_input is not None
            else dict(self.config_entry.options or self.config_entry.data)
        )
        return self.async_show_form(step_id="init", data_schema=_schema(values), errors=errors)
