# SentinelGUI

A desktop, SCADA-style monitoring and fault-diagnosis dashboard for a reactor cooling-loop
demonstration rig. It ingests temperature, flow-rate, and pressure readings from an Arduino
over USB serial (or a built-in fault simulator), evaluates them against two-band
Warning/Critical thresholds, raises alarms, and explains the likely physical fault — with
always-available rule-based diagnosis and optional AI enrichment reused from SentinelCLI.

SentinelGUI is the GUI companion to **SentinelCLI** (`project.py`). It imports SentinelCLI
for threshold logic and AI; it never modifies it.

---

## Quick start (run this first)

```bash
# 1. Install dependencies
pip install -r sentinelgui/requirements.txt

# 2. Smoke-test — no hardware needed
python -m sentinelgui --simulate
```

If the dashboard opens and sensor cards update, everything is working.

---

## Install

```bash
pip install -r sentinelgui/requirements.txt
```

Requires **Python 3.12+**. The headless logic and tests run with no third-party packages;
the dependencies above (`customtkinter`, `matplotlib`, `pyserial`) are only needed to launch
the dashboard.

---

## Run

```bash
python -m sentinelgui --simulate                  # no hardware — recommended for demos/tests
python -m sentinelgui --port COM3                 # Arduino rig on Windows
python -m sentinelgui --port /dev/ttyUSB0         # Arduino rig on Linux/macOS
python -m sentinelgui --simulate --kiosk          # exhibition: fullscreen, enlarged, guarded
python -m sentinelgui --port COM3 --baud 115200   # custom baud rate (default: 115200)
python -m sentinelgui --config path/to/cfg.json  # alternative config file
```

If a serial port cannot be opened the app falls back to the simulator automatically so a
demo always runs.

---

## Connecting a physical rig (temperature, flow rate, pressure)

### Hardware

The rig connects an **Arduino Nano** to three sensors over USB serial:

| Sensor | Component | Connects to |
|--------|-----------|-------------|
| Temperature | DS18B20 | Arduino digital pin (1-Wire) |
| Flow rate | YF-S201 | Arduino digital pin (interrupt) |
| Pressure | Analog pressure sensor | Arduino analog pin (A0) |

The relay module (emergency shutdown) connects to a digital output pin on the Arduino.

### Arduino serial protocol

The Arduino must emit **one CSV line per second** to USB serial at **115200 baud**:

```
temperature,flow_rate,pressure\n
```

Example frame:
```
72.4,34.1,3.2
```

Rules:
- Exactly three numeric fields per line, comma-separated, newline-terminated.
- Lines beginning with `#` are treated as comments and discarded.
- Lines with the wrong field count or non-numeric values are discarded (counted, not alarmed).
- Emergency stop command: when SentinelGUI sends `CMD:STOP\n`, the Arduino should
  actuate the relay and reply `ACK:STOP\n` within 1 second.

### Automatic threshold defaults

Thresholds are loaded from `sentinelgui/config/gui_config.json`. The shipped defaults are:

| Sensor | Critical min | Warning min | Warning max | Critical max |
|--------|-------------|-------------|-------------|-------------|
| Temperature (°C) | 0 | 10 | 90 | 100 |
| Pressure (bar) | 1.0 | 1.4 | 4.6 | 5.0 |
| Flow rate (L/min) | 10 | 14 | 46 | 50 |

To set your own values, edit `sentinelgui/config/gui_config.json`:

```json
{
  "serial": { "port": "COM3", "baud": 115200, "read_timeout_s": 1.0 },
  "thresholds": {
    "temperature": { "critical": {"min": 0, "max": 100}, "warning": {"min": 10, "max": 90} },
    "pressure":    { "critical": {"min": 1.0, "max": 5.0}, "warning": {"min": 1.4, "max": 4.6} },
    "flow_rate":   { "critical": {"min": 10, "max": 50},  "warning": {"min": 14, "max": 46} }
  },
  "window": { "samples": 300, "slope_n": 10 },
  "alarm": { "debounce_samples": 2 },
  "ai": { "timeout_s": 10 },
  "recording": { "dir": "." }
}
```

`critical` is the outer band (alarm fires here); `warning` is the inner band (early alert).
Critical limits are checked first — if a reading is outside critical it is not also
checked for warning.

### Launching with the rig connected

```bash
# Windows — find your port in Device Manager → Ports (COMx)
python -m sentinelgui --port COM3

# Linux/macOS — usually /dev/ttyUSB0 or /dev/ttyACM0
python -m sentinelgui --port /dev/ttyUSB0
```

If the port is correct but readings do not appear, verify the Arduino is running firmware
that outputs the CSV format above at 115200 baud.

---

## Gemini AI key (optional)

