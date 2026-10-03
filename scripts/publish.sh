#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
repo='jerzik/Vodomer_esp32_C3_CC1101'
expected_origin="https://github.com/$repo.git"
login=$(gh api user --jq .login)
if [[ "$login" != jerzik ]]; then
  echo 'Přihlaste GitHub CLI jako jerzik; jiný účet nebyl určen.' >&2
  exit 1
fi
if [[ ! -d .git ]]; then
  git init -b main
fi
if git remote get-url origin >/dev/null 2>&1; then
  origin=$(git remote get-url origin)
  if [[ "$origin" != "$expected_origin" && "$origin" != "git@github.com:$repo.git" ]]; then
    echo 'Repozitář již má jiný origin; skript jej nezměnil.' >&2
    exit 1
  fi
fi
git add README.md CHANGELOG.md LICENSE hacs.json pyproject.toml requirements-test.txt .gitignore .github custom_components docs esphome home_assistant scripts tests
if ! git diff --cached --quiet; then
  git commit -m 'Prepare water meter ESPHome firmware and HACS integration 1.0.0'
fi
if gh repo view "$repo" >/dev/null 2>&1; then
  if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$expected_origin"
  fi
  git push -u origin main
else
  # Repository creation is explicit in the original project request.
  gh repo create "$repo" --public --source . --remote origin --push --description 'Studená a teplá voda v Home Assistantu přes ESP32-C3 Super Mini a CC1101. ESPHome firmware a HACS integrace.'
fi
gh repo edit "$repo" --add-topic home-assistant --add-topic hacs --add-topic esphome --add-topic esp32-c3 --add-topic cc1101 --add-topic water-meter --add-topic wireless-mbus
echo 'Zdrojový projekt je nahraný. Nechte projít Validate, potom: git tag v1.0.0 && git push origin v1.0.0'
