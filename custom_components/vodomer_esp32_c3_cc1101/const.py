"""Constants for the ESPHome water meter companion integration."""

DOMAIN = "vodomer_esp32_c3_cc1101"
NAME = "Vodoměr ESP32-C3 + CC1101"
CONF_COLD = "cold_source"
CONF_HOT = "hot_source"
CHANNELS = ((CONF_COLD, "cold", "Studená voda celkem"), (CONF_HOT, "hot", "Teplá voda celkem"))
UNIT_FACTORS = {"m³": 1.0, "m3": 1.0, "L": 0.001, "l": 0.001}
