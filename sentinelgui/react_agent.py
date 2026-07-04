"""Module 4 — ReAct Agent (Observe → Reason → Act).

Ties the alarm manager, fault engine, and rolling window into a single per-reading step
that yields an ``AgentResult`` (new/cleared alarms, the current diagnosis, per-stage
mimic health, and an optional reasoning trace for visibility). The optional AI enrichment
runs on a worker thread and never blocks the step loop (Constitution v3.0.0, Principle
IV). Pure standard library; the bridge is imported lazily so the core stays testable
without network or the GUI stack.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Callable, Optional

from . import fault_engine
from .models import PROCESS_STAGES, SENSOR_STAGE, FaultDiagnosis
from .reading_window import ReadingWindow

_RANK = {"normal": 0, "warning": 1, "critical": 2}
_CLEARED = "cleared"
_PUMP_FAULTS = {"pump_failure", "cavitation"}


@dataclass
class AgentResult:
    reading: object
    new_alarms: list = field(default_factory=list)
    cleared_alarms: list = field(default_factory=list)
    diagnosis: Optional[FaultDiagnosis] = None
    stage_health: dict = field(default_factory=dict)
    trace: list = field(default_factory=list)


class ReActAgent:
    """Observe the reading, reason about alarms + faults, act by producing a result."""

    def __init__(self, alarms, window: ReadingWindow, bands=None, bridge=None,
                 stages=None, stage_sensor=None):
        self.alarms = alarms
        self.window = window
        self.bands = bands
        self.bridge = bridge
        self._last_fault: Optional[str] = None
        self._stages = stages if stages else PROCESS_STAGES
        self._stage_sensor = stage_sensor if stage_sensor else SENSOR_STAGE

    # -- trace helpers ---------------------------------------------------------

    def _short_sensor(self, key: str) -> str:
        return {"temperature": "temp", "flow_rate": "flow", "pressure": "press"}.get(key, key)

    def _zone_label(self, sensor: str, value: float) -> str:
        if self.bands is None:
            return "—"
        from .thresholds import zone_of
        return zone_of(sensor, value, self.bands)

    def _build_trace(self, reading, new_alarms, cleared, diagnosis) -> list:
        trace: list = []
        ts = getattr(reading, "timestamp", "—")

        # -- diagnosis changed without a new alarm
        diag_changed = False
        if diagnosis and diagnosis.fault != self._last_fault:
            diag_changed = True
            self._last_fault = diagnosis.fault
        elif diagnosis is None and self._last_fault is not None:
            diag_changed = True
            self._last_fault = None

        if new_alarms or (diag_changed and diagnosis is not None):
            sev = "critical" if any(a.severity == "critical" for a in new_alarms) else "warning"
            obs = []
            for s, v in reading.values.items():
                z = self._zone_label(s, v)
                obs.append(f"{self._short_sensor(s)} {v} → {z}")
            reason = ""
            if diagnosis:
                r = f"{diagnosis.fault} ({diagnosis.confidence} confidence)"
                reason = f"  Reason:  {r} — {diagnosis.explanation}"
            else:
                reason = "  Reason:  out of range, no known fault signature matched"
            names = ", ".join(f"'{a.sensor}'" for a in new_alarms) if new_alarms else ""
            names = names or (diagnosis.fault if diagnosis else "—")
            act = f"  Act:     raised {sev} alarm {names}"
            trace.append(f"{ts} [{sev}]\n  Observe: {', '.join(obs)}\n{reason}\n{act}")

        if cleared:
            for alarm in cleared:
                trace.append(f"{ts} [{_CLEARED}] — {alarm.sensor} returned to normal zone")

        return trace

    def step(self, reading) -> AgentResult:
        changes = self.alarms.evaluate(reading)
        new_alarms = [a for a in changes if a.state == "active"]
        cleared = [a for a in changes if a.state == "cleared"]

        diagnosis = None
        if self.alarms.active:
            diagnosis = fault_engine.classify(reading, self.window, self.alarms.active)

        stage_health = self._stage_health(diagnosis)
        trace = self._build_trace(reading, new_alarms, cleared, diagnosis)

        return AgentResult(
            reading=reading,
            new_alarms=new_alarms,
            cleared_alarms=cleared,
            diagnosis=diagnosis,
            stage_health=stage_health,
            trace=trace,
        )

    def _stage_health(self, diagnosis) -> dict:
        health = {stage: "normal" for stage in self._stages}
        for alarm in self.alarms.active:
            stage = self._stage_sensor.get(alarm.sensor)
            if stage and _RANK[alarm.severity] > _RANK[health[stage]]:
                health[stage] = alarm.severity
        # Attribute pump-type faults to the Pump stage as well.
        if diagnosis and diagnosis.fault in _PUMP_FAULTS and self.alarms.active:
            worst = max((a.severity for a in self.alarms.active), key=lambda s: _RANK[s])
            if _RANK[worst] > _RANK[health["Pump"]]:
                health["Pump"] = worst
        return health

    def request_ai(self, alarm, on_done: Callable[[Optional[str]], None], client=None) -> None:
        """Run AI enrichment for *alarm* on a worker thread; call ``on_done(text|None)``."""

        def worker():
            text = None
            try:
                from . import sentinelcli_bridge

                text = sentinelcli_bridge.ai_diagnose(alarm, client=client)
            except Exception:
                text = None
            on_done(text)

        threading.Thread(target=worker, name="ai-diagnose", daemon=True).start()
