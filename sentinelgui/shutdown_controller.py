"""Module 9 — Emergency Shutdown Controller.

Latches the UI into a SHUTDOWN safe state immediately, then makes a best-effort attempt to
send a physical stop command to the rig and reports the outcome (FR-020, FR-021). The UI
safe state is latched *first* and unconditionally, regardless of whether hardware can be
actuated. ``resume`` clears the latch (callers must obtain explicit confirmation first,
FR-022). Pure standard library.

Outcome mapping (contracts/serial-protocol.md §2):
    bytes written + ACK:STOP ≤1 s  -> acked
    bytes written, no ACK          -> sent
    write raises / port closed     -> failed
    no serial channel (simulator)  -> no_channel
"""

from __future__ import annotations

import datetime
from typing import Optional

from .models import ShutdownEvent

STOP_COMMAND = "CMD:STOP"


class ShutdownController:
    """Latch a safe state and best-effort actuate a hardware stop."""

    def __init__(self, source=None):
        self.source = source
        self._latched = False

    @property
    def is_latched(self) -> bool:
        return self._latched

    def trigger(self, by: str = "operator", now: Optional[str] = None) -> ShutdownEvent:
        """Latch SHUTDOWN and attempt a hardware stop. Returns a ``ShutdownEvent``."""
        # 1. Latch the UI safe state first, unconditionally (FR-020).
        self._latched = True
        timestamp = now or datetime.datetime.now().isoformat(timespec="seconds")

        # 2. Attempt the hardware stop and classify the outcome (FR-021).
        outcome, attempted = self._attempt_hardware_stop()
        return ShutdownEvent(
            timestamp=timestamp,
            triggered_by=by,
            ui_safe_state=True,
            hardware_attempted=attempted,
            hardware_outcome=outcome,
        )

    def _attempt_hardware_stop(self) -> tuple[str, bool]:
        send = getattr(self.source, "send_command", None)
        if self.source is None or not callable(send):
            return "no_channel", False
        try:
            written = send(STOP_COMMAND)
        except Exception:
            return "failed", True
        if not written:
            return "failed", True
        read_ack = getattr(self.source, "read_ack", None)
        if callable(read_ack):
            try:
                ack = read_ack(1.0)
            except Exception:
                ack = None
            if ack and "STOP" in ack:
                return "acked", True
        return "sent", True

    def resume(self) -> None:
        """Clear the SHUTDOWN latch (explicit confirmation handled by the caller)."""
        self._latched = False
