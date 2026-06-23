"""Tests for the ReAct agent step (no AI)."""

from sentinelgui.alarm_manager import AlarmManager
from sentinelgui.models import Reading
from sentinelgui.react_agent import ReActAgent
from sentinelgui.reading_window import ReadingWindow
from sentinelgui.thresholds import ThresholdBand

BANDS = {
    "temperature": ThresholdBand(
        critical={"min": 0.0, "max": 100.0}, warning={"min": 10.0, "max": 90.0}
    ),
    "flow_rate": ThresholdBand(
        critical={"min": 10.0, "max": 50.0}, warning={"min": 14.0, "max": 46.0}
    ),
    "pressure": ThresholdBand(
        critical={"min": 1.0, "max": 5.0}, warning={"min": 1.4, "max": 4.6}
    ),
}


def _agent():
    window = ReadingWindow(maxlen=300)
    alarms = AlarmManager(BANDS, debounce_samples=1)
    return ReActAgent(alarms, window, BANDS), window


def test_step_no_alarm_when_normal():
    agent, window = _agent()
    reading = Reading(timestamp="t", values={"temperature": 50, "flow_rate": 30, "pressure": 3.0})
    window.append(reading)
    result = agent.step(reading)
    assert result.new_alarms == []
    assert result.diagnosis is None
    assert result.stage_health["Reactor"] == "normal"


def test_step_raises_alarm_and_diagnoses():
    agent, window = _agent()
    # Build a rising-temperature history so the diagnosis has trend to work with.
    for i in range(12):
        r = Reading(timestamp=f"t{i}", values={"temperature": 70 + i * 4, "flow_rate": 30, "pressure": 3.0}, seq=i)
        window.append(r)
    reading = Reading(timestamp="now", values={"temperature": 110, "flow_rate": 30, "pressure": 3.0})
    window.append(reading)
    result = agent.step(reading)
    assert any(a.severity == "critical" for a in result.new_alarms)
    assert result.diagnosis is not None
    assert result.diagnosis.fault == "thermal_runaway"
    assert result.stage_health["Reactor"] == "critical"


def test_step_clears_alarm_on_return_to_normal():
    agent, window = _agent()
    hot = Reading(timestamp="t1", values={"temperature": 105, "flow_rate": 30, "pressure": 3.0})
    window.append(hot)
    agent.step(hot)
    cool = Reading(timestamp="t2", values={"temperature": 50, "flow_rate": 30, "pressure": 3.0})
    window.append(cool)
    result = agent.step(cool)
    assert any(a.state == "cleared" for a in result.cleared_alarms)
    assert agent.alarms.active == []
