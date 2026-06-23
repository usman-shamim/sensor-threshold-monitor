# SentinelGUI

A desktop, SCADA-style monitoring and fault-diagnosis dashboard for a reactor cooling-loop
demonstration rig. It ingests temperature, flow-rate, and pressure readings from an Arduino
over USB serial (or a built-in fault simulator), evaluates them against two-band
Warning/Critical thresholds, raises alarms, and explains the likely physical fault — with
always-available rule-based diagnosis and optional AI enrichment reused from SentinelCLI.

SentinelGUI is the GUI companion to **SentinelCLI** (`project.py`). It imports SentinelCLI
for threshold logic and AI; it never modifies it.

## Install

```
pip install -r sentinelgui/requirements.txt
```

(Python 3.12. The headless logic and tests run with no third-party packages; the
dependencies above are needed to launch the dashboard.)

## Run

```
python -m sentinelgui --simulate                 # no hardware — recommended for demos/tests
python -m sentinelgui --port COM3                 # Arduino rig (Windows)
python -m sentinelgui --port /dev/ttyUSB0         # Arduino rig (Linux/macOS)
python -m sentinelgui --simulate --kiosk          # exhibition: fullscreen, enlarged, guarded
```

If a serial port can't be opened the app falls back to the simulator so a demo always runs.

## Features

- **Live sensor cards** — value, unit, and normal/warning/critical status (1 Hz).
- **Trend charts** — a scrolling Matplotlib chart per sensor.
- **Process mimic** — Reservoir → Pump → Flow → Pressure → Reactor, with the faulty stage
  highlighted.
- **Alarm panel** — Warning/Critical alarms, debounced against valve-toggle flicker.
- **Rule-based diagnosis** — blockage, pump failure, cavitation, fouling, thermal runaway,
  cooling failure (current values + short-term trend). Works fully offline.
- **Explain with AI** — on-demand enrichment via SentinelCLI's Gemini layer; times out to
  the rule-based text and never blocks the UI.
- **CSV recording** — start/stop to a timestamped `sentinelgui_YYYYMMDD_HHMMSS.csv`.
- **Fault history log** — every alarm with timestamp, sensor, value, severity, diagnosis.
- **Emergency Shutdown** — latches a SHUTDOWN safe state and best-effort sends `CMD:STOP`.

## Optional AI key

Rule-based diagnosis always works with no key. For "Explain with AI", set SentinelCLI's key
(never hardcoded):

```
export GEMINI_API_KEY=...            # PowerShell: $env:GEMINI_API_KEY="..."
```

## Tests

```
pytest sentinelgui/tests/            # SentinelGUI logic (no hardware/network needed)
pytest test_project.py              # SentinelCLI — unchanged, still green
```

## Architecture

Nine cooperating modules with a thin `dashboard/` view layer. A background thread reads the
data source and pushes onto a `queue.Queue`; the CustomTkinter UI drains it via Tk
`after()` polling, so serial and AI never block the UI. See
`specs/002-sentinel-gui/` for the full spec, plan, contracts, and tasks.
