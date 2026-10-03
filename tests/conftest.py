"""Exercise real Home Assistant without touching the user's installation."""

import asyncio
from pathlib import Path

import pytest_asyncio
from homeassistant import config_entries, loader
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry,
    category_registry,
    device_registry,
    entity_registry,
    floor_registry,
    issue_registry,
    label_registry,
)
from homeassistant.setup import async_setup_component


@pytest_asyncio.fixture
async def hass(tmp_path):
    """Start isolated HA infrastructure with the actual custom component."""
    (tmp_path / "custom_components").symlink_to(
        Path(__file__).resolve().parents[1] / "custom_components", target_is_directory=True
    )
    instance = HomeAssistant(str(tmp_path))
    instance.config.skip_pip = True
    instance.config_entries = config_entries.ConfigEntries(instance, {})
    loader.async_setup(instance)
    await instance.config_entries.async_initialize()
    device_registry.async_setup(instance)
    await asyncio.gather(
        entity_registry.async_load(instance),
        device_registry.async_load(instance),
        area_registry.async_load(instance),
        floor_registry.async_load(instance),
        label_registry.async_load(instance),
        issue_registry.async_load(instance),
        category_registry.async_load(instance),
    )
    assert await async_setup_component(instance, "sensor", {})
    yield instance
    for entry in instance.config_entries.async_entries():
        await instance.config_entries.async_unload(entry.entry_id)
    await instance.async_block_till_done()
    await instance.async_stop(force=True)


def set_source(hass, entity_id, value, unit="m³"):
    """Publish a realistic native ESPHome volume sensor state."""
    hass.states.async_set(
        entity_id,
        value,
        {
            "unit_of_measurement": unit,
            "device_class": "water",
            "state_class": "total_increasing",
        },
    )
