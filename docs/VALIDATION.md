# Ověření verze 1.1.0

Kontroly 6. 10. 2026.

- Home Assistant 2026.9.4 / Python 3.14.7: **32 testů prošlo**, včetně přidání/odebrání topení, ročního resetu, nedostupnosti a zachování vodních unique_id.
- C++ dekodér z výsledného YAML: g++ -std=c++17 -Wall -Wextra -Werror, čtyři vlastní zachycené telegramy, cizí syntetické ID, všechny zkrácené délky a změněné hlavičky. Prošlo.
- Původní pracovní replay před publikací: 134 zpráv, 12 vlastních; okolní měřidla se ignorují. Ve veřejných testech jsou jen čtyři vlastní telegramy.
- Ruff a formátování: prošly.
- Kompletní rozšířený YAML dříve validován v ESPHome 2026.9.1 a úspěšně přeložen/nahrán uživatelem; provozní log potvrzuje oba vodoměry a tři indikátory. Pokoj byl potvrzen předchozím logem a replay testem, nikoli novým krátkým provozním výpisem.
- Release workflow zveřejní 1.1.0 až po úspěchu Validate na stejném commitu: testy, HACS, hassfest a plná kompilace vodní i rozšířené konfigurace. Výsledky jsou dostupné v GitHub Actions.
- Teploty jsou průměry okolí (VIF 0x65 + Average 0x12), registr 0/1. Délka průměrovacího období není potvrzená. Aktuální teplota radiátoru, podrobný měsíční profil a procenta baterie se nevytvářejí.
- Skutečné kliknutí na aktualizaci HACS a vizuální vykreslení karty v uživatelově HA nebylo vzdáleně provedeno.

## Historický záznam 1.0.0
Následující stav platí pro 3. 10., nikoli pro již ověřené logy 6. 10. 2026.

# Ověření verze 1.0.0

Kontroly provedené **3. 10. 2026** v odděleném pracovním prostředí.
Žádná změna nebyla nahraná do uživatelova Home Assistantu ani ESP32.

| Kontrola | Prostředí / výsledek |
|---|---|
| Testy integrace | Home Assistant 2026.9.4, Python 3.14.7: **22 passed** |
| Statická kontrola | Ruff 0.16.10: prošla |
| Formátování | Ruff format: prošlo |
| ESPHome konfigurace obou měřidel | ESPHome 2026.9.1: validní |
| ESPHome diagnostická konfigurace | ESPHome 2026.9.1: validní |
| Kompilace C3 firmware | ESP-IDF 5.5.5: **Successfully compiled program**, místně i na GitHub runneru |
| Paměť | RAM 109 202 B / 321 296 B (34,0 %); aplikace 1 165 166 B / 1 835 008 B (63,5 %) |
| Schéma | Vizuální kontrola všech 7 propojení, 3,3 V a nezapojeného GDO2 |
| Ikony | PNG 256/512 px s alfa kanálem, tmavá varianta; ICO 16–256 px |
| HACS a hassfest | **Obě kontroly prošly na GitHub Actions** |
| Instalace přes HACS | Projekt se distribuuje jako vlastní veřejný repozitář HACS; instalaci v uživatelově HA je třeba ověřit |

Testy používají skutečný runtime HA, načtenou integraci, konfigurační flow,
registry zařízení a entit a události změn zdrojových senzorů. Pokrývají vytvoření
obou kanálů, převod litrů, nedostupnost/unknown/NaN/záporný stav, odstranění a
obnovení zdroje, unload, přidání i odebrání teplé vody přes options, duplicitní
konfiguraci, kruhový zdroj, neplatný senzor a BCD pořadí bajtů identifikátoru.

Kompilace používá veřejné **testovací hodnoty** ze secrets.example.yaml. Výsledná
binárka není určena pro instalaci: před skutečným nahráním je nutné zkompilovat
vlastní Wi-Fi, OTA a API údaje i správné klíče měřidel. Do release proto patří YAML,
nikoli testovací firmware BIN.

V tomto pracovním prostředí psutil neviděl vlastní proces v /proc při přípravě
ESP-IDF (`NoSuchProcess`). Pro místní kontrolu byl pouze v prostředí sestavení
ošetřen výpadek hledání PID použitím již dokumentované náhradní cesty
`os.getppid()`. Kód ESPHome, dekodér a soubory projektu tím nebyly změněny.
Tato úprava není součástí repozitáře ani návodu pro uživatelův HAOS.
Následná kompilace stejného firmware na GitHub runneru prošla bez této úpravy.

Externí W-MBus komponenta při konfiguraci vydává varování k chybějícímu
`synchronous=`. Sestavení tím není zastaveno; jde o varování upstream komponenty.
Testy HA mají jedno upstream varování aiohttp, bez selhání testů.

## Co stále vyžaduje ověření na zařízení

- Příjem a dekódování obou měřidel pomocí nové dvoukanálové konfigurace.
- Potvrzení rádiového ID teplé vody; `04846989` je zatím kandidát.
- Potvrzení AES klíčů; klíč z 32 nul zde není ověřený pro žádný vlastní modul.
- Shoda stavů a změn po odběru s mechanickými počítadly.
- Skutečná instalace zveřejněné verze přes HACS do uživatelova HA.

Uživatel potvrdil funkční přijímač s přímým propojením ESP32-C3 a CC1101 bez
přidaných odporů a vlastní studený modul `04840742`. To není důkaz, že nová
dvoukanálová konfigurace již byla nahraná nebo že jsou oba AES klíče správné.

## GitHub Actions

[Úspěšný běh všech čtyř kontrol](https://github.com/jerzik/Vodomer_esp32_C3_CC1101/actions/runs/37138414958) ověřil kód na commitu `14fa86ac317581d88c06921248c033b2ae8c304f`. Následující změny se týkají pouze README, tohoto záznamu ověření a poznámek k vydání; kód integrace a konfigurace firmware zůstávají shodné.
