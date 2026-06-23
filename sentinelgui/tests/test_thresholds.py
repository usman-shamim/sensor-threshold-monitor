"""Tests for two-band threshold loading and zone classification."""

import json

import pytest

from sentinelgui.thresholds import ThresholdBand, load_thresholds, zone_of

BANDS = {
    "temperature": ThresholdBand(
        critical={"min": 0.0, "max": 100.0}, warning={"min": 10.0, "max": 90.0}
    )
}


def test_zone_normal_inside_warning_band():
    assert zone_of("temperature", 50.0, BANDS) == "normal"


def test_zone_warning_between_warning_and_critical():
    assert zone_of("temperature", 95.0, BANDS) == "warning"
    assert zone_of("temperature", 5.0, BANDS) == "warning"


def test_zone_critical_beyond_critical_band():
    assert zone_of("temperature", 105.0, BANDS) == "critical"
    assert zone_of("temperature", -1.0, BANDS) == "critical"


def test_zone_boundary_is_inclusive_in_range():
    # Equal to a warning bound is still inside the safe (normal) zone.
    assert zone_of("temperature", 90.0, BANDS) == "normal"
    assert zone_of("temperature", 10.0, BANDS) == "normal"
    # Equal to a critical bound is in the warning zone, not critical.
    assert zone_of("temperature", 100.0, BANDS) == "warning"


def test_zone_unknown_sensor_is_normal():
    assert zone_of("humidity", 999.0, BANDS) == "normal"


def test_load_thresholds_default_config_is_valid():
    bands = load_thresholds()
    assert set(bands) == {"temperature", "pressure", "flow_rate"}
    assert bands["pressure"].critical["max"] == 5.0


def test_load_thresholds_rejects_broken_nesting(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "thresholds": {
                    "temperature": {
                        "critical": {"min": 0, "max": 100},
                        "warning": {"min": 10, "max": 110},  # warning.max > critical.max
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="critical.min <= warning.min"):
        load_thresholds(str(bad))
