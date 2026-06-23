"""Tests for the fault simulator data source."""

import math

from sentinelgui.simulator import NOMINAL, FaultSimulator


def _settle(sim, ticks=40):
    frame = None
    for _ in range(ticks):
        frame = sim.next_frame()
    return frame


def test_nominal_stream_three_finite_floats_near_nominal():
    sim = FaultSimulator()
    frame = _settle(sim)
    assert set(frame) == {"temperature", "flow_rate", "pressure"}
    for value in frame.values():
        assert isinstance(value, float)
        assert math.isfinite(value)
    # Should hover near the nominal operating point.
    assert abs(frame["flow_rate"] - NOMINAL["flow_rate"]) < 3.0
    assert abs(frame["temperature"] - NOMINAL["temperature"]) < 3.0


def test_inject_blockage_drops_flow_and_raises_pressure():
    sim = FaultSimulator()
    _settle(sim)
    sim.inject("blockage")
    frame = _settle(sim)
    assert frame["flow_rate"] < NOMINAL["flow_rate"]
    assert frame["pressure"] > NOMINAL["pressure"]


def test_inject_thermal_runaway_raises_temperature():
    sim = FaultSimulator()
    _settle(sim)
    sim.inject("thermal_runaway")
    frame = _settle(sim)
    assert frame["temperature"] > 100.0


def test_clear_fault_returns_to_nominal():
    sim = FaultSimulator()
    sim.inject("pump_failure")
    _settle(sim)
    sim.clear_fault()
    frame = _settle(sim)
    assert abs(frame["flow_rate"] - NOMINAL["flow_rate"]) < 3.0


def test_inject_unknown_fault_raises():
    sim = FaultSimulator()
    try:
        sim.inject("explosion")
        assert False, "expected ValueError"
    except ValueError:
        pass
