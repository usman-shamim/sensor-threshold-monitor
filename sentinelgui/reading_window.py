"""Rolling buffer of recent readings (Reading Window entity).

Backed by ``collections.deque`` so it is bounded in memory. Provides the per-sensor series
that feed trend charts and the short-term slope used by hybrid fault classification.
Pure standard library — unit-testable without the GUI stack.
"""

from __future__ import annotations

from collections import deque
from typing import Optional

from .models import Reading


class ReadingWindow:
    """A bounded, time-ordered buffer of the most recent readings."""

    def __init__(self, maxlen: int = 300):
        if maxlen < 1:
            raise ValueError("ReadingWindow maxlen must be >= 1")
        self._buf: deque[Reading] = deque(maxlen=maxlen)

    def append(self, reading: Reading) -> None:
        self._buf.append(reading)

    def __len__(self) -> int:
        return len(self._buf)

    @property
    def latest(self) -> Optional[Reading]:
        return self._buf[-1] if self._buf else None

    def series(self, sensor: str) -> list[float]:
        """Return the ordered list of values for *sensor* (missing samples skipped)."""
        out = []
        for reading in self._buf:
            if sensor in reading.values:
                out.append(reading.values[sensor])
        return out

    def slope(self, sensor: str, n: int = 10) -> float:
        """Return the average per-sample rate of change over the last *n* samples.

        Positive = rising, negative = falling. Returns 0.0 when fewer than two samples
        are available. Computed as ``(last - first) / (count - 1)`` over the tail window.
        """
        values = self.series(sensor)
        if len(values) < 2:
            return 0.0
        tail = values[-n:] if n > 0 else values
        if len(tail) < 2:
            return 0.0
        return (tail[-1] - tail[0]) / (len(tail) - 1)

    def variance(self, sensor: str, n: int = 10) -> float:
        """Return the sample variance over the last *n* samples (0.0 if too few)."""
        values = self.series(sensor)
        tail = values[-n:] if n > 0 else values
        if len(tail) < 2:
            return 0.0
        mean = sum(tail) / len(tail)
        return sum((v - mean) ** 2 for v in tail) / len(tail)
