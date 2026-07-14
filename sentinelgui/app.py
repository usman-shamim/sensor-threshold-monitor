"""AppController — wires the data source, logic modules, and the dashboard together.

Owns the thread-safe reading queue and the Tk ``after()`` drain loop. The background data
source (serial or simulator) pushes raw frames onto the queue; the UI thread drains them
on a timer, never blocking on serial or AI (Constitution v3.0.0, Principle IV; research R3).

This module imports the GUI stack and is constructed only at runtime (never by the test
suite). All business logic it calls lives in the headless, unit-tested modules.
"""

from __future__ import annotations

import datetime
import queue
from typing import Optional

from . import fault_engine
from .alarm_manager import AlarmManager
from .data_logger import DataLogger
from .models import DataSource
from .process_engine import build_reading
from .react_agent import ReActAgent
from .reading_window import ReadingWindow
from .scenario import list_scenarios, load_scenario
from .shutdown_controller import ShutdownController
from .thresholds import load_thresholds, zone_of

DRAIN_INTERVAL_MS = 250


def _bands_from_dict(thresholds: dict):
    from .thresholds import ThresholdBand
    return {sensor: ThresholdBand(
        critical={k: float(v) for k, v in spec["critical"].items()},
        warning={k: float(v) for k, v in spec["warning"].items()},
    ) for sensor, spec in thresholds.items()}


def _now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


