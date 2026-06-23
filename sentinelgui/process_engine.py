"""Module 2 — Process Data Engine.

Converts a raw serial/simulator frame into an engineering-unit ``Reading``. The Arduino
firmware already emits values in engineering units (°C, L/min, bar) per
contracts/serial-protocol.md, so conversion is validation + pass-through with an optional
per-sensor scale/offset hook for future calibration. Pure standard library.
"""

from __future__ import annotations

import math
from typing import Optional

from .models import Reading

# Optional linear calibration per sensor: engineering = raw * scale + offset.
# Defaults are identity because firmware sends engineering units already.
CALIBRATION = {
    "temperature": (1.0, 0.0),
    "flow_rate": (1.0, 0.0),
    "pressure": (1.0, 0.0),
}


def to_engineering(raw: dict[str, float]) -> Optional[dict[str, float]]:
    """Apply calibration to a raw frame. Returns ``None`` if any result is non-finite."""
    out = {}
    for sensor, value in raw.items():
        scale, offset = CALIBRATION.get(sensor, (1.0, 0.0))
        converted = value * scale + offset
        if not math.isfinite(converted):
            return None
        out[sensor] = converted
    return out


def build_reading(raw: dict[str, float], seq: int, source: str, now: str) -> Optional[Reading]:
    """Build a ``Reading`` from a raw frame, or ``None`` if conversion fails (FR-004)."""
    values = to_engineering(raw)
    if values is None:
        return None
    return Reading(timestamp=now, values=values, seq=seq, source=source, raw=dict(raw))
