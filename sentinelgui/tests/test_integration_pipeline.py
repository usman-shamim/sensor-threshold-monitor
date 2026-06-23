"""End-to-end pipeline test (no UI, no hardware): simulator → engine → agent → diagnosis.

Exercises the same composition the AppController drives each tick, validating the
offline simulator path (SC-003) and correct fault identification (SC-002).
"""

from sentinelgui.alarm_manager import AlarmManager
from sentinelgui.process_engine import build_reading
from sentinelgui.react_agent import ReActAgent
from sentinelgui.reading_window import ReadingWindow
from sentinelgui.simulator import FaultSimulator
from sentinelgui.thresholds import load_thresholds


def _drive(fault, ticks=60):
    bands = load_thresholds()
    window = ReadingWindow(maxlen=300)
    agent = ReActAgent(AlarmManager(bands, debounce_samples=1), window, bands)
    sim = FaultSimulator()
    last = None
    for seq in range(ticks):
        if seq == 10:
            sim.inject(fault)
        raw = sim.next_frame()
        reading = build_reading(raw, seq, "simulator", f"t{seq}")
        window.append(reading)
        last = agent.step(reading)
    return agent, last


def test_blockage_pipeline_raises_alarm_and_diagnoses():
    agent, result = _drive("blockage")
    assert agent.alarms.active, "expected an active alarm for an injected blockage"
    assert result.diagnosis is not None
    assert result.diagnosis.fault == "blockage"


def test_thermal_runaway_pipeline_identifies_fault():
    agent, result = _drive("thermal_runaway")
    assert any(a.severity == "critical" for a in agent.alarms.active)
    assert result.diagnosis.fault == "thermal_runaway"


def test_pump_failure_pipeline_identifies_fault():
    agent, result = _drive("pump_failure")
    assert result.diagnosis is not None
    assert result.diagnosis.fault == "pump_failure"


def test_clear_fault_returns_to_normal_and_clears_alarms():
    bands = load_thresholds()
    window = ReadingWindow(maxlen=300)
    agent = ReActAgent(AlarmManager(bands, debounce_samples=1), window, bands)
    sim = FaultSimulator()
    sim.inject("thermal_runaway")
    for seq in range(40):
        raw = sim.next_frame()
        window.append(build_reading(raw, seq, "simulator", f"t{seq}"))
        agent.step(window.latest)
    assert agent.alarms.active
    sim.clear_fault()
    for seq in range(40, 90):
        raw = sim.next_frame()
        window.append(build_reading(raw, seq, "simulator", f"t{seq}"))
        result = agent.step(window.latest)
    assert agent.alarms.active == []
