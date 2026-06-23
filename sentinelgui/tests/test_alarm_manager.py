"""Tests for the AlarmManager (debounce, raise/clear, history retention)."""

from sentinelgui.alarm_manager import AlarmManager
from sentinelgui.models import Reading
from sentinelgui.thresholds import ThresholdBand

BANDS = {
    "temperature": ThresholdBand(
        critical={"min": 0.0, "max": 100.0}, warning={"min": 10.0, "max": 90.0}
    )
}


def _reading(temp, seq=0):
    return Reading(timestamp=f"t{seq}", values={"temperature": temp}, seq=seq)


def test_no_alarm_in_normal_zone():
    mgr = AlarmManager(BANDS, debounce_samples=1)
    assert mgr.evaluate(_reading(50.0)) == []
    assert mgr.active == []


def test_warning_then_critical_then_clear():
    mgr = AlarmManager(BANDS, debounce_samples=1)
    raised = mgr.evaluate(_reading(95.0, 1))
    assert len(raised) == 1 and raised[0].severity == "warning"
    assert raised[0].limit == "max" and raised[0].bound == 90.0

    upgraded = mgr.evaluate(_reading(105.0, 2))
    severities = {a.severity for a in upgraded}
    assert "critical" in severities  # new critical alarm
    assert any(a.state == "cleared" for a in upgraded)  # old warning cleared
    assert len(mgr.active) == 1 and mgr.active[0].severity == "critical"

    cleared = mgr.evaluate(_reading(50.0, 3))
    assert len(cleared) == 1 and cleared[0].state == "cleared"
    assert mgr.active == []


def test_debounce_suppresses_single_sample_spike():
    mgr = AlarmManager(BANDS, debounce_samples=2)
    # One out-of-range sample should NOT raise yet (needs 2 consecutive).
    assert mgr.evaluate(_reading(95.0, 1)) == []
    assert mgr.active == []
    # Second consecutive confirms the warning.
    raised = mgr.evaluate(_reading(96.0, 2))
    assert len(raised) == 1 and raised[0].severity == "warning"


def test_history_retained_after_clear():
    mgr = AlarmManager(BANDS, debounce_samples=1)
    mgr.evaluate(_reading(95.0, 1))
    mgr.evaluate(_reading(50.0, 2))
    assert mgr.active == []
    assert len(mgr.history) == 1
    assert mgr.history[0].state == "cleared"
    assert mgr.history[0].cleared_at == "t2"
