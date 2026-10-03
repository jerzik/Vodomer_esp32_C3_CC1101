"""Runtime coverage of setup, updates, failures, configuration and removal."""

import pytest
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er

from custom_components.vodomer_esp32_c3_cc1101.const import CONF_COLD, CONF_HOT, DOMAIN
from custom_components.vodomer_esp32_c3_cc1101.reading import volume_m3

from .conftest import set_source


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        ("123.456", "m³", 123.456),
        ("12500", "L", 12.5),
        ("0", "m³", 0.0),
        ("unavailable", "m³", None),
        ("unknown", "m³", None),
        ("nan", "m³", None),
        ("inf", "m³", None),
        ("-1", "m³", None),
        ("1", "kWh", None),
        ("1", None, None),
    ],
)
def test_no_false_zero(value, unit, expected):
    assert volume_m3(value, unit) == expected


async def create_entry(hass, hot=True):
    set_source(hass, "sensor.cold_radio", "12.345")
    data = {CONF_COLD: "sensor.cold_radio"}
    if hot:
        set_source(hass, "sensor.hot_radio", "6789", "L")
        data[CONF_HOT] = "sensor.hot_radio"
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}, data=data
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    entry = result["result"]
    registry = er.async_get(hass)
    cold_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_cold")
    hot_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_hot")
    assert cold_id, "Actual HA platform did not load"
    return entry, cold_id, hot_id


async def test_real_setup_update_outage_recovery_and_unload(hass):
    entry, cold, hot = await create_entry(hass)
    assert hass.states.get(cold).state == "12.345"
    assert hass.states.get(hot).state == "6.789"
    assert hass.states.get(cold).attributes["state_class"] == "total_increasing"
    set_source(hass, "sensor.cold_radio", "12.355")
    await hass.async_block_till_done()
    assert hass.states.get(cold).state == "12.355"
    for invalid in ("unavailable", "unknown", "nan", "inf", "-1"):
        set_source(hass, "sensor.cold_radio", invalid)
        await hass.async_block_till_done()
        assert hass.states.get(cold).state == "unavailable"
    hass.states.async_remove("sensor.cold_radio")
    await hass.async_block_till_done()
    assert hass.states.get(cold).state == "unavailable"
    set_source(hass, "sensor.cold_radio", "12.365")
    await hass.async_block_till_done()
    assert hass.states.get(cold).state == "12.365"
    assert await hass.config_entries.async_unload(entry.entry_id)
    set_source(hass, "sensor.cold_radio", "12.375")
    await hass.async_block_till_done()
    assert hass.states.get(cold).state == "unavailable"


async def test_optional_hot_added_and_removed_in_options(hass):
    entry, cold, hot = await create_entry(hass, hot=False)
    assert hot is None
    set_source(hass, "sensor.hot_radio", "123.456")
    result = await hass.config_entries.options.async_init(
        entry.entry_id, data={CONF_COLD: "sensor.cold_radio", CONF_HOT: "sensor.hot_radio"}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    hot = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_hot")
    assert hass.states.get(hot).state == "123.456"
    result = await hass.config_entries.options.async_init(
        entry.entry_id, data={CONF_COLD: "sensor.cold_radio"}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_hot") is None
    assert hass.states.get(cold).state == "12.345"


async def test_duplicate_and_circular_sources_rejected(hass):
    _, cold, _ = await create_entry(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}, data={CONF_COLD: "sensor.cold_radio"}
    )
    assert result["type"] == FlowResultType.ABORT
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}, data={CONF_COLD: cold}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"][CONF_COLD] == "circular_source"
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
        data={CONF_COLD: "sensor.cold_radio", CONF_HOT: "sensor.cold_radio"},
    )
    assert result["errors"]["base"] == "same_source"


async def test_unknown_source_allowed_without_inventing_initial_value(hass):
    set_source(hass, "sensor.cold_radio", "unknown")
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}, data={CONF_COLD: "sensor.cold_radio"}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    entry = result["result"]
    cold = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_cold")
    assert hass.states.get(cold).state == "unavailable"


async def test_invalid_source_rejected(hass):
    hass.states.async_set(
        "sensor.power", "100", {"device_class": "power", "unit_of_measurement": "W"}
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}, data={CONF_COLD: "sensor.power"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"][CONF_COLD] == "invalid_source"
