"""Module 4 — ReAct Agent (Observe → Reason → Act).

Ties the alarm manager, fault engine, and rolling window into a single per-reading step
that yields an ``AgentResult`` (new/cleared alarms, the current diagnosis, and per-stage
mimic health). The optional AI enrichment runs on a worker thread and never blocks the
step loop (Constitution v3.0.0, Principle IV). Pure standard library; the bridge is
imported lazily so the core stays testable without network or the GUI stack.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Callable, Optional

from . import fault_engine
from .models import PROCESS_STAGES, SENSOR_STAGE, FaultDiagnosis
from .reading_window import ReadingWindow

_RANK = {"normal": 0, "warning": 1, "critical": 2}
# Faults whose blame belongs to the Pump stage of the mimic.
_PUMP_FAULTS = {"pump_failure", "cavitation"}


@dataclass
class AgentResult:
    reading: object
    new_alarms: list = field(default_factory=list)
    cleared_alarms: list = field(default_factory=list)
    diagnosis: Optional[FaultDiagnosis] = None
    stage_health: dict = field(default_factory=dict)


class ReActAgent:
    """Observe the reading, reason about alarms + faults, act by producing a result."""

    def __init__(self, alarms, window: ReadingWindow, bands=None, bridge=None):
        self.alarms = alarms
        self.window = window
        self.bands = bands
        self.bridge = bridge

    def step(self, reading) -> AgentResult:
        # Observe → Reason: evaluate zones/alarms for this reading.
        changes = self.alarms.evaluate(reading)
        new_alarms = [a for a in changes if a.state == "active"]
        cleared = [a for a in changes if a.state == "cleared"]

        # Reason: diagnose only when something is actively in alarm.
        diagnosis = None
        if self.alarms.active:
            diagnosis = fault_engine.classify(reading, self.window, self.alarms.active)

        # Act: compute mimic stage health for highlighting.
        stage_health = self._stage_health(diagnosis)
        return AgentResult(
            reading=reading,
            new_alarms=new_alarms,
            cleared_alarms=cleared,
            diagnosis=diagnosis,
            stage_health=stage_health,
        )

    def _stage_health(self, diagnosis) -> dict:
        health = {stage: "normal" for stage in PROCESS_STAGES}
        for alarm in self.alarms.active:
            stage = SENSOR_STAGE.get(alarm.sensor)
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
