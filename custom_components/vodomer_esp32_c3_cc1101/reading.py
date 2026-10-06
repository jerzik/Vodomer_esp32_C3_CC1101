"""Validate a cumulative volume without inventing a reading on failure."""

from math import isfinite

from .const import HEAT_UNITS, UNIT_FACTORS


def heat_units(value: str, unit: str | None) -> float | None:
    """Accept dimensionless allocator readings; never convert to energy."""
    if unit not in HEAT_UNITS:
        return None
    try:
        number = float(value)
    except TypeError, ValueError:
        return None
    return number if isfinite(number) and number >= 0 else None


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
