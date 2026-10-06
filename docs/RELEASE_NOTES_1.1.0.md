# Voda a topení ESP32-C3 + CC1101 — 1.1.0

Jeden přijímač nyní obslouží dva vodoměry a čtyři E-ITN 40. Původní HACS konfigurace vody zůstává kompatibilní.

- Celý rozšířený ESPHome YAML, připnutá W-MBus komponenta a 40 nativních entit topení.
- Aktuální/minulý roční náměr, průměrné teploty okolí, data a diagnostika příjmu.
- HACS UI pro volitelné pomocné roční náměry topení.
- Nativní dashboard bez dalších frontend doplňků.
- Fotografie všech čtyř indikátorů, postup identifikace a přehled entit.

## Aktualizace
HACS → tento vlastní repozitář → 1.1.0 → restart Home Assistantu. Volitelné roční náměry přidejte v konfiguraci integrace výběrem zdrojových ESPHome senzorů `_aktualni`.

**HACS neaktualizuje firmware ESP32 ani nevkládá kartu.** Rozšířený YAML je v `esphome/vodomer-c3-topeni.yaml`; karta v `home_assistant/dashboard-topeni.yaml`. Postup a zachování existujících vodních entit: `docs/TOPENI.md`.

Teploty jsou **průměry okolí**, ne okamžité teploty radiátoru. Délka průměrovacího období a detailní měsíční historie nejsou ověřené. Indikátor hlásí dílky, nikoli kWh. Podpora platí pro zachycený nešifrovaný formát APA v0F.

## Ověření
Release workflow je podmíněné úspěchem testů, HACS, hassfest a kompilace ESPHome na stejném commitu. Přesný rozsah je v `docs/VALIDATION.md`.
Uživatelův provozní log potvrzuje funkční vodu a nové dekódování tří indikátorů. Pokoj je ověřen předchozím telegramem a replay testem; instalace tohoto vydání přes HACS v konkrétní domácnosti nebyla vzdáleně provedena.

## Stažení
- `Vodomer_esp32_C3_CC1101-1.1.0.zip`: celý projekt, firmware YAML, dashboard, fotografie a dokumentace.
- `vodomer-ha-1.1.0.zip`: pouze custom_components pro ruční instalaci.
- `SHA256SUMS`: kontrolní součty.
