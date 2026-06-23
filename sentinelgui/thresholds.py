"""Two-band (Warning/Critical) threshold model.

Loads and validates the nested bands from ``gui_config.json`` and classifies a value into
``normal`` / ``warning`` / ``critical``. Zone evaluation reuses SentinelCLI's tested,
inclusive-bound ``check_reading`` once per band so the GUI and CLI agree on "in range"
(see contracts/sentinelcli-bridge.md §1). Pure standard library + SentinelCLI import.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import project  # SentinelCLI — reused, never modified


@dataclass
class ThresholdBand:
    """Two explicit nested bands for one sensor: warning ⊂ critical."""

    critical: dict[str, float]  # {"min": float, "max": float}
    warning: dict[str, float]  # {"min": float, "max": float}


_DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "gui_config.json")


def _validate_band(sensor: str, band: ThresholdBand) -> None:
    c, w = band.critical, band.warning
    for label, rng in (("critical", c), ("warning", w)):
        if "min" not in rng or "max" not in rng:
            raise ValueError(
                f"Threshold for '{sensor}' {label} band must include 'min' and 'max'."
            )
    # Invariant: critical.min <= warning.min <= warning.max <= critical.max
    if not (c["min"] <= w["min"] <= w["max"] <= c["max"]):
        raise ValueError(
            f"Threshold for '{sensor}' must satisfy "
            f"critical.min <= warning.min <= warning.max <= critical.max "
            f"(got critical={c}, warning={w})."
        )


def load_thresholds(path: str | None = None) -> dict[str, ThresholdBand]:
    """Load and validate the two-band thresholds from *path* (or the bundled default).

    Raises ``ValueError`` with a human-readable message on a bad config (Principle V).
    """
    config_path = path or _DEFAULT_CONFIG_PATH
    try:
        with open(config_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise FileNotFoundError(f"GUI config not found: {config_path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"GUI config is not valid JSON: {exc}")

    raw_thresholds = data.get("thresholds", data)
    if not isinstance(raw_thresholds, dict):
        raise ValueError("GUI config 'thresholds' must be an object of sensors.")

    bands: dict[str, ThresholdBand] = {}
    for sensor, spec in raw_thresholds.items():
        if not isinstance(spec, dict) or "critical" not in spec or "warning" not in spec:
            raise ValueError(
                f"Threshold for '{sensor}' must define 'critical' and 'warning' bands."
            )
        band = ThresholdBand(
            critical={k: float(v) for k, v in spec["critical"].items()},
            warning={k: float(v) for k, v in spec["warning"].items()},
        )
        _validate_band(sensor, band)
        bands[sensor] = band
    return bands


def zone_of(sensor: str, value: float, bands: dict[str, ThresholdBand]) -> str:
    """Return ``"normal"`` | ``"warning"`` | ``"critical"`` for *value*.

    Reuses SentinelCLI ``check_reading`` per band: a breach of the critical band is
    critical; else a breach of the warning band is warning; else normal. Bounds are
    inclusive (a value equal to a bound is in-range), matching SentinelCLI.
    """
    band = bands.get(sensor)
    if band is None:
        return "normal"
    reading = {"timestamp": None, "row": 0, "values": {sensor: value}}
    if project.check_reading(reading, {sensor: band.critical}):
        return "critical"
    if project.check_reading(reading, {sensor: band.warning}):
        return "warning"
    return "normal"
