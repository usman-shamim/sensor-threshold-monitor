"""Tests for the Sensor Threshold Monitor (project.py).

Every custom function in project.py has a corresponding test here (Constitution
Principle III). The AI layer is tested with an injected fake client so no network
access or API key is required.
"""

import json
import sys

import pytest

from project import (
    DEFAULT_THRESHOLDS,
    check_reading,
    diagnose_alert,
    format_summary,
    load_config,
    main,
    read_readings,
)


def test_load_config(tmp_path):
    # No path -> a copy of the defaults.
    cfg = load_config(None)
    assert cfg["temperature"] == {"min": 0.0, "max": 100.0}

    # Valid file with a subset -> overrides one sensor, defaults for the rest.
    good = tmp_path / "config.json"
    good.write_text(json.dumps({"pressure": {"min": 2.0, "max": 4.0}}))
    cfg = load_config(str(good))
    assert cfg["pressure"] == {"min": 2.0, "max": 4.0}
    assert cfg["temperature"] == {"min": 0.0, "max": 100.0}

    # min > max -> ValueError with a human-readable message.
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"temperature": {"min": 100, "max": 0}}))
    with pytest.raises(ValueError):
        load_config(str(bad))

    # Missing file -> FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        load_config(str(tmp_path / "nope.json"))


def test_read_readings(tmp_path):
    csv_text = (
        "timestamp,temperature,pressure,flow_rate\n"
        "2026-06-14T10:00,72.5,3.1,22.0\n"
        "2026-06-14T10:01,not_a_number,3.0,21.0\n"  # malformed -> skipped
        ",80.0,3.2,25.0\n"                            # blank timestamp -> kept, None
    )
    path = tmp_path / "r.csv"
    path.write_text(csv_text)
    readings, skipped = read_readings(str(path))
    assert len(readings) == 2
    assert len(skipped) == 1
    assert readings[0]["values"]["temperature"] == 72.5
    assert readings[1]["timestamp"] is None  # blank timestamp falls back later

    # Missing file -> FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        read_readings(str(tmp_path / "missing.csv"))

    # Header-only file -> no readings, no skips.
    empty = tmp_path / "empty.csv"
    empty.write_text("timestamp,temperature,pressure,flow_rate\n")
    readings, skipped = read_readings(str(empty))
    assert readings == [] and skipped == []


def test_check_reading():
    thresholds = DEFAULT_THRESHOLDS

    # All values in range -> no alerts.
    reading = {"timestamp": "t", "row": 1, "values": {"temperature": 50.0, "pressure": 3.0}}
    assert check_reading(reading, thresholds) == []

    # Above max -> one max alert.
    reading = {"timestamp": "t", "row": 2, "values": {"temperature": 150.0}}
    alerts = check_reading(reading, thresholds)
    assert len(alerts) == 1 and alerts[0]["limit"] == "max"

    # Below min -> one min alert.
    reading = {"timestamp": "t", "row": 3, "values": {"flow_rate": 5.0}}
    assert check_reading(reading, thresholds)[0]["limit"] == "min"

    # Boundary values are inclusive -> no alert.
    reading = {"timestamp": "t", "row": 4, "values": {"temperature": 100.0, "pressure": 1.0}}
    assert check_reading(reading, thresholds) == []

    # Missing timestamp -> fall back to "row N".
    reading = {"timestamp": None, "row": 7, "values": {"temperature": 150.0}}
    assert check_reading(reading, thresholds)[0]["timestamp"] == "row 7"


def test_format_summary():
    # Zero alerts -> clear "none" message and zero counts.
    out = format_summary(5, [], skipped=0)
    assert "Total readings : 5" in out
    assert "Alerts         : 0" in out
    assert "none" in out.lower()

    # With alerts -> distinct, sorted triggered sensors and correct counts.
    alerts = [
        {"sensor": "pressure", "value": 6, "limit": "max", "bound": 5, "timestamp": "t"},
        {"sensor": "temperature", "value": 150, "limit": "max", "bound": 100, "timestamp": "t"},
        {"sensor": "pressure", "value": 0, "limit": "min", "bound": 1, "timestamp": "t"},
    ]
    out = format_summary(10, alerts, skipped=2)
    assert "Alerts         : 3" in out
    assert "pressure, temperature" in out
    assert "Skipped rows   : 2" in out


def test_diagnose_alert():
    alert = {
        "sensor": "temperature",
        "value": 150,
        "limit": "max",
        "bound": 100,
        "timestamp": "t",
    }

    # Injected fake client returns a string.
    assert diagnose_alert(alert, client=lambda prompt: "Likely coolant loss.") == (
        "Likely coolant loss."
    )

    # A client that raises -> graceful None, no exception propagates.
    def boom(_prompt):
        raise RuntimeError("api down")

    assert diagnose_alert(alert, client=boom) is None


def test_main_happy_path(tmp_path, capsys, monkeypatch):
    csv_text = (
        "timestamp,temperature,pressure,flow_rate\n"
        "2026-06-14T10:00,118.0,3.0,22.0\n"  # temperature over max
        "2026-06-14T10:01,70.0,3.0,9.0\n"    # flow_rate under min
    )
    path = tmp_path / "r.csv"
    path.write_text(csv_text)

    monkeypatch.setattr(sys, "argv", ["project.py", str(path), "--no-ai"])
    assert main() == 0

    out = capsys.readouterr().out
    assert "ALERT" in out
    assert "Total readings : 2" in out
    assert "Alerts         : 2" in out


def test_main_missing_input(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["project.py", str(tmp_path / "nope.csv")])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code != 0
