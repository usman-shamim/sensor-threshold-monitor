"""Module 1b — Fault Simulator data source.

Emits the same ``{"temperature","flow_rate","pressure"}`` raw dicts at ~1 Hz through the
identical queue path as the real serial link, so every downstream module is
source-agnostic (FR-003, SC-003). Fault injection eases the relevant fields toward the
signatures in data-model.md. Pure standard library — unit-testable without hardware.
"""

from __future__ import annotations

import math
import queue
import random
import threading
from typing import Optional

# Nominal operating point (engineering units).
NOMINAL = {"temperature": 50.0, "flow_rate": 30.0, "pressure": 3.0}

# Per-fault target operating points the simulator eases toward. ``None`` for a sensor
# means "hold nominal". Cavitation additionally oscillates pressure (see _apply_dynamics).
FAULT_TARGETS = {
    "blockage": {"flow_rate": 8.0, "pressure": 4.9},        # flow down, pressure up
    "pump_failure": {"flow_rate": 1.0, "pressure": 1.1},    # flow ~0, pressure down
    "cavitation": {"pressure": 1.2},                        # low + oscillating pressure
    "fouling": {"temperature": 88.0, "flow_rate": 22.0},    # temp up slowly, flow mild down
    "thermal_runaway": {"temperature": 110.0},              # temp steep up
    "cooling_failure": {"temperature": 95.0},               # temp up, flow normal
}


class FaultSimulator:
    """A no-hardware data source with on-demand fault injection."""

    def __init__(self, out_queue: "queue.Queue" = None, tick_s: float = 1.0):
        self.out_queue = out_queue if out_queue is not None else queue.Queue()
        self.tick_s = tick_s
        self._state = dict(NOMINAL)
        self._fault: Optional[str] = None
        self._phase = 0  # tick counter, drives cavitation oscillation deterministically
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._rng = random.Random(1234)

    def inject(self, fault: str) -> None:
        """Begin easing readings toward *fault*'s signature."""
        if fault not in FAULT_TARGETS:
            raise ValueError(f"Unknown fault: {fault}")
        self._fault = fault

    def clear_fault(self) -> None:
        """Return toward nominal operation."""
        self._fault = None

    @property
    def active_fault(self) -> Optional[str]:
        return self._fault

    def _targets(self) -> dict[str, float]:
        targets = dict(NOMINAL)
        if self._fault:
            targets.update(FAULT_TARGETS[self._fault])
        return targets

    def next_frame(self) -> dict[str, float]:
        """Advance the simulation one tick and return the current raw frame."""
        self._phase += 1
        targets = self._targets()
        for sensor in NOMINAL:
            target = targets[sensor]
            # Ease 25% toward the target each tick, then add small sensor noise.
            self._state[sensor] += (target - self._state[sensor]) * 0.25
            self._state[sensor] += self._rng.uniform(-0.3, 0.3)
        if self._fault == "cavitation":
            # Superimpose a pressure oscillation to mimic cavitation instability.
            self._state["pressure"] += 0.6 * math.sin(self._phase / 2.0)
        return {sensor: round(value, 3) for sensor, value in self._state.items()}

    def start(self) -> None:
        """Spawn a background thread emitting a frame onto the queue every ``tick_s``."""
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="simulator", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            self.out_queue.put(self.next_frame())
            self._stop.wait(self.tick_s)

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
