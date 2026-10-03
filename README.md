# Vodomer_esp32_C3_CC1101

<img src="docs/assets/icon.png" width="128" alt="Ikona vodoměru">

**Studená a teplá voda v Home Assistantu přes ESP32-C3 Super Mini a CC1101.**
Příjem rádiových telegramů Apator AT-WMBUS-16-2 na 868,95 MHz, firmware ESPHome,
vlastní integrace pro HACS a volitelné denní/měsíční součty.

## Co projekt instaluje

| Část | Kde se instaluje | Účel |
|---|---|---|
| `esphome/vodomer-c3.yaml` | ESPHome Device Builder → ESP32-C3 | Příjem CC1101 a dekódování dvou vodoměrů |
| `custom_components/vodomer_esp32_c3_cc1101` | HACS → integrace | Přiřazení zdrojových senzorů v českém UI, oddělené celkové stavy |
| `home_assistant/vodomer-package.yaml` | HA packages, volitelné | Denní a měsíční spotřeba pro oba vodoměry |
| `home_assistant/dashboard.yaml` | Ruční karta dashboardu | Ukázka zobrazení stavů a spotřeby |

**HACS stáhne integraci do HA. Firmware ESP32 se nahrává zvlášť přes ESPHome.**
Máte-li již funkční přijímač a dva správně dekódované senzory vody, jeho firmware
nemusíte měnit. V integraci pouze vyberte jeho původní senzory. Nativní ESPHome
integrace musí být nejdříve připojena; tato doprovodná integrace nezískává AES klíč.

## Stav a požadavky

- Home Assistant **2026.3.0 nebo novější** (lokální ikony integrací), HACS 2.x.
- Referenční firmware: ESPHome **2026.9.1**, ESP-IDF.
- ESP32-C3 Super Mini, CC1101 **pro 868 MHz**, odpovídající anténa a USB zdroj.
- Jedna deska a jedno rádio stačí pro dvě měřidla ve stejném rádiovém pásmu.
- Uživatel potvrdil funkční přímé zapojení pouze **ESP32-C3 + CC1101, bez přidaných odporů**.
- Funkční příjem rádiových zpráv a příslušnost studeného modulu `04840742` jsou potvrzené.
- **Teplá voda `04846989` zůstává kandidátem ze štítku.** V dosavadních předaných
  výpisech nebyla potvrzena. Nulové AES klíče také zatím nejsou potvrzené dekódováním.
- Podrobné výsledky softwarových kontrol jsou v [docs/VALIDATION.md](docs/VALIDATION.md).
  Nový firmware pro obě měřidla vyžaduje ověření příjmu a shody s mechanickými počítadly.

## Zapojení

![Zapojení ESP32-C3 Super Mini + CC1101](docs/assets/zapojeni-c3-cc1101.png)

| ESP32-C3 Super Mini | Signál CC1101 | Funkce |
|---|---|---|
| 3V3 | VCC | Napájení rádia **3,3 V** |
| GND | GND | Společná zem |
| GPIO3 | GDO0 | Přerušení / IRQ |
| GPIO4 | CSN / CS / SS | Výběr zařízení SPI |
| GPIO5 | SCK / SCLK | Hodiny SPI |
| GPIO6 | MOSI / SI | Data z ESP32 do rádia |
| GPIO7 | MISO / SO / GDO1 | Data z rádia do ESP32 |
| — | GDO2 | Nezapojený |

ESP32 napájejte přes USB-C. **CC1101 nikdy nepřipojujte na 5 V.** Zapojení
neobsahuje externí rezistory ani další požadované součástky. Vodiče držte krátké.
Poloha vývodů se mezi variantami CC1101 liší: řiďte se názvy signálů, nikoli číslem
pinu nebo jeho polohou v obrázku. S vodoměry není žádné kabelové spojení.

## 1. Najít a určit správné vodoměry

1. Zapište **sériová čísla rádiových modulů** na studené a teplé vodě.
   Číslo mechanického vodoměru, PID a rádiové ID se mohou lišit.
2. V ESPHome otevřete **LOGS**. Hledejte `WMBUS ... FRAME=...`, `address`,
   případně dekódované ID. Pro první hledání je připravený i
   [esphome/vodomer-c3-diagnostika.yaml](esphome/vodomer-c3-diagnostika.yaml).
3. Číslo modulu `4840742` zapisujeme jako osm číslic `04840742`; YAML vyžaduje
   `0x04840742`. Zachycené ID porovnejte se štítkem.
4. Přijímač umístěte poblíž měřidel, ideálně asi 30–50 cm od kovových trubek a krytu.
   Ve funkčním pokusu byl i přibližně 10 cm od vodoměru. RSSI pouze napovídá blízkost;
   **neprokazuje příslušnost měřidla**. Nevybírejte sousední ID podle síly signálu.
5. Vyčkejte na vysílání. Záleží na konfiguraci modulu; krátký log bez vašeho ID
   sám neznamená chybu rádia. Lze sbírat log 15–30 minut a opakovat během dne.
