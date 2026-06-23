"""Tests for the process data engine (raw -> engineering Reading)."""

import math

from sentinelgui.process_engine import build_reading, to_engineering


def test_to_engineering_identity_passthrough():
    raw = {"temperature": 72.4, "flow_rate": 31.8, "pressure": 3.21}
    assert to_engineering(raw) == raw


def test_to_engineering_rejects_non_finite():
    assert to_engineering({"temperature": math.inf}) is None
    assert to_engineering({"pressure": math.nan}) is None


def test_build_reading_populates_fields():
    raw = {"temperature": 50.0, "flow_rate": 30.0, "pressure": 3.0}
    reading = build_reading(raw, seq=7, source="simulator", now="2026-06-19T10:00:00")
    assert reading is not None
    assert reading.seq == 7
    assert reading.source == "simulator"
    assert reading.timestamp == "2026-06-19T10:00:00"
    assert reading.values["temperature"] == 50.0
    assert reading.raw == raw


def test_build_reading_returns_none_on_bad_value():
    assert build_reading({"temperature": math.inf}, 1, "serial", "t") is None
