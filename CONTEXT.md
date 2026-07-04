# Context: Sensor Threshold Monitor

## Domain

Industrial process monitoring for a reactor cooling loop. Two tools:

| Tool | Purpose |
|------|---------|
| **SentinelCLI** | CLI batch monitor — reads CSV sensor readings, checks against thresholds, logs alerts, optionally diagnoses via Gemini AI |
| **SentinelGUI** | Desktop SCADA dashboard — real-time monitoring, alarm panel, fault diagnosis, emergency shutdown |

## Sensors

| Sensor | Unit | Normal range |
|--------|------|-------------|
| Temperature | °C | 0–100 |
| Pressure | bar | 1.0–5.0 |
| Flow rate | L/min | 10–50 |

## Key terms

| Term | Definition |
|------|------------|
| Reading | A single snapshot of all sensor values at one timestamp |
| Alert | An out-of-range sensor value (below min or above max) |
| Zone | Normal / Warning / Critical — two-band threshold classification |
| Fault | A diagnosed failure mode (blockage, pump failure, cavitation, fouling, thermal runaway, cooling failure) |
| SHUTDOWN | Latched safe state triggered by emergency stop |
| Kiosk | Fullscreen exhibition mode with enlarged UI and confirmation guards |

## Architecture

- SentinelGUI reuses `project.check_reading()` and `project.diagnose_alert()` from SentinelCLI
- GUI never modifies `project.py`
- Serial protocol: CSV frames at 115200 baud, `CMD:STOP` / `ACK:STOP`
- Background thread + `queue.Queue` — UI never blocks on serial or AI
- All business logic is headless (unit-tested without GUI)