6. Nastavte správné ID a AES klíč. Pak **porovnejte dekódovaný stav s počítadlem**.
7. Při kontrolovaném odběru pouze studené a poté pouze teplé vody ověřte změnu
   správného počítadla. Přibližně 10 litrů odpovídá **0,010 m³**. Respektujte zpoždění
   vysílání a u míchací baterie počítejte s možností současného odběru obou vod.
8. Statistiku a přehled Energie zapněte až po ověření. Samotné přijetí telegramu
   není potvrzení správného klíče nebo správně přiřazené spotřeby.

| Kanál v této instalaci | Rádiové ID | Ověření |
|---|---|---|
| Studená voda | `04840742` | Uživatel potvrdil vlastní modul; zachycený signál −36 dBm |
| Teplá voda | `04846989` | Kandidát z dřívějšího štítku; ověřit na skutečném modulu a v logu |

Klíč `00000000000000000000000000000000` je veřejně používaný **zkušební kandidát**,
ne klíč zjištěný z vašeho zařízení. Má-li modul individuální AES-128 klíč,
vyžádejte jej od správce odečtu nebo dodavatele. Sériové číslo není klíč.
Rádiový přijímač běžným příjmem tajný individuální klíč nezíská.

### Orientační rozbor FRAME

Skript `python scripts/telegram_id.py HEX` přečte identifikátor z běžného
W-MBus linkového rámce **bez vložených blokových CRC**. Skript nedekóduje spotřebu,
neověřuje klíč a nenahrazuje CRC kontrolu přijímače. Podrobnosti a omezení vypíše
`python scripts/telegram_id.py --help`. Pro identifikaci vždy kombinujte log se štítkem.

## 2. Nahrání ESPHome firmware

1. Před změnou si uložte kopii funkční konfigurace a přihlašovací údaje.
2. V Device Builderu použijte [esphome/vodomer-c3.yaml](esphome/vodomer-c3.yaml).
   Existující název `vodomer-c3` je zachovaný. Neměňte funkční piny své desky.
3. Do místního `secrets.yaml` přidejte hodnoty podle
   [esphome/secrets.example.yaml](esphome/secrets.example.yaml). Doplňte Wi-Fi,
   OTA heslo, **vlastní** ESPHome API klíč a klíče obou vodoměrů.
   ESPHome API klíč je Base64 a liší se od 32 hexadecimálních znaků AES klíče měřidla.
4. V `substitutions` nastavte `cold_meter_id` a ověřené `hot_meter_id`.
   Teplý kandidát je v ukázce jasně označený; do Energie jej zatím nepřidávejte.
5. **Validate → Install**. První nahrání přes USB, další obvykle OTA.
   Pokud jste již měli šifrované API, ponechte jeho vlastní klíč. Při zavedení
   šifrování z původního nešifrovaného API aktualizujte připojení ESPHome v HA.
6. V HA přidejte nativní integraci **ESPHome**, IP přijímače a port **6053**.
   Případný požadavek na API klíč vyplňte hodnotou `vodomer_api_key`.
7. Vyčkejte na dekódované `Studena voda radio` a `Tepla voda radio` a porovnejte
   je s počítadly. Chybějící údaj nebude uměle nahrazen nulou.

Externí komponenta je připnutá na revizi
`381afe89f39f8a7aaaae6330f214d3b4f59785b1`. Změna revize je samostatná aktualizace
firmware, kterou nejprve ověřte. HACS tuto komponentu v ESPHome nespravuje.

## 3. Instalace doprovodné integrace přes HACS

Po zveřejnění repozitáře a release:

1. **HACS → nabídka ⋮ → Vlastní repozitáře**.
2. URL: `https://github.com/jerzik/Vodomer_esp32_C3_CC1101`; typ **Integrace**.
3. Vyhledejte **Vodoměr ESP32-C3 + CC1101**, stáhněte verzi **1.0.0** a restartujte HA.
4. **Nastavení → Zařízení a služby → Přidat integraci → Vodoměr ESP32-C3 + CC1101**.
5. Vyberte původní ESPHome senzor studené vody. Teplou vodu můžete zatím vynechat.
   Jakmile je identifikovaná a dekódovaná, přidejte její zdroj přes **Konfigurovat**.
6. Vytvoří se zařízení s oddělenými celkovými stavy. Integrace reaguje na změny
   zdrojových senzorů, používá `water` / `total_increasing` a jednotku **m³**.
   Zdroj v litrech převede na m³. Při výpadku zdroje ukáže **nedostupné**, ne nulu.

[Přidat repozitář do HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=jerzik&repository=Vodomer_esp32_C3_CC1101&category=integration)

Jde o **vlastní repozitář HACS**. Release ho automaticky nezařadí do výchozího
katalogu HACS; to vyžaduje samostatné podání a přijetí podle pravidel HACS.

### Ruční instalace

