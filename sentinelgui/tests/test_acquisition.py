"""Tests for the pure serial frame parser (no port required)."""

from sentinelgui.acquisition import parse_frame


def test_parse_valid_frame():
    assert parse_frame("72.4,31.8,3.21") == {
        "temperature": 72.4,
        "flow_rate": 31.8,
        "pressure": 3.21,
    }


def test_parse_tolerates_surrounding_whitespace():
    assert parse_frame("  72.4 , 31.8 , 3.21  \r\n") == {
        "temperature": 72.4,
        "flow_rate": 31.8,
        "pressure": 3.21,
    }


def test_parse_ignores_comment_and_empty_lines():
    assert parse_frame("# STATUS: ok") is None
    assert parse_frame("   ") is None
    assert parse_frame("") is None
    assert parse_frame(None) is None


def test_parse_rejects_wrong_token_count():
    assert parse_frame("72.4,31.8") is None
    assert parse_frame("72.4,31.8,3.21,9.9") is None


def test_parse_rejects_non_numeric_and_non_finite():
    assert parse_frame("72.4,abc,3.21") is None
    assert parse_frame("nan,31.8,3.21") is None
    assert parse_frame("72.4,inf,3.21") is None
