"""Module 7 — CSV Data Logger.

Records the reading stream to a timestamped CSV that opens cleanly in spreadsheet tools
(FR-017). Uses the standard-library ``csv`` module so logging works with no third-party
install and is fully unit-testable; if the destination is unwritable the session enters an
``error`` state and monitoring continues (FR-019) rather than raising.
"""

from __future__ import annotations

import csv
import datetime
import os
from typing import Optional

from .models import Reading, RecordingSession

_COLUMNS = ["timestamp", "seq", "source", "temperature", "flow_rate", "pressure", "alarms"]


class DataLogger:
    """Start/stop CSV recording of the reading stream."""

    def __init__(self, directory: str = "."):
        self.directory = directory
        self.session = RecordingSession()
        self._handle = None
        self._writer = None

    def _timestamped_name(self, now: Optional[str]) -> str:
        stamp = now or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"sentinelgui_{stamp}.csv"

    def start(self, now: Optional[str] = None) -> RecordingSession:
        """Open a new timestamped CSV and write the header. Never raises (FR-019)."""
        name = self._timestamped_name(now)
        path = os.path.join(self.directory, name)
        try:
            self._handle = open(path, "w", newline="", encoding="utf-8")
            self._writer = csv.writer(self._handle)
            self._writer.writerow(_COLUMNS)
            self._handle.flush()
        except OSError as exc:
            self.session = RecordingSession(
                path=path, state="error", error=f"Cannot write recording to {path}: {exc}"
            )
            self._handle = None
            self._writer = None
            return self.session
        self.session = RecordingSession(
            path=path,
            state="recording",
            started_at=now or datetime.datetime.now().isoformat(timespec="seconds"),
            rows_written=0,
        )
        return self.session

    def write(self, reading: Reading, alarms: Optional[list] = None) -> None:
        """Append one row for *reading*. No-op if not recording."""
        if self.session.state != "recording" or self._writer is None:
            return
        alarm_text = ";".join(f"{a.severity}:{a.sensor}" for a in (alarms or []))
        row = [
            reading.timestamp,
            reading.seq,
            reading.source,
            reading.values.get("temperature", ""),
            reading.values.get("flow_rate", ""),
            reading.values.get("pressure", ""),
            alarm_text,
        ]
        try:
            self._writer.writerow(row)
            self._handle.flush()
            self.session.rows_written += 1
        except OSError as exc:
            self.session.state = "error"
            self.session.error = f"Recording write failed: {exc}"

    def stop(self) -> RecordingSession:
        """Close the file and mark the session stopped."""
        if self._handle is not None:
            try:
                self._handle.close()
            except OSError:
                pass
        self._handle = None
        self._writer = None
        if self.session.state == "recording":
            self.session.state = "stopped"
        return self.session