Z úplného balíčku zkopírujte složku `custom_components/vodomer_esp32_c3_cc1101`
do `/config/custom_components/`, restartujte HA a pokračujte přidáním integrace.
HACS instaluje právě tuto složku; firmware a ukázkové YAML z repozitáře kopírujte samostatně.

## 4. Denní a měsíční spotřeba + Energie

Nejjednodušší je vytvořit v **Nastavení → Zařízení a služby → Pomocníci** čtyři
pomocníky **Měřič spotřeby / Utility Meter**: studená dnes, studená měsíc, teplá
dnes a teplá měsíc. Zdroj je správný ověřený celkový stav, cyklus denní/měsíční,
vstup není rozdílový a mechanický vodoměr se periodicky nenuluje.

Pro YAML variantu:

1. [home_assistant/vodomer-package.yaml](home_assistant/vodomer-package.yaml)
   uložte do `/config/packages/vodomer.yaml`.
2. **V každém `source:` nahraďte ukázkové ID skutečným ID entity z HA.** Názvy
   se mohou lišit podle jména zařízení a předchozích instalací.
3. Pokud teplá voda není ověřená, její dva bloky zatím vynechte.
4. V `configuration.yaml` slučte s existující sekcí `homeassistant:`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Nevytvářejte druhou sekci `homeassistant:`. Pokud již používáte packages,
ponechte existující způsob načítání. Zkontrolujte konfiguraci a restartujte HA.
První den a měsíc obsahují jen období od zahájení sledování.

Do **Energie → Voda** přidejte celkové kumulativní stavy obou ověřených vodoměrů.
Každý fyzický vodoměr přidejte jen jednou; zdroj ESPHome a jeho doprovodný senzor
jsou dvě reprezentace stejného odečtu. Přidáním obou byste spotřebu započítali dvakrát.

## Ikona a favicon

Motiv vychází z obrázku dodaného uživatelem; vyčištěná varianta byla vytvořena
pomocí ImageGen. Ikony pro světlé i tmavé prostředí jsou v `brand/` uvnitř integrace.
`docs/assets/favicon.ico` obsahuje velikosti 16–256 px; přiložené jsou i PNG varianty.
Jde o favicon projektu pro případný vlastní web. **Instalace integrace nemění
globální favicon ani systémové ikony celého Home Assistantu.** Senzory používají
standardní MDI ikony vody; vlastní značka se zobrazuje u integrace.

## Řešení problémů

| Projev | Co ověřit |
|---|---|
| `real_time_clock.h: No such file` | Ponechat blok `time:` v ESPHome konfiguraci |
| `Telegram not handled by any handler` | Rádiové ID nesouhlasí nebo není nakonfigurovaný handler; samotná hláška nedokazuje špatný klíč |
| Rámce jsou, stav vody chybí | Správné vlastní ID, dekodér `apator162`, AES klíč, formát telegramu |
| Žádné rámce | Napájení 3,3 V, piny, 868MHz modul a anténa, vysílací rozvrh |
| HA API handshake selže | IP, port 6053 a shodný Base64 API klíč na obou stranách |
| V nastavení nejsou zdrojové senzory | Nativní ESPHome připojení, device_class water, state_class total_increasing, m³/L |
| Denní statistika nesedí | Shoda fyzického měřidla, skutečné entity v `source`, počátek neúplného cyklu |

## Vývoj a vydávání

Testy: `python -m pytest tests`. Referenční prostředí je uvedeno
v `requirements-test.txt`. Kontroly HACS a hassfest jsou připravené v GitHub Actions.
Skript `python scripts/build_release.py` vytvoří úplný ZIP a instalační ZIP.
Postup založení repozitáře a vydání je v [docs/RELEASE.md](docs/RELEASE.md).

## Zdroje a licence

- [ESPHome W-MBus komponenta — SzczepanLeon a spoluautoři](https://github.com/SzczepanLeon/esphome-components)
- [Referenční C3 + CC1101](https://github.com/SzczepanLeon/esphome-components/blob/381afe89f39f8a7aaaae6330f214d3b4f59785b1/ESP32-C3_SuperMini_CC1101.yaml)
- [Apator AT-WMBUS-16-2 — katalog výrobce](https://api.apator.com/uploads/oferta/woda-i-cieplo/systemy/radiowy/at-wmbus--16-2-apt-o3a-1-2/at-wmbus-16-2-catalogue.pdf)
- [Dekodér apator162 — wmbusmeters](https://wmbusmeters.org/drivers/apator162.xmq.html)
- [Nulový klíč v příkladech — nepotvrzuje vaše měřidlo](https://github.com/wmbusmeters/wmbusmeters/issues/1094)
- [HACS — pravidla integrací](https://hacs.xyz/docs/publish/integration/)
- [Home Assistant — lokální brand assets](https://developers.home-assistant.io/docs/core/integration/brand_images/)
- [Home Assistant — Utility Meter](https://www.home-assistant.io/integrations/utility_meter/)

Vlastní kód projektu: MIT. Externí dekodér a W-MBus komponenta nejsou kopírované
do tohoto repozitáře; jejich licence a autoři zůstávají u původních projektů.
