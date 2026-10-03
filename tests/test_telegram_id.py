"""Check BCD address endianness and rejection of unsupported frames."""

import pytest

from scripts.telegram_id import extract_id


def test_address():
    # Minimal synthetic link header: L,C,M[2],A[4-byte BCD + version + medium].
    assert extract_id("09440106420784040307") == "04840742"
    assert extract_id("0x09 44 01 06 89 69 84 04 03 07") == "04846989"


@pytest.mark.parametrize(
    "frame",
    ["", "ABC", "XX", "0944010674428404", "0B440106FFFF744284040307", "094401067A4284040307"],
)
def test_invalid(frame):
    with pytest.raises(ValueError):
        extract_id(frame)
