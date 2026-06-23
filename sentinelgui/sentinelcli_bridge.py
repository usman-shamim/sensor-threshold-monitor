"""Module 5 — SentinelCLI Integration Bridge.

Reuses the existing ``project.py`` (SentinelCLI) for optional AI diagnosis rather than
reimplementing it. Maps a SentinelGUI ``Alarm`` to a SentinelCLI alert dict and calls
``project.diagnose_alert`` on a worker thread bounded by a timeout, so the UI and the
emergency-stop control never block (Constitution v3.0.0, Principle IV). Never raises —
returns ``None`` on timeout/unavailability so the caller falls back to rule-based text.

Credentials: ``project.diagnose_alert`` reads ``GEMINI_API_KEY`` from the environment;
SentinelGUI hardcodes no key (Principle VI).
"""

from __future__ import annotations

import concurrent.futures
from typing import Callable, Optional

import project  # SentinelCLI — reused, never modified


def alarm_to_cli_alert(alarm) -> dict:
    """Adapt a SentinelGUI ``Alarm`` to the SentinelCLI alert dict shape."""
    return {
        "sensor": alarm.sensor,
        "value": alarm.value,
        "limit": alarm.limit,  # "min" | "max"
        "bound": alarm.bound,
        "timestamp": alarm.raised_at,
    }


def ai_diagnose(
    alarm,
    timeout_s: float = 10.0,
    client: Optional[Callable[[str], str]] = None,
) -> Optional[str]:
    """Return an AI narrative for *alarm*, or ``None`` on timeout/unavailability.

    Runs ``project.diagnose_alert`` on a worker thread and joins with *timeout_s*.
    *client* is an injectable callable (as SentinelCLI's tests use) so the bridge is
    testable with no network. Never raises.
    """
    alert = alarm_to_cli_alert(alarm)
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(project.diagnose_alert, alert, client)
            try:
                return future.result(timeout=timeout_s)
            except concurrent.futures.TimeoutError:
                return None
    except Exception:
        return None
