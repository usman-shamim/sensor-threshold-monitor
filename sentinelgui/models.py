"""Core in-memory domain objects for SentinelGUI.

Pure standard-library dataclasses (no third-party imports) so every logic module and test
can use them without the GUI stack installed. Field names mirror SentinelCLI where they
cross the bridge (see contracts/sentinelcli-bridge.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Canonical sensor keys and display metadata.
SENSOR_KEYS = ("temperature", "flow_rate", "pressure")

SENSOR_LABELS = {
    "temperature": "Temperature",
    "flow_rate": "Flow Rate",
    "pressure": "Pressure",
}

SENSOR_UNITS = {
    "temperature": "°C",  # °C
    "flow_rate": "L/min",
    "pressure": "bar",
}

# Mimic stage each sensor maps to.
SENSOR_STAGE = {
    "flow_rate": "Flow Sensor",
    "pressure": "Pressure Sensor",
    "temperature": "Reactor",
}

# Ordered mimic loop.
PROCESS_STAGES = ("Reservoir", "Pump", "Flow Sensor", "Pressure Sensor", "Reactor")

FAULT_KEYS = (
    "blockage",
    "pump_failure",
    "cavitation",
    "fouling",
    "thermal_runaway",
    "cooling_failure",
    "undetermined",
)


@dataclass
class Reading:
    """One timestamped sample after engineering-unit conversion."""

    timestamp: str
    values: dict[str, float]
    seq: int = 0
    source: str = "simulator"
    raw: Optional[dict[str, float]] = None


@dataclass
class Alarm:
    """An event raised when a value leaves its safe band."""

    sensor: str
    value: float
    severity: str  # "warning" | "critical"
    limit: str  # "min" | "max"
    bound: float
    raised_at: str
    cleared_at: Optional[str] = None
    state: str = "active"  # "active" | "cleared"

    @property
    def key(self) -> tuple[str, str]:
        """Identity used for dedupe/debounce."""
        return (self.sensor, self.severity)


@dataclass
class FaultDiagnosis:
    """A classified fault with a plain-language explanation."""

    fault: str
    explanation: str
    source: str = "rule"  # "rule" | "ai"
    confidence: str = "medium"  # "low" | "medium" | "high"
    related_sensors: list[str] = field(default_factory=list)


@dataclass
class FaultHistoryEntry:
    """Session-only record of an alarm and its diagnosis (also written to CSV)."""

    timestamp: str
    sensor: str
    value: float
    severity: str
    fault: str
    explanation: str
    source: str


@dataclass
class RecordingSession:
    """State of a CSV recording session."""

    path: Optional[str] = None
    state: str = "idle"  # "idle" | "recording" | "stopped" | "error"
    started_at: Optional[str] = None
    rows_written: int = 0
    error: Optional[str] = None


@dataclass
class DataSource:
    """The active origin of readings."""

    kind: str = "simulator"  # "serial" | "simulator"
    status: str = "simulating"  # "connected" | "disconnected" | "simulating" | "error"
    detail: str = ""


@dataclass
class ProcessStage:
    """A node of the mimic loop with a health/alarm state for highlighting."""

    name: str
    health: str = "normal"  # "normal" | "warning" | "critical"


@dataclass
class ShutdownEvent:
    """A record of an emergency shutdown."""

    timestamp: str
    triggered_by: str = "operator"
    ui_safe_state: bool = True
    hardware_attempted: bool = False
    hardware_outcome: str = "no_channel"  # "sent" | "acked" | "failed" | "no_channel"
