# Sensor Threshold Monitor

A command-line tool for monitoring industrial process sensor data. It reads a CSV of
sensor readings (temperature, pressure, flow rate), checks each value against
configurable safe thresholds, logs a timestamped alert for every out-of-range value, and
prints a summary report.

#### Video Demo: <URL HERE>

## Description

The tool uses **only the Python standard library** — no installation is required to run
it. An **optional** AI diagnosis layer (Google Gemini API) can add a one-line likely-cause
explanation to each alert; it is off by default, called over HTTPS via the standard-library
`urllib` (no third-party package), and the tool is fully functional without it.

### Project structure

| File | Purpose |
|------|---------|
| `project.py` | Main program: `main()` plus `load_config`, `read_readings`, `check_reading`, `format_summary`, `diagnose_alert`. |
| `test_project.py` | `pytest` tests — one `test_<function>` per custom function. |
| `config.json` | Example/default safe ranges per sensor. |
| `sample_readings.csv` | Example input (includes an out-of-range and a malformed row). |
| `requirements.txt` | Notes the optional `anthropic` extra; core needs nothing. |

### Functions

- **`load_config(path)`** — parses and validates a `config.json` of inclusive `min`/`max`
  ranges; falls back to documented defaults; raises clear errors on invalid input.
- **`read_readings(csv_path)`** — parses the CSV (column names matched by alias), skips and
  reports malformed rows, and returns readings plus a skipped list.
- **`check_reading(reading, thresholds)`** — pure range check; returns an alert per
  out-of-range value (bounds inclusive).
- **`format_summary(total, alerts, skipped)`** — builds the human-readable summary.
- **`diagnose_alert(alert, client=None)`** — optional AI diagnosis; calls the Google
  Gemini REST API via stdlib `urllib`, accepts an injectable client for testing, returns
  `None` if AI is unavailable.

## Usage

```bash
# Default: standard library only, no AI, built-in thresholds
python project.py sample_readings.csv

# Custom thresholds
python project.py sample_readings.csv --config config.json

# Explicitly disable AI (same as default)
python project.py sample_readings.csv --no-ai

# Enable AI diagnosis (requires only a GEMINI_API_KEY; no package to install)
export GEMINI_API_KEY=...
python project.py sample_readings.csv --config config.json --ai
```

### Input format

A CSV with a header row including a timestamp column and any of the sensor columns
(`temperature`, `pressure`, `flow_rate`; common aliases like `temp`/`flow` are accepted).
Extra columns are ignored. Rows with missing or non-numeric sensor values are reported and
skipped; processing continues.

### Thresholds (`config.json`)

```json
{
  "temperature": { "min": 0, "max": 100 },
  "pressure": { "min": 1.0, "max": 5.0 },
  "flow_rate": { "min": 10, "max": 50 }
}
```

Bounds are inclusive. A subset may be provided; unlisted sensors use defaults.

### Exit codes

- `0` — the run completed (including runs with zero alerts or skipped rows).
- non-zero — the run could not be performed (missing/unreadable input or invalid config).

## Running the tests

```bash
pip install pytest
pytest test_project.py
```

The AI test injects a fake client, so the suite needs no network access or API key.
