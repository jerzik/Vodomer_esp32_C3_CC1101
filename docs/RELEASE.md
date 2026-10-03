# Založení repozitáře a release 1.0.0

Požadovaný cíl: **veřejný** repozitář účtu `jerzik` s přesným názvem
`Vodomer_esp32_C3_CC1101`. HACS používá veřejné repozitáře.

## Přes GitHub web a následně git

1. V účtu `jerzik` založte prázdný veřejný repozitář s tímto názvem.
2. Popis: `Studená a teplá voda v Home Assistantu přes ESP32-C3 Super Mini a CC1101. ESPHome firmware a HACS integrace.`
3. Témata: `home-assistant`, `hacs`, `esphome`, `esp32-c3`, `cc1101`, `water-meter`, `wireless-mbus`.
4. Nahrajte tento projekt včetně složek `.github/`, `custom_components/`, `docs/`,
   `esphome/`, `home_assistant/`, `scripts/` a `tests/`. **Nenahrávejte secrets.yaml,
   logy ani konfigurace s vlastními hesly.** Release builder je z balíčku vylučuje.
5. Po prvním push nechte dokončit workflow **Validate**. Chyby HACS nebo hassfest
   opravte před zveřejněním. Místní runtime testy nenahrazují tyto vzdálené kontroly.
6. Vytvořte tag **`v1.0.0`** na ověřeném commitu a pushněte jej.
   Workflow **Release** vytvoří veřejné vydání se dvěma ZIP soubory a kontrolními součty.
7. Zkontrolujte hotový release a instalaci vlastní URL v HACS.

## GitHub CLI

Máte-li lokálně GitHub CLI (`gh`) přihlášené jako `jerzik`, ve složce projektu spusťte
`bash scripts/publish.sh`. Skript nejprve zkontroluje účet a existující remote,
vytvoří repozitář, pushne zdrojové soubory a nastaví témata. Poté skončí s postupem
pro spuštění release až po zeleném Validate. Nic netlačí s `--force`.

Ruční tag po úspěšném Validate:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Samotný tag nestačí pro číslované verze HACS: workflow musí dokončit **GitHub Release**.
Vlastní repozitář je možné přidat ručně do HACS bez přijetí do výchozího katalogu.
