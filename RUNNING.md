# Running the Project

Everything needed to run **SentinelCLI** and **SentinelGUI** on Windows (with Linux/macOS notes).

---

## Prerequisites

- **Python 3.12+** — check: `python --version`
- **pip** — check: `pip --version`
- **pytest** (for tests only): `pip install pytest`

---

## SentinelCLI (command-line batch monitor)

No third-party dependencies — Python standard library only.

```powershell
# Default thresholds (built-in)
python project.py sample_readings.csv

# Custom config
python project.py sample_readings.csv --config config.json

# Optional AI diagnosis (needs Gemini API key)
$env:GEMINI_API_KEY = "your-key-here"
python project.py sample_readings.csv --config config.json --ai
```

**Exit codes:** `0` = success (even with alerts); non-zero = missing input or bad config.

---

## SentinelGUI (desktop SCADA dashboard)

Requires extra packages:

```powershell
pip install -r sentinelgui\requirements.txt
```

### Run with simulator (no hardware needed)

```powershell
python -m sentinelgui --simulate
```

### Run with Arduino rig

```powershell
python -m sentinelgui --port COM3           # Windows
python -m sentinelgui --port /dev/ttyUSB0   # Linux/macOS
```

If the port can't be opened, it falls back to the simulator automatically.

### Exhibition kiosk mode

```powershell
python -m sentinelgui --simulate --kiosk
```

### Optional AI button

```powershell
$env:GEMINI_API_KEY = "your-key-here"
```

Rule-based diagnosis works without it — the AI key only enables the "Explain with AI" button.

---

## Tests

```powershell
# SentinelCLI tests only
pytest test_project.py -q

# SentinelGUI tests only
pytest sentinelgui\tests\ -v

# All tests
pytest sentinelgui\tests\ test_project.py -q
```

Expected: **58 passed** (51 GUI + 7 CLI) — no hardware or network needed.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python not found` | Install Python 3.12+, check PATH during install |
| `ModuleNotFoundError` | `pip install -r sentinelgui\requirements.txt` |
| `pytest not found` | `pip install pytest` |
| Serial port not opening | Run with `--simulate` instead |
| AI diagnosis silent | Check `$env:GEMINI_API_KEY` is set, or ignore (rule-based works offline) |
| GUI won't launch (Linux) | `sudo apt install python3-tk` (system Tk needed by customtkinter) |

---

## Quick reference

```powershell
# CLI
python project.py sample_readings.csv

# GUI (simulated)
python -m sentinelgui --simulate

# Tests
pytest test_project.py sentinelgui\tests\ -q
```