Rule-based diagnosis works fully offline with no key. For the **"Explain with AI"** button
(which calls SentinelCLI's Gemini layer for a richer narrative), set the key as an
environment variable — **never hardcode it**:

```bash
# Linux / macOS
export GEMINI_API_KEY=your-key-here

# Windows PowerShell
$env:GEMINI_API_KEY = "your-key-here"

# Windows Command Prompt
set GEMINI_API_KEY=your-key-here
```

The key is read at runtime. If it is absent, empty, or the call times out (~10 s), the
panel silently keeps the rule-based explanation. No error is raised and monitoring is
never interrupted.

To use a `.env` file (requires `python-dotenv`):

```
# .env  (never commit this file)
GEMINI_API_KEY=your-key-here
```

```bash
pip install python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv()"
python -m sentinelgui --simulate
```

---

## Testing

```bash
# Run all SentinelGUI tests (headless — no hardware or network needed)
pytest sentinelgui/tests/ -v

# Run with coverage
pytest sentinelgui/tests/ --cov=sentinelgui --cov-report=term-missing

# Confirm SentinelCLI is still green (isolation guarantee)
pytest test_project.py -v

# Run everything at once
pytest sentinelgui/tests/ test_project.py -q
```

Expected: **58 passed** (51 SentinelGUI + 7 SentinelCLI).

Test modules:

| Module | Tests | Covers |
|--------|-------|--------|
| `test_acquisition.py` | 5 | Serial frame parsing, malformed frames |
| `test_alarm_manager.py` | 4 | Warning/critical escalation, debounce, history |
| `test_data_logger.py` | 3 | CSV open, write, unwritable-dir error path |
| `test_fault_engine.py` | 6 | All 6 fault signatures + undetermined + resolution order |
| `test_integration_pipeline.py` | 4 | End-to-end: simulator → engine → agent (blockage, thermal runaway, pump failure, clear) |
| `test_process_engine.py` | 4 | Raw → engineering units, non-finite discard |
| `test_react_agent.py` | 3 | Observe→reason→act cycle, alarm + diagnosis output |
| `test_sentinelcli_bridge.py` | 4 | AI call, timeout → None, raising client → None |
| `test_shutdown_controller.py` | 6 | Latch, ACK/NAK/no-channel outcomes |
| `test_simulator.py` | 5 | Nominal stream, fault injection, clear |
| `test_thresholds.py` | 7 | Zone classification, nesting invariant, boundary inclusivity |

---

## Features

- **Live sensor cards** — value, unit, and normal/warning/critical status (1 Hz).
- **Trend charts** — a scrolling Matplotlib chart per sensor.
- **Process mimic** — Reservoir → Pump → Flow → Pressure → Reactor, with the faulty
  stage highlighted in alarm colour.
- **Alarm panel** — Warning/Critical alarms, debounced against valve-toggle flicker.
- **Rule-based diagnosis** — blockage, pump failure, cavitation, fouling, thermal runaway,
  cooling failure. Classified by current values (primary) + short-term trend (corroboration).
  Works fully offline, no key required.
- **Explain with AI** — on-demand enrichment via SentinelCLI's Gemini layer; times out
  gracefully to the rule-based text and never blocks the UI.
- **CSV recording** — start/stop to a timestamped `sentinelgui_YYYYMMDD_HHMMSS.csv`.
- **Fault history log** — every alarm with timestamp, sensor, value, severity, diagnosis.
- **Emergency Shutdown** — latches a SHUTDOWN safe state and best-effort sends `CMD:STOP`
  to the rig; reports whether hardware stop succeeded or could not be actuated.
- **Kiosk / Exhibition mode** — fullscreen, enlarged cards, confirmation guards
  (`--kiosk` flag).
- **Offline-first** — all core capabilities work with no network connection.

---

## Architecture

Twelve cooperating modules with a thin `dashboard/` view layer:

```
sentinelgui/
├── models.py            # Reading, Alarm, FaultDiagnosis dataclasses
├── reading_window.py    # Rolling deque buffer; per-sensor slope helpers
├── acquisition.py       # Background serial thread → queue.Queue
├── simulator.py         # Offline FaultSimulator (inject/clear_fault)
├── process_engine.py    # Raw → engineering units
├── thresholds.py        # Two-band zone_of(), reuses project.check_reading
├── alarm_manager.py     # Debounced Warning/Critical alarms + history
├── fault_engine.py      # Value-primary hybrid fault classifier
├── react_agent.py       # Observe→Reason→Act loop; async AI hook
├── sentinelcli_bridge.py# ai_diagnose() off UI thread, GEMINI_API_KEY env
├── data_logger.py       # stdlib-csv timestamped recording
├── shutdown_controller.py# Latching SHUTDOWN + CMD:STOP/ACK:STOP + resume
├── app.py               # AppController: queue drain, root.after(250) loop
├── __main__.py          # argparse launcher (--simulate/--port/--baud/--kiosk)
├── config/gui_config.json
├── requirements.txt
└── dashboard/
    ├── theme.py         # Dark CustomTkinter colour constants
    ├── sensor_card.py   # Value + zone status widget
    ├── trend_chart.py   # Scrolling Matplotlib FigureCanvasTkAgg
    ├── mimic_diagram.py # Process loop with per-stage health colour
    ├── alarm_panel.py   # Warning/Critical alarm list
    ├── fault_log.py     # Session fault history table
    ├── ai_panel.py      # Rule-based + "Explain with AI" panel
    └── main_window.py   # Root window + grid layout
```

A background thread reads the data source and pushes frames onto a `queue.Queue`.
The CustomTkinter UI drains it via `root.after(250, drain)`, so serial I/O and AI calls
never block the event loop. See `specs/002-sentinel-gui/` for the full spec, plan,
contracts, and task breakdown.
