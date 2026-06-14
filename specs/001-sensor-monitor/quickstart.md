# Quickstart: Sensor Threshold Monitor

## Prerequisites

- Python 3.11 or newer.
- **No installation required** for the core tool — it uses only the standard library.
- *(Optional, AI only)* `pip install anthropic` and an `ANTHROPIC_API_KEY` environment variable
  if you intend to use `--ai`.

## 1. Prepare an input CSV

`sample_readings.csv` (header row + timestamp + the three sensors):

```csv
timestamp,temperature,pressure,flow_rate
2026-06-14T10:00:00,72.5,3.1,22.0
2026-06-14T10:01:00,118.0,3.0,21.5
2026-06-14T10:02:00,70.0,5.9,9.0
```

## 2. (Optional) Define thresholds — `config.json`

```json
{
  "temperature": { "min": 0, "max": 100 },
  "pressure": { "min": 1.0, "max": 5.0 },
  "flow_rate": { "min": 10, "max": 50 }
}
```

If you omit `--config`, the tool uses these same values as built-in defaults.

## 3. Run (default: standard library only, no AI)

```bash
python project.py sample_readings.csv --config config.json
```

Expected (illustrative) output:

```text
ALERT  temperature=118.0 exceeds max 100  @ 2026-06-14T10:01:00
ALERT  pressure=5.9 exceeds max 5.0       @ 2026-06-14T10:02:00
ALERT  flow_rate=9.0 below min 10         @ 2026-06-14T10:02:00

Summary
  Total readings : 3
  Alerts         : 3
  Triggered      : flow_rate, pressure, temperature
  Skipped rows   : 0
```

## 4. (Optional) Enable AI diagnosis

```bash
export ANTHROPIC_API_KEY=sk-...      # never hardcode this
python project.py sample_readings.csv --config config.json --ai
```

Each alert gains a short plain-language likely-cause note. If `anthropic` is not installed or the
key is missing, the tool prints a warning and continues without diagnoses (exit code 0).

## 5. Run the tests

```bash
pytest test_project.py
```

Every custom function in `project.py` has a corresponding `test_<function>` (Constitution
Principle III). AI tests use an injected fake client — no network or API key needed.

## Acceptance checks (map to spec)

- [ ] In-range-only file → 0 alerts, summary alert count 0 (US1 / SC-001).
- [ ] Out-of-range values → one alert each with sensor, value, breached limit, timestamp (US1 / FR-005).
- [ ] Narrowing a threshold in `config.json` changes the alerts (US2 / SC-003).
- [ ] Summary totals match input exactly (US3 / SC-002).
- [ ] Missing file / malformed row / empty file → plain-language message, no traceback (SC-004).
- [ ] `--no-ai` (default) run requires no `pip install` (Constitution Principle II).
