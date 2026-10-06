"""Protect existing water entries while adding optional HCA totals."""

import pytest
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er

from custom_components.vodomer_esp32_c3_cc1101.const import CONF_COLD, CONF_HEAT, DOMAIN
from custom_components.vodomer_esp32_c3_cc1101.reading import heat_units

from .test_integration import create_entry


def set_heat(hass, value, unit="dilky", state_class="total_increasing"):
    hass.states.async_set(
        "sensor.eitn_00548628_aktualni",
        value,
        {"unit_of_measurement": unit, "state_class": state_class},
    )


@pytest.mark.parametrize("value", ["unknown", "unavailable", "nan", "inf", "-1"])
def test_invalid_heat_values(value):
    assert heat_units(value, "dilky") is None
    assert heat_units("149", "kWh") is None


async def test_heat_add_reset_outage_remove_preserves_water(hass):
    entry, cold, _ = await create_entry(hass, hot=False)
    water_unique_id = er.async_get(hass).async_get(cold).unique_id
    set_heat(hass, "149")
    result = await hass.config_entries.options.async_init(
        entry.entry_id,
        data={CONF_COLD: "sensor.cold_radio", CONF_HEAT: ["sensor.eitn_00548628_aktualni"]},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    unique_id = f"{entry.entry_id}_heat_sensor.eitn_00548628_aktualni"
    heat = registry.async_get_entity_id("sensor", DOMAIN, unique_id)
    assert hass.states.get(heat).state == "149.0"
    assert hass.states.get(heat).attributes.get("device_class") is None
    assert hass.states.get(heat).attributes["unit_of_measurement"] == "dilky"
    for value, expected in [("0", "0.0"), ("unavailable", "unavailable"), ("1", "1.0")]:
        set_heat(hass, value)
        await hass.async_block_till_done()
        assert hass.states.get(heat).state == expected
    await hass.config_entries.options.async_init(
        entry.entry_id, data={CONF_COLD: "sensor.cold_radio", CONF_HEAT: []}
    )
    await hass.async_block_till_done()
    assert registry.async_get_entity_id("sensor", DOMAIN, unique_id) is None
    assert registry.async_get(cold).unique_id == water_unique_id
    assert hass.states.get(cold).state == "12.345"
    assert hass.states.get("sensor.eitn_00548628_aktualni").state == "1"


@pytest.mark.parametrize(
    ("unit", "state_class"), [("kWh", "total_increasing"), ("°C", "measurement"), ("dilky", None)]
)
async def test_wrong_heat_source_rejected(hass, unit, state_class):
    entry, _, _ = await create_entry(hass, hot=False)
    set_heat(hass, "7", unit, state_class)
    result = await hass.config_entries.options.async_init(
        entry.entry_id,
        data={CONF_COLD: "sensor.cold_radio", CONF_HEAT: ["sensor.eitn_00548628_aktualni"]},
    )
    assert result["errors"][CONF_HEAT] == "invalid_heat_source"


async def test_duplicate_and_circular_heat_rejected(hass):
    entry, _, _ = await create_entry(hass, hot=False)
    set_heat(hass, "7")
    source = "sensor.eitn_00548628_aktualni"
    result = await hass.config_entries.options.async_init(
        entry.entry_id, data={CONF_COLD: "sensor.cold_radio", CONF_HEAT: [source, source]}
    )
    assert result["errors"][CONF_HEAT] == "duplicate_heat_source"
    await hass.config_entries.options.async_init(
        entry.entry_id, data={CONF_COLD: "sensor.cold_radio", CONF_HEAT: [source]}
    )
    await hass.async_block_till_done()
    heat = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_heat_{source}"
    )
    result = await hass.config_entries.options.async_init(
        entry.entry_id, data={CONF_COLD: "sensor.cold_radio", CONF_HEAT: [heat]}
    )
    assert result["errors"][CONF_HEAT] == "circular_source"