class AppController:
    """Coordinates acquisition, processing, alarms, diagnosis, logging, and the view."""

    def __init__(self, config_path: str | None = None, kiosk: bool = False,
                 scenario_id: str = "reactor"):
        self.config_path = config_path
        self.kiosk = kiosk
        self._scenarios_list = list_scenarios()
        self.scenario = load_scenario(scenario_id)  # fall through to reactor default
        if self.scenario is None:
            self.scenario = load_scenario("reactor")

        self.bands = _bands_from_dict(self.scenario.thresholds)
        self.window = ReadingWindow(maxlen=300)
        self.alarms = AlarmManager(self.bands)
        self.agent = ReActAgent(self.alarms, self.window, self.bands,
                               stages=self.scenario.stages,
                               stage_sensor=self.scenario.stage_sensor)
        self.logger = DataLogger(directory=".")
        self.shutdown = ShutdownController(source=None)
        self.queue: "queue.Queue" = queue.Queue()
        self.source = DataSource()
        self._producer = None
        self._seq = 0
        self._missed = 0
        self._view = None
        self._root = None
        self.fault_history: list = []
        self._trace: list = []
        self.started_at: str | None = None

        fault_engine.set_explanations(self.scenario.fault_explanations)
        if self.scenario.fault_tuning:
            fault_engine.set_tuning(self.scenario.fault_tuning)
        else:
            fault_engine.reset_tuning()

    # -- producer wiring -------------------------------------------------------
    def use_simulator(self):
        from .simulator import FaultSimulator

        nominal = getattr(self.scenario, "nominal", None)
        targets = getattr(self.scenario, "fault_targets", None)
        self._producer = FaultSimulator(out_queue=self.queue, tick_s=1.0,
                                        nominal=nominal, fault_targets=targets)
        self.source = DataSource(kind="simulator", status="simulating", detail="fault simulator")
        self.shutdown.source = self._producer
        return self._producer

    def use_serial(self, port: str, baud: int = 115200):
        from .acquisition import SerialDataAcquisition

        self._producer = SerialDataAcquisition(port, baud, out_queue=self.queue)
        self.source = DataSource(kind="serial", status="disconnected", detail=port)
        self.shutdown.source = self._producer
        return self._producer

    # -- lifecycle -------------------------------------------------------------
    def attach_view(self, view, root):
        self._view = view
        self._root = root

    def start(self):
        self.started_at = _now_iso()
        try:
            self._producer.start()
            if self.source.kind == "serial":
                self.source.status = "connected"
        except RuntimeError as exc:
            # Serial failed to open — fall back to the simulator (FR-002, FR-028).
            self._notify_status(f"{exc} — switching to simulator")
            self.use_simulator()
            self._producer.start()
        if self._root is not None:
            self._root.after(DRAIN_INTERVAL_MS, self._drain)

    def _drain(self):
        """Drain all queued frames, update the model, and refresh the view."""
        processed_any = False
        while True:
            try:
                raw = self.queue.get_nowait()
            except queue.Empty:
                break
            if self.shutdown.is_latched:
                continue  # skip processing — SHUTDOWN freezes everything
            processed_any = True
            self._seq += 1
            reading = build_reading(raw, self._seq, self.source.kind, _now_iso())
            if reading is None:
                continue  # malformed/non-finite — discarded (FR-004)
            self.window.append(reading)
            result = self.agent.step(reading)
            self._trace.extend(result.trace)
            self._trace = self._trace[-50:]
            if self.logger.session.state == "recording":
                self.logger.write(reading, result.new_alarms)
            for alarm in result.new_alarms:
                self._record_fault(alarm, result.diagnosis)
            if self._view is not None:
                self._view.update(self._build_state(result))

        self._update_connection(processed_any)
        if self._root is not None:
            self._root.after(DRAIN_INTERVAL_MS, self._drain)

    def _update_connection(self, processed_any: bool):
        if self.source.kind != "serial":
            return
        if processed_any:
            self._missed = 0
            self.source.status = "connected"
        else:
            self._missed += 1
            if self._missed >= 2 and self.source.status != "simulating":
                self.source.status = "disconnected"
                if self.kiosk:
                    self._auto_recover_to_simulator()

    def _auto_recover_to_simulator(self):
        self._notify_status("Serial link lost — auto-recovering into simulation mode")
        try:
            self._producer.stop()
        except Exception:
            pass
        self.use_simulator()
        self._producer.start()

    # -- helpers ---------------------------------------------------------------
    def zone(self, sensor: str, value: float) -> str:
        return zone_of(sensor, value, self.bands)

    def _record_fault(self, alarm, diagnosis):
        from .models import FaultHistoryEntry

        entry = FaultHistoryEntry(
            timestamp=alarm.raised_at,
            sensor=alarm.sensor,
            value=alarm.value,
            severity=alarm.severity,
            fault=diagnosis.fault if diagnosis else "undetermined",
            explanation=diagnosis.explanation if diagnosis else "",
            source=diagnosis.source if diagnosis else "rule",
        )
        self.fault_history.append(entry)

    def _build_state(self, result):
        return {
            "reading": result.reading,
            "zones": {
                s: self.zone(s, result.reading.values[s])
                for s in result.reading.values
            },
            "active_alarms": self.alarms.active,
            "diagnosis": result.diagnosis,
            "stage_health": result.stage_health,
            "source": self.source,
            "window": self.window,
            "recording": self.logger.session,
            "shutdown_latched": self.shutdown.is_latched,
            "fault_history": self.fault_history,
            "malformed": getattr(self._producer, "malformed_count", 0),
            "trace": self._trace,
            "scenario": self.scenario,
            "scenario_list": self._scenarios_list,
        }

    # -- scenario switching ----------------------------------------------------

    def switch_scenario(self, scenario_id: str):
        scenario = load_scenario(scenario_id)
        if scenario is None:
            return

        self.scenario = scenario
        self.bands = _bands_from_dict(scenario.thresholds)
        self.window = ReadingWindow(maxlen=300)
        self.alarms = AlarmManager(self.bands)
        self.agent = ReActAgent(self.alarms, self.window, self.bands,
                               stages=scenario.stages,
                               stage_sensor=scenario.stage_sensor)
        self._trace = []
        self.fault_history = []
        self._seq = 0

        fault_engine.set_explanations(scenario.fault_explanations)
        if scenario.fault_tuning:
            fault_engine.set_tuning(scenario.fault_tuning)
        else:
            fault_engine.reset_tuning()

        # Restart the data producer
        if self._producer is not None:
            try:
                self._producer.stop()
            except Exception:
                pass
        self.use_simulator()
        self._producer.start()

        if self._view is not None:
            self._view.set_status(f"Switched to {scenario.name}")
            self._view.update(self._build_state_raw())

    def _build_state_raw(self):
        return {
            "reading": None,
            "zones": {},
            "active_alarms": [],
            "diagnosis": None,
            "stage_health": {stage: "normal" for stage in self.scenario.stages},
            "source": self.source,
            "window": self.window,
            "recording": None,
            "shutdown_latched": False,
            "fault_history": self.fault_history,
            "malformed": 0,
            "trace": self._trace,
            "scenario": self.scenario,
            "scenario_list": self._scenarios_list,
        }

    def _notify_status(self, text: str):
        if self._view is not None and hasattr(self._view, "set_status"):
            try:
                self._view.set_status(text)
            except Exception:
                pass

    def stop(self):
        self._generate_report()
        if self._producer is not None:
            try:
                self._producer.stop()
            except Exception:
                pass

    def _generate_report(self):
        from .report import generate
        path = generate(
            scenario_name=self.scenario.name,
            started_at=self.started_at,
            seq=self._seq,
            fault_history=self.fault_history,
        )
        if path:
            self._notify_status(f"Report saved: {path}")
