"""Module 8 — Alarm Manager.

Evaluates each reading into normal/warning/critical zones (reusing ``thresholds.zone_of``),
applies debounce/hysteresis so alarms don't flicker on rapid valve toggling, and tracks the
active alarms plus a session history. Pure standard library + SentinelCLI threshold reuse.
"""

from __future__ import annotations

from typing import Optional

from .models import Alarm
from .thresholds import ThresholdBand, zone_of

_SEVERITY_RANK = {"normal": 0, "warning": 1, "critical": 2}


class AlarmManager:
    """Stateful zone evaluator with debounce and active/history tracking."""

    def __init__(self, bands: dict[str, ThresholdBand], debounce_samples: int = 2):
        self.bands = bands
        self.debounce_samples = max(1, debounce_samples)
        self._confirmed: dict[str, str] = {}  # sensor -> confirmed zone
        self._candidate: dict[str, tuple[str, int]] = {}  # sensor -> (zone, count)
        self._active: dict[str, Alarm] = {}  # sensor -> active Alarm
        self._history: list[Alarm] = []

    @property
    def active(self) -> list[Alarm]:
        return list(self._active.values())

    @property
    def history(self) -> list[Alarm]:
        return list(self._history)

    def evaluate(self, reading) -> list[Alarm]:
        """Return the alarms whose state changed on this reading (raised or cleared)."""
        changes: list[Alarm] = []
        for sensor, value in reading.values.items():
            if sensor not in self.bands:
                continue
            zone = zone_of(sensor, value, self.bands)
            confirmed = self._confirmed.get(sensor, "normal")
            if zone == confirmed:
                self._candidate.pop(sensor, None)
                continue
            # Debounce: the new zone must persist N consecutive samples.
            cand_zone, cand_count = self._candidate.get(sensor, (zone, 0))
            if cand_zone == zone:
                cand_count += 1
            else:
                cand_zone, cand_count = zone, 1
            self._candidate[sensor] = (cand_zone, cand_count)
            if cand_count < self.debounce_samples:
                continue
            # Confirmed transition.
            self._confirmed[sensor] = zone
            self._candidate.pop(sensor, None)
            changes.extend(self._apply_transition(sensor, value, zone, reading))
        return changes

    def _apply_transition(self, sensor, value, zone, reading) -> list[Alarm]:
        out: list[Alarm] = []
        existing = self._active.get(sensor)
        timestamp = reading.timestamp
        if zone == "normal":
            if existing is not None:
                existing.state = "cleared"
                existing.cleared_at = timestamp
                del self._active[sensor]
                out.append(existing)
            return out
        # warning or critical: clear any prior active alarm of a different severity first.
        if existing is not None and existing.severity != zone:
            existing.state = "cleared"
            existing.cleared_at = timestamp
            out.append(existing)
            del self._active[sensor]
        if sensor not in self._active:
            limit, bound = self._breached_edge(sensor, value, zone)
            alarm = Alarm(
                sensor=sensor,
                value=value,
                severity=zone,
                limit=limit,
                bound=bound,
                raised_at=timestamp,
            )
            self._active[sensor] = alarm
            self._history.append(alarm)
            out.append(alarm)
        return out

    def _breached_edge(self, sensor, value, zone) -> tuple[str, float]:
        band = self.bands[sensor]
        rng = band.critical if zone == "critical" else band.warning
        if value < rng["min"]:
            return "min", rng["min"]
        return "max", rng["max"]
