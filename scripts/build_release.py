"""Build deterministic source and manual-install release archives."""

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "vodomer_esp32_c3_cc1101"


def build() -> None:
    """Exclude credentials, firmware build output, logs, and local environments."""
    version = json.loads((ROOT / "custom_components" / DOMAIN / "manifest.json").read_text())[
        "version"
    ]
    target = ROOT / "dist"
    target.mkdir(exist_ok=True)
    excludes = {".git", "dist", "__pycache__", ".pytest_cache", ".ruff_cache", ".esphome", ".venv"}
    files = [
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and not (set(p.relative_to(ROOT).parts) & excludes)
        and p.name != "secrets.yaml"
        and p.suffix not in {".log", ".bin", ".elf", ".pyc"}
    ]
    archives = {}
    for name, selected, prefix in [
        (f"Vodomer_esp32_C3_CC1101-{version}.zip", files, "Vodomer_esp32_C3_CC1101/"),
        (
            f"vodomer-ha-{version}.zip",
            [p for p in files if "custom_components" in p.relative_to(ROOT).parts],
            "",
        ),
    ]:
        archive = target / name
        with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
            for path in sorted(selected):
                info = ZipInfo(
                    prefix + path.relative_to(ROOT).as_posix(), date_time=(2026, 10, 3, 0, 0, 0)
                )
                info.compress_type = ZIP_DEFLATED
                info.external_attr = (0o755 if path.suffix == ".sh" else 0o644) << 16
                zip_file.writestr(info, path.read_bytes())
        archives[name] = hashlib.sha256(archive.read_bytes()).hexdigest()
        print(f"{archive.name}: {archive.stat().st_size} bytes")
    (target / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in archives.items())
    )


if __name__ == "__main__":
    build()
