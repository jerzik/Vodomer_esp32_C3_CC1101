# Vydání nové verze

1. Aktualizujte manifest.json, CHANGELOG a docs/RELEASE_NOTES_<verze>.md.
2. Ověřte testy HA, C++ dekodér, formátování, konfigurace ESPHome a nepřítomnost secrets.
3. Pushněte změny do main. Validate spustí testy, HACS, hassfest a kompilaci vodní i rozšířené konfigurace.
4. Teprve po úspěchu všech kontrol spustí workflow Release publikaci nové verze podle manifestu. Checkout i tag cílí přesně na ověřený head_sha. Existující release se nepřepisuje.
5. Ověřte novou stránku release, tři přílohy a tag. HACS verzi nabízí jako aktualizaci vlastního repozitáře; nezařazuje projekt automaticky do výchozího katalogu.

Distribuují se konfigurace a zdroje, nikoli testovací binárky s cizími Wi-Fi údaji. HACS neflashuje ESP32.
