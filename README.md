# Sensor Threshold Monitor

An industrial process monitoring system built in Python, consisting of two cooperating tools:

- **SentinelCLI** — a command-line tool that reads sensor CSV data, checks it against configurable thresholds, and optionally diagnoses faults using Gemini AI.
- **SentinelGUI** — a desktop SCADA-style dashboard that monitors a live reactor cooling loop in real time, raises alarms, classifies faults, and optionally enriches diagnoses with AI.

#### Video Demo: `<URL HERE>`

---

## How the two tools relate

SentinelCLI (`project.py`) provides the core threshold logic and AI layer.
SentinelGUI **reuses** two functions from it directly:

| CLI function | Where GUI uses it |
|---|---|
| `check_reading(reading, thresholds)` | `sentinelgui/thresholds.py` — decides normal / warning / critical for each sensor |
| `diagnose_alert(alert, client)` | `sentinelgui/sentinelcli_bridge.py` — calls Gemini AI on demand for richer explanations |

The GUI never modifies `project.py`. Both tools remain independently runnable.

---

## SentinelCLI — command-line batch monitor

Reads a CSV of sensor readings, checks every value against safe thresholds, logs a
timestamped alert for each out-of-range value, and prints a summary report.
Uses only the Python standard library — no installation required.

### Quick start

```bash
# No dependencies needed — standard library only
python project.py sample_readings.csv

# With custom thresholds
python project.py sample_readings.csv --config config.json

# With optional Gemini AI diagnosis
export GEMINI_API_KEY=your-key-here
python project.py sample_readings.csv --config config.json --ai
```

### Project files

| File | Purpose |
|------|---------|
| `project.py` | `main()` + `load_config`, `read_readings`, `check_reading`, `format_summary`, `diagnose_alert` |
| `test_project.py` | pytest suite — one `test_<function>` per function |
| `config.json` | Default safe ranges per sensor |
| `sample_readings.csv` | Example input (includes out-of-range and malformed rows) |
| `requirements.txt` | Optional extras only; core needs nothing |

### Input format

CSV with a header row containing a timestamp column and any sensor columns
(`temperature`, `pressure`, `flow_rate`; aliases like `temp`/`flow` accepted).
Malformed rows are skipped and reported; processing continues.

### Thresholds (`config.json`)

```json
{
  "temperature": { "min": 0, "max": 100 },
  "pressure":    { "min": 1.0, "max": 5.0 },
  "flow_rate":   { "min": 10, "max": 50 }
}
```

Bounds are inclusive. Omitted sensors use built-in defaults.

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Run completed (including zero-alert or skipped-row runs) |
| non-zero | Could not run — missing input or invalid config |

### Tests

```bash
pip install pytest
pytest test_project.py
```

AI test uses a fake client — no network or API key needed.

---

## SentinelGUI — live SCADA dashboard

A desktop monitoring and fault-diagnosis dashboard for a physical reactor cooling-loop
rig. Receives real-time temperature, flow-rate, and pressure readings from an Arduino
over USB serial (or a built-in fault simulator), evaluates them against Warning/Critical
thresholds, raises alarms, names the likely fault, and offers AI-enriched explanations
on demand.

### Quick start

```bash
# 1. Install dependencies
pip install -r sentinelgui/requirements.txt

# 2. Run with the built-in simulator (no hardware needed)
python -m sentinelgui --simulate
```

### Run modes

```bash
python -m sentinelgui --simulate                  # no hardware — fault injection available
python -m sentinelgui --port COM3                 # live Arduino rig (Windows)
python -m sentinelgui --port /dev/ttyUSB0         # live Arduino rig (Linux/macOS)
python -m sentinelgui --simulate --kiosk          # exhibition fullscreen mode
```

If the specified port cannot be opened the app falls back to the simulator automatically.

### Features

| Feature | Description |
|---------|-------------|
| Live sensor cards | Temperature, flow rate, pressure — value, unit, and zone at 1 Hz |
| Real-time trend charts | Scrolling Matplotlib chart per sensor |
| Process mimic diagram | Reservoir → Pump → Flow → Pressure → Reactor, fault stage highlighted |
| Alarm panel | Warning / Critical alarms with debounce |
| Rule-based diagnosis | Blockage, pump failure, cavitation, fouling, thermal runaway, cooling failure — offline, no key needed |
| AI diagnosis | "Explain with AI" button calls SentinelCLI's Gemini layer; ~10 s timeout then silent fallback |
| CSV recording | Start/stop timestamped `sentinelgui_YYYYMMDD_HHMMSS.csv` |
| Fault history log | Every alarm with timestamp, sensor, value, severity, diagnosis |
| Emergency Shutdown | Latches SHUTDOWN state, sends `CMD:STOP` to rig, logs event |
| Kiosk mode | Fullscreen, enlarged cards, confirmation guards — `--kiosk` flag |

### Connecting a physical rig

The Arduino must emit one CSV frame per second at 115200 baud:

```
temperature,flow_rate,pressure\n
```

Example: `72.4,34.1,3.2`

Emergency stop: SentinelGUI sends `CMD:STOP\n`; Arduino replies `ACK:STOP\n` within 1 s.

Threshold defaults (`sentinelgui/config/gui_config.json`):

| Sensor | Critical min | Warning min | Warning max | Critical max |
|--------|-------------|-------------|-------------|-------------|
| Temperature (°C) | 0 | 10 | 90 | 100 |
| Pressure (bar) | 1.0 | 1.4 | 4.6 | 5.0 |
| Flow rate (L/min) | 10 | 14 | 46 | 50 |

### Gemini AI key (optional)

```bash
# Linux / macOS
export GEMINI_API_KEY=your-key-here

# Windows PowerShell
$env:GEMINI_API_KEY = "your-key-here"
```

Rule-based diagnosis always works without a key. The key is never hardcoded.

### Architecture

```
sentinelgui/
├── models.py              Reading, Alarm, FaultDiagnosis dataclasses
├── reading_window.py      Rolling deque buffer + per-sensor slope helpers
├── acquisition.py         Background serial thread → queue.Queue
├── simulator.py           Offline FaultSimulator (inject / clear_fault)
├── process_engine.py      Raw values → engineering units
├── thresholds.py          Two-band zone_of(), reuses project.check_reading
├── alarm_manager.py       Debounced Warning/Critical alarms + history
├── fault_engine.py        Value-primary hybrid fault classifier
├── react_agent.py         Observe → Reason → Act loop
├── sentinelcli_bridge.py  ai_diagnose() off UI thread; reuses project.diagnose_alert
├── data_logger.py         stdlib-csv timestamped recording
├── shutdown_controller.py Latching SHUTDOWN + CMD:STOP/ACK:STOP
├── app.py                 AppController — queue drain, root.after(250) loop
├── __main__.py            argparse launcher
├── config/gui_config.json threshold and serial config
├── requirements.txt
└── dashboard/             GUI widgets (customtkinter + matplotlib)
```

### Tests

```bash
# All SentinelGUI tests (no hardware or network needed)
pytest sentinelgui/tests/ -v

# Everything — GUI + CLI isolation check
pytest sentinelgui/tests/ test_project.py -q
# Expected: 58 passed (51 GUI + 7 CLI)
```

---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| pytest | any (tests only) |
| customtkinter | 5.2+ (SentinelGUI only) |
| matplotlib | 3.9+ (SentinelGUI only) |
| pyserial | 3.5+ (SentinelGUI only) |

SentinelCLI has **no third-party dependencies**.

---

## License

[MIT](LICENSE) © 2026 usman-shamim
