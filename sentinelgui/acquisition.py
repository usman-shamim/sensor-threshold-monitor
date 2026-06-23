"""Module 1 — Serial Data Acquisition.

``parse_frame`` is a pure function (tested without a port). ``SerialDataAcquisition`` runs
a background thread that reads CSV frames from the Arduino over USB serial and pushes raw
dicts onto a thread-safe queue. PySerial is imported lazily inside methods so that
``parse_frame`` and the test suite work without the library installed.

See contracts/serial-protocol.md for the frame and command grammar.
"""

from __future__ import annotations

import math
import queue
import threading
import time
from typing import Optional

# Canonical field order of an Arduino data frame.
FRAME_FIELDS = ("temperature", "flow_rate", "pressure")


def parse_frame(line: str) -> Optional[dict[str, float]]:
    """Parse one serial line into a raw reading dict, or ``None`` if malformed.

    Rules (contracts/serial-protocol.md §1):
    - Strip surrounding whitespace; ignore empty lines and ``#``-prefixed comments.
    - Split on ``,`` → must be exactly three tokens, each a finite ``float``.
    - On success return ``{"temperature", "flow_rate", "pressure"}`` (raw units).
    - Never raises.
    """
    if line is None:
        return None
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    tokens = text.split(",")
    if len(tokens) != len(FRAME_FIELDS):
        return None
    values = {}
    for field_name, token in zip(FRAME_FIELDS, tokens):
        try:
            number = float(token.strip())
        except (TypeError, ValueError):
            return None
        if not math.isfinite(number):
            return None
        values[field_name] = number
    return values


class SerialDataAcquisition:
    """Background reader for an Arduino serial link.

    Pushes ``parse_frame`` results onto *out_queue*. Malformed frames increment
    ``malformed_count`` and are dropped (never alarm). All serial errors are caught and
    reflected in ``status`` rather than raised on the UI thread.
    """

    def __init__(
        self,
        port: str,
        baud: int = 115200,
        out_queue: "queue.Queue" = None,
        read_timeout_s: float = 1.0,
    ):
        self.port = port
        self.baud = baud
        self.out_queue = out_queue if out_queue is not None else queue.Queue()
        self.read_timeout_s = read_timeout_s
        self.malformed_count = 0
        self._serial = None
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._status = "disconnected"

    @property
    def status(self) -> str:
        """One of: connected | disconnected | error."""
        return self._status

    def start(self) -> None:
        """Open the port and spawn the background read thread."""
        try:
            import serial  # lazy import — pyserial only needed at runtime
        except ImportError as exc:  # pragma: no cover - environment dependent
            self._status = "error"
            raise RuntimeError(
                "pyserial is required for hardware mode; install sentinelgui/requirements.txt"
            ) from exc
        try:
            self._serial = serial.Serial(
                self.port, self.baud, timeout=self.read_timeout_s
            )
        except Exception as exc:  # serial.SerialException and friends
            self._status = "error"
            raise RuntimeError(f"Could not open serial port {self.port}: {exc}") from exc
        self._status = "connected"
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="serial-acq", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                raw_line = self._serial.readline()
            except Exception:
                self._status = "error"
                break
            if not raw_line:
                continue  # read timeout — no data this tick
            try:
                line = raw_line.decode("utf-8", errors="ignore")
            except Exception:
                self.malformed_count += 1
                continue
            parsed = parse_frame(line)
            if parsed is None:
                if line.strip() and not line.strip().startswith("#"):
                    self.malformed_count += 1
                continue
            self.out_queue.put(parsed)

    def send_command(self, cmd: str) -> bool:
        """Write *cmd* (e.g. ``"CMD:STOP"``) to the port. Returns True if bytes written."""
        if self._serial is None:
            return False
        try:
            payload = (cmd.rstrip("\n") + "\n").encode("utf-8")
            self._serial.write(payload)
            return True
        except Exception:
            return False

    def read_ack(self, timeout_s: float = 1.0) -> Optional[str]:
        """Best-effort read of a single ``ACK:`` line within *timeout_s*."""
        if self._serial is None:
            return None
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            try:
                raw = self._serial.readline()
            except Exception:
                return None
            if not raw:
                continue
            text = raw.decode("utf-8", errors="ignore").strip()
            if text.startswith("ACK:"):
                return text
        return None

    def stop(self) -> None:
        """Stop the read thread and close the port."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        self._status = "disconnected"
