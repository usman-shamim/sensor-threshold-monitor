"""Tests for the SentinelCLI AI bridge (no network — injectable client)."""

import time

from sentinelgui.models import Alarm
from sentinelgui.sentinelcli_bridge import ai_diagnose, alarm_to_cli_alert


def _alarm():
    return Alarm(
        sensor="temperature",
        value=105.0,
        severity="critical",
        limit="max",
        bound=100.0,
        raised_at="2026-06-19T10:00:00",
    )


def test_alarm_to_cli_alert_mapping():
    alert = alarm_to_cli_alert(_alarm())
    assert alert == {
        "sensor": "temperature",
        "value": 105.0,
        "limit": "max",
        "bound": 100.0,
        "timestamp": "2026-06-19T10:00:00",
    }


def test_ai_diagnose_returns_client_text():
    result = ai_diagnose(_alarm(), client=lambda prompt: "Likely thermal runaway.")
    assert result == "Likely thermal runaway."


def test_ai_diagnose_returns_none_when_client_raises():
    def boom(prompt):
        raise RuntimeError("no network")

    assert ai_diagnose(_alarm(), client=boom) is None


def test_ai_diagnose_times_out_to_none():
    def slow(prompt):
        time.sleep(0.5)
        return "too late"

    assert ai_diagnose(_alarm(), timeout_s=0.05, client=slow) is None
