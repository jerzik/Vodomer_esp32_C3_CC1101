# Změny

## 1.0.0 — 2026-10-03

- Jeden ESP32-C3 Super Mini a CC1101 přijímá dva Apator AT-WMBUS-16-2.
- Přímé propojení bez přidaných rezistorů; napájení CC1101 z 3,3 V.
- Firmware ESPHome se dvěma oddělenými celkovými stavy a diagnostikou rámců.
- Integrace Home Assistantu pro instalaci jako vlastní repozitář HACS.
- České a anglické nastavení zdrojových senzorů, teplá voda volitelná.
- Změna zdrojů přes nabídku Konfigurovat, korektní propagace nedostupnosti.
- YAML pro denní/měsíční spotřebu a ukázkový dashboard.
- Schéma, návod k identifikaci vodoměru, vlastní ikona a favicon.
- Připnutá revize externí W-MBus komponenty.

Identifikace studené vody `04840742` a funkční příjem potvrzeny uživatelem.
Teplá voda `04846989`, AES klíče a nová konfigurace obou měřidel vyžadují ověření na zařízení.
