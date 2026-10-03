"""Validate a cumulative volume without inventing a reading on failure."""

from math import isfinite

from .const import UNIT_FACTORS


def volume_m3(value: str, unit: str | None) -> float | None:
    """Convert supported source units; reject missing and invalid totals."""
    if unit not in UNIT_FACTORS:
        return None
    try:
        number = float(value)
    except TypeError, ValueError:
        return None
    if not isfinite(number) or number < 0:
        return None
    return number * UNIT_FACTORS[unit]
