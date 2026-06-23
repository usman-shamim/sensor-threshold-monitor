"""Tests for the hybrid rule-based fault classifier."""

from sentinelgui.fault_engine import classify, slope
from sentinelgui.models import Reading
from sentinelgui.reading_window import ReadingWindow


def _window(series):
    """Build a window from a list of (temp, flow, press) tuples in time order."""
    win = ReadingWindow(maxlen=300)
    for i, (t, f, p) in enumerate(series):
        win.append(Reading(timestamp=f"t{i}", values={"temperature": t, "flow_rate": f, "pressure": p}, seq=i))
    return win


def test_slope_detects_rising_series():
    win = _window([(10, 30, 3), (12, 30, 3), (14, 30, 3), (16, 30, 3)])
    assert slope(win, "temperature", 4) > 0


def test_blockage_flow_down_pressure_up():
    series = [(50, 30 - i, 3.0 + i * 0.2) for i in range(12)]
    win = _window(series)
    reading = Reading(timestamp="t", values={"temperature": 50, "flow_rate": 18, "pressure": 4.5})
    assert classify(reading, win).fault == "blockage"


def test_pump_failure_flow_and_pressure_collapse():
    series = [(50, 30 - i * 2.5, 3.0 - i * 0.2) for i in range(12)]
    win = _window(series)
    reading = Reading(timestamp="t", values={"temperature": 50, "flow_rate": 2.0, "pressure": 1.0})
    assert classify(reading, win).fault == "pump_failure"


def test_thermal_runaway_steep_temperature_rise():
    series = [(70 + i * 4, 30, 3.0) for i in range(12)]
    win = _window(series)
    reading = Reading(timestamp="t", values={"temperature": 110, "flow_rate": 30, "pressure": 3.0})
    assert classify(reading, win).fault == "thermal_runaway"


def test_cavitation_low_oscillating_pressure():
    series = [(50, 30, 1.5 + (0.8 if i % 2 else -0.8)) for i in range(12)]
    win = _window(series)
    reading = Reading(timestamp="t", values={"temperature": 50, "flow_rate": 30, "pressure": 1.4})
    assert classify(reading, win).fault == "cavitation"


def test_undetermined_when_no_signature_matches():
    win = _window([(50, 30, 3.0)] * 12)
    reading = Reading(timestamp="t", values={"temperature": 50, "flow_rate": 30, "pressure": 3.0})
    assert classify(reading, win).fault == "undetermined"
