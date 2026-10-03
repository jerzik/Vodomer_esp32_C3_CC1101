"""Event-driven cumulative sensors sourced from native ESPHome entities."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CHANNELS, DOMAIN, NAME
from .reading import volume_m3


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create configured channels; drop the old hot channel if removed."""
    sources = entry.options or entry.data
    registry = er.async_get(hass)
    entities = []
    for config_key, channel, name in CHANNELS:
        if source := sources.get(config_key):
            entities.append(WaterMeterSensor(entry, source, channel, name))
        else:
            old_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{channel}")
            if old_id:
                registry.async_remove(old_id)
    async_add_entities(entities)


class WaterMeterSensor(SensorEntity):
    """Copy valid totals; propagate unavailable sources instead of zero."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "m³"
    _attr_suggested_display_precision = 3

    def __init__(self, entry: ConfigEntry, source: str, channel: str, name: str) -> None:
        self._source = source
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{channel}"
        self._attr_icon = "mdi:water" if channel == "cold" else "mdi:water-thermometer"
        self._attr_available = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=NAME,
            manufacturer="DIY",
            model="ESP32-C3 Super Mini + CC1101 / Wireless M-Bus",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe before reading the initial state to avoid a missed change."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(self.hass, [self._source], self._source_changed)
        )
        self._read_source()

    @callback
    def _source_changed(self, event: Event) -> None:
        """Refresh when the source changes, disappears, or becomes available."""
        self._read_source()
        self.async_write_ha_state()

    @callback
    def _read_source(self) -> None:
        state = self.hass.states.get(self._source)
        value = None
        if (
            state
            and state.attributes.get("device_class") == "water"
            and state.attributes.get("state_class") == "total_increasing"
        ):
            value = volume_m3(state.state, state.attributes.get("unit_of_measurement"))
        self._attr_available = value is not None
        self._attr_native_value = value
        self._attr_extra_state_attributes = {"source_entity": self._source}
