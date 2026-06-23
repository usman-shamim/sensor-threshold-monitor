"""Tests for the CSV data logger."""

import csv

from sentinelgui.data_logger import DataLogger
from sentinelgui.models import Alarm, Reading


def _reading(seq):
    return Reading(
        timestamp=f"2026-06-19T10:00:0{seq}",
        values={"temperature": 50 + seq, "flow_rate": 30.0, "pressure": 3.0},
        seq=seq,
        source="simulator",
    )


def test_start_opens_timestamped_file_with_header(tmp_path):
    logger = DataLogger(directory=str(tmp_path))
    session = logger.start(now="20260619_100000")
    assert session.state == "recording"
    assert session.path.endswith("sentinelgui_20260619_100000.csv")
    logger.stop()
    with open(session.path, newline="", encoding="utf-8") as handle:
        header = next(csv.reader(handle))
    assert header[0] == "timestamp" and "pressure" in header


def test_write_appends_one_row_per_reading(tmp_path):
    logger = DataLogger(directory=str(tmp_path))
    session = logger.start(now="20260619_100001")
    logger.write(_reading(1), [])
    logger.write(_reading(2), [Alarm("temperature", 95, "warning", "max", 90, "t")])
    logger.stop()
    assert session.rows_written == 2
    with open(session.path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 3  # header + 2 data rows
    assert rows[2][-1] == "warning:temperature"


def test_unwritable_directory_enters_error_state(tmp_path):
    missing = tmp_path / "does_not_exist"
    logger = DataLogger(directory=str(missing))
    session = logger.start(now="20260619_100002")
    assert session.state == "error"
    assert "Cannot write" in session.error
    # Writing while in error state is a safe no-op.
    logger.write(_reading(1), [])
    assert session.rows_written == 0
