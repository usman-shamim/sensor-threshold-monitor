# Phase 1 Data Model: SentinelGUI

In-memory domain objects (no database). Types are Python-level; persisted artifacts are the session
CSV and `gui_config.json`. Field names mirror SentinelCLI where they cross the bridge.

## Entities

### Reading
One timestamped sample after engineering-unit conversion.
- `timestamp: str` — ISO-8601 local time when received (GUI-assigned; firmware sends no clock).
- `values: dict[str, float]` — `{"temperature": °C, "flow_rate": L/min, "pressure": bar}`.
- `raw: dict[str, float] | None` — original pre-conversion values (for debugging/logging).
- `seq: int` — monotonically increasing sequence number.
- `source: str` — `"serial"` or `"simulator"`.
- Shape is bridge-compatible with SentinelCLI: `{"timestamp", "row"/"seq", "values"}`.

### Sensor (static metadata)
- `key: str` — `temperature` | `flow_rate` | `pressure`.
- `label: str` — display name (e.g. "Temperature").
- `unit: str` — `°C` | `L/min` | `bar`.
- `stage: str` — mimic stage it maps to (Flow Sensor, Pressure Sensor, Reactor).

### ThresholdBand (per sensor)
Two explicit nested bands (resolved in clarification).
- `critical: {min: float, max: float}` — seeded from SentinelCLI `config.json`.
- `warning: {min: float, max: float}` — nested inside critical (default ≈10% inside each bound).
- Invariant: `critical.min ≤ warning.min ≤ warning.max ≤ critical.max`.
- Zone of a value `v` (inclusive bounds): `critical` if `v < critical.min or v > critical.max`,
  else `warning` if `v < warning.min or v > warning.max`, else `normal`.
- Loaded/validated by `thresholds.py`; reuses SentinelCLI `check_reading` once per band.

### Alarm
Raised when a value leaves its safe band.
- `sensor: str`, `value: float`, `severity: "warning" | "critical"`.
- `limit: "min" | "max"`, `bound: float` (the breached band edge).
- `raised_at: str`, `cleared_at: str | None`.
- `state: "active" | "cleared"`.
- `key: tuple[str, str]` — `(sensor, severity)` identity for dedupe/debounce.

### FaultDiagnosis
- `fault: str` — `blockage | pump_failure | cavitation | fouling | thermal_runaway |
  cooling_failure | undetermined`.
- `explanation: str` — plain-language reason from current values + trend.
- `source: "rule" | "ai"`.
- `confidence: "low" | "medium" | "high"` (rule strength; AI = narrative only).
- `related_sensors: list[str]`.

### FaultHistoryEntry
Session-only record (also written to CSV when recording).
- `timestamp: str`, `sensor: str`, `value: float`, `severity: str`.
- `fault: str`, `explanation: str`, `source: str`.

### RecordingSession
- `path: str` — `sentinelgui_YYYYMMDD_HHMMSS.csv` in the chosen directory.
- `state: "idle" | "recording" | "stopped" | "error"`.
- `started_at: str | None`, `rows_written: int`, `error: str | None`.

### DataSource
- `kind: "serial" | "simulator"`.
- `status: "connected" | "disconnected" | "simulating" | "error"`.
- `detail: str` — port name / simulator scenario / error text.

### ProcessStage (mimic node)
- `name: str` — `Reservoir | Pump | Flow Sensor | Pressure Sensor | Reactor`.
- `health: "normal" | "warning" | "critical"` — drives highlight colour.
- Ordered loop: Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir.

### ShutdownEvent
- `timestamp: str`, `triggered_by: str` (e.g. "operator").
- `ui_safe_state: bool` — always true once latched.
- `hardware_attempted: bool`, `hardware_outcome: "sent" | "acked" | "failed" | "no_channel"`.

### ReadingWindow (rolling buffer)
- Backed by `collections.deque(maxlen=window_samples)` (default ≈300 @ 1 Hz / 5 min).
- Provides: latest reading, per-sensor series for charts, and per-sensor slope (Δ over last N).

## Fault Signature Table (Module 3 logic)

| Fault | Value condition | Trend condition |
|-------|-----------------|-----------------|
| `blockage` | flow in warning/critical-low; pressure high | pressure slope ↑ while flow slope ↓ |
| `pump_failure` | flow near zero; pressure low | flow ↓ and pressure ↓ together |
| `cavitation` | pressure low | high pressure (and/or flow) variance/oscillation in window |
| `fouling` | temperature elevated; flow mildly low | temperature slow ↑ sustained; flow slow ↓ |
| `thermal_runaway` | temperature ≥ critical-max | temperature steep ↑ slope; flow ~normal |
| `cooling_failure` | temperature > warning, sustained | temperature ↑ persists despite adequate flow (slow) |
| `undetermined` | a breach with no signature match | — |

Resolution order (first match wins, then severity rank): pump_failure, blockage, cavitation,
thermal_runaway, cooling_failure, fouling, undetermined.

## State Transitions

### Alarm
```
normal --(value enters warning band)--> warning(active)
warning --(value enters critical band)--> critical(active)
critical --(value back in warning band)--> warning(active)
warning/critical --(value back in safe band, held ≥ debounce)--> cleared   # history retained
```
Debounce/hysteresis: a band change must persist ≥ N samples (config, default 2) before the alarm
state flips, preventing flicker on rapid valve toggling.

### Recording
```
idle --start--> recording --stop--> stopped
recording --(write error)--> error   # warn user, monitoring continues (FR-019)
```

### Shutdown
```
monitoring --E-stop pressed--> SHUTDOWN(ui latched) --attempt serial CMD:STOP-->
   {sent|acked|failed|no_channel}  (logged as ShutdownEvent)
SHUTDOWN --resume (explicit confirm)--> monitoring
```

### DataSource
```
startup --(port openable)--> connected:serial
startup --(no/again unopenable port)--> simulating
connected:serial --(read timeout / unplug)--> disconnected --(kiosk auto)--> simulating
```

## Validation Rules
- Threshold bands must satisfy the nesting invariant; otherwise `thresholds.py` raises a
  human-readable config error (Principle V) and the app refuses to start with that config.
- A frame must yield three finite floats or it is discarded and counted (FR-004); never alarms.
- Engineering conversion must produce finite values; non-finite → frame discarded.
- CSV path parent must be writable at record start; else `RecordingSession.state = error` and the
  user is warned (FR-019).

## Configuration (`sentinelgui/config/gui_config.json`)
```json
{
  "serial": { "port": "COM3", "baud": 115200, "read_timeout_s": 1.0 },
  "thresholds": {
    "temperature": { "critical": {"min": 0,  "max": 100}, "warning": {"min": 10, "max": 90} },
    "pressure":    { "critical": {"min": 1.0,"max": 5.0}, "warning": {"min": 1.4,"max": 4.6} },
    "flow_rate":   { "critical": {"min": 10, "max": 50},  "warning": {"min": 14, "max": 46} }
  },
  "window": { "samples": 300, "slope_n": 10 },
  "alarm": { "debounce_samples": 2 },
  "ai": { "timeout_s": 10 },
  "recording": { "dir": "." }
}
```
Critical values mirror SentinelCLI `config.json`; warning values are ~10% inside each bound.
