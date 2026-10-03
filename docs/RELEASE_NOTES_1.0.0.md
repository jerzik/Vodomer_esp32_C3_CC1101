# Vodoměr ESP32-C3 + CC1101 — 1.0.0

První verze projektu pro vlastní rádiový odečet studené a teplé vody do Home Assistantu.

- HACS integrace s českým i anglickým nastavením zdrojových ESPHome senzorů.
- ESPHome konfigurace pro jeden ESP32-C3 Super Mini + CC1101 a dva Apator AT-WMBUS-16-2.
- Přímé propojení bez přidaných odporů, schéma a kompletní postup identifikace měřidel.
- Samostatný YAML pro denní a měsíční spotřebu, ukázka dashboardu.
- Lokální značka integrace a favicon podle dodaného obrázku.

## Instalace

HACS → Vlastní repozitáře → `jerzik/Vodomer_esp32_C3_CC1101` → typ Integrace → stáhnout 1.0.0 → restart HA → přidat integraci.
Vyberte již funkční zdrojové senzory z nativní ESPHome integrace. Teplá voda je volitelná.
Home Assistant 2026.3.0+, HACS 2.x. Firmware se nahrává zvlášť přes ESPHome; není součástí automatické instalace HACS.

## Soubory ke stažení

- `Vodomer_esp32_C3_CC1101-1.0.0.zip`: celý projekt, dokumentace, schéma, firmware YAML, HA YAML, integrace a testy.
- `vodomer-ha-1.0.0.zip`: pouze `custom_components/` pro ruční instalaci do `/config/`.
- `SHA256SUMS`: kontrolní součty archivů.

Studená voda `04840742` je identifikovaná. Teplé ID `04846989` a nulové AES klíče zůstávají k ověření na skutečných měřidlech.
Výsledky kontrol a hranice ověření jsou v `docs/VALIDATION.md`.

## Ověření vydání

Na [GitHub Actions](https://github.com/jerzik/Vodomer_esp32_C3_CC1101/actions/runs/37138414958) prošly všechny čtyři kontroly: 22 testů integrace, HACS, hassfest a kompilace ESPHome 2026.9.1 pro ESP32-C3. Firmware nebyl nahrán do uživatelova zařízení.
