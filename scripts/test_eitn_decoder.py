"""Compile the actual YAML decoder against owned telegram fixtures and invalid frames."""

import json
import subprocess
import tempfile
from pathlib import Path

import yaml

rooms = ["obyvak", "kuchyn", "loznice", "pokoj"]
ids = ["00548628", "00548629", "00548645", "00547681"]

root = Path(__file__).resolve().parents[1]


class Loader(yaml.SafeLoader):
    pass


Loader.add_constructor("!secret", lambda loader, node: loader.construct_scalar(node))
config = yaml.load((root / "esphome/vodomer-c3-topeni.yaml").read_text(), Loader=Loader)
core = config["wmbus_radio"]["on_frame"][0]["then"][0]["lambda"]
for key, value in config["substitutions"].items():
    core = core.replace("${" + key + "}", value)
src = """#include <string>
#include <vector>
#include <cstdint>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <cassert>
#define id(x) x
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
struct Sensor {float state=NAN; bool has_state(){return !std::isnan(state);} void publish_state(float x){state=x;}};
struct Text {std::string state;void publish_state(std::string x){state=x;}};
struct Time {bool is_valid(){return true;} std::string strftime(const char*){return "test";}};
struct Clock {Time now(){return {};}} ha_time;
uint32_t millis(){return 12345;}
struct Frame {std::string hex;bool handled=false;std::string as_hex(){return hex;}int rssi(){return -56;}void mark_as_handled(){handled=true;}};
"""
for r in rooms:
    src += (
        "Sensor "
        + ",".join(
            f"{r}_{k}"
            for k in ["aktualni", "minuly", "teplota", "teplota_archiv", "rssi", "pocet", "stari"]
        )
        + ";\n"
    )
    src += "Text " + ",".join(f"{r}_{k}" for k in ["prijem", "datum", "archiv_datum"]) + ";\n"
    src += f"uint32_t {r}_posledni_ms=0;\n"
src += "void decode(Frame *frame){\n" + core + "}\nint main(){\n"

frames = list(json.loads((root / "tests/fixtures/eitn40.json").read_text()).values())
# A valid frame from an unselected ID must be ignored.
frames.append(frames[0][:8] + "99999999" + frames[0][16:])
n = 0
targets = 0
for h in frames:
    b = bytes.fromhex(h)
    mid = b[4:8][::-1].hex()
    own = mid in ids
    targets += own
    n += 1
    src += (
        '{Frame f{"'
        + h
        + '"}; decode(&f);assert(f.handled == '
        + ("true" if own else "false")
        + ");}\n"
    )
for r, values in zip(
    rooms,
    [(149, 114, 21.75, 21.81), (0, 14, 23.31, 23.31), (7, 1, 20, 19.94), (250, 184, 22.25, 22.25)],
):
    for k, val in zip(["aktualni", "minuly", "teplota", "teplota_archiv"], values):
        src += f"assert(std::fabs({r}_{k}.state - {val}) < 0.005);\n"
    src += f'assert({r}_datum.state == "2026-10-06");\n'
# Every truncation, changed record header, encrypted config must be rejected.
h = next(h for h in frames if h[8:16] == "28865400")
for length in range(len(h)):
    src += '{Frame f{"' + h[:length] + '"};decode(&f);assert(!f.handled);}\n'
for offset in [0, 2, 8, 9, 10, 13, 14, 15, 19, 23, 27, 31, 35, 40, 45, 50, 55, 58, 63, 68]:
    b = bytearray.fromhex(h)
    b[offset] ^= 0x01
    src += '{Frame f{"' + b.hex() + '"};decode(&f);assert(!f.handled);}\n'
src += f'std::cout << "PASS: {n} frames (4 captured + 1 synthetic), {targets} own frames; four rooms and temperatures; truncations and changed layouts rejected\\n";}}'

work = Path(tempfile.mkdtemp(prefix="eitn-test-"))
(work / "decoder-test.cpp").write_text(src)
subprocess.run(
    [
        "g++",
        "-std=c++17",
        "-Wall",
        "-Wextra",
        "-Werror",
        str(work / "decoder-test.cpp"),
        "-o",
        str(work / "decoder-test"),
    ],
    check=True,
)
subprocess.run([str(work / "decoder-test")], check=True)
