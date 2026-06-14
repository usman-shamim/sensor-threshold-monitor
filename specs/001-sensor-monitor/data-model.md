# Phase 1 Data Model: Sensor Threshold Monitor

In-memory data only (no persistence). Representations are plain stdlib types (dicts/lists) to keep
the design simple and stdlib-only.

## Entity: Reading

A single timestamped observation parsed from one CSV data row.

| Field | Type | Notes |
|-------|------|-------|
| `timestamp` | str | Raw timestamp from the CSV; `None` if column absent/blank → caller falls back to `row <N>`. |
| `row` | int | 1-based data row index (for diagnostics and timestamp fallback). |
| `values` | dict[str, float] | Sensor name → numeric value, e.g. `{"temperature": 91.4, "pressure": 3.1, "flow_rate": 22.0}`. Only successfully parsed numeric sensors are included. |

**Validation rules**:

- A row with a non-numeric or missing value for an expected sensor is reported (`row N`) and the
  whole row is skipped (FR-007); it does not produce a Reading used for alerting.
- Extra/unknown columns are ignored.

## Entity: Threshold (Safe Range) / Config

The set of inclusive safe ranges, loaded from `config.json` or built-in defaults.

| Field | Type | Notes |
|-------|------|-------|
| `<sensor>` | object | One per sensor (`temperature`, `pressure`, `flow_rate`). |
| `<sensor>.min` | float | Inclusive lower bound. |
| `<sensor>.max` | float | Inclusive upper bound. |

Default ranges (documented; used when `--config` omitted):

| Sensor | min | max | unit (informational) |
|--------|-----|-----|----------------------|
| temperature | 0 | 100 | °C |
| pressure | 1.0 | 5.0 | bar |
| flow_rate | 10 | 50 | L/min |

**Validation rules**:

- Each configured sensor MUST provide numeric `min` and `max` with `min <= max`; otherwise load
  fails with a human-readable message and non-zero exit.
- A config may define a subset of sensors; unlisted sensors fall back to defaults.

## Entity: Alert

Produced when a sensor value is outside its inclusive safe range.

| Field | Type | Notes |
|-------|------|-------|
| `sensor` | str | Sensor type that breached (`temperature`/`pressure`/`flow_rate`). |
| `value` | float | The offending reading value. |
| `limit` | str | Which bound was breached: `"min"` or `"max"`. |
| `bound` | float | The numeric bound value that was breached. |
| `timestamp` | str | Reading timestamp, or `row <N>` fallback. |
| `diagnosis` | str \| None | Optional plain-language AI explanation; `None` unless `--ai` succeeded. |

**Rules**:

- `value < min` → `limit="min"`; `value > max` → `limit="max"`. Equality with a bound is in-range
  (FR-006) and produces no alert.
- One Alert per out-of-range sensor value (a single Reading may yield multiple Alerts).

## Entity: Summary Report

End-of-run aggregate.

| Field | Type | Notes |
|-------|------|-------|
| `total_readings` | int | Count of readings evaluated (excludes skipped malformed rows). |
| `alert_count` | int | Total number of Alerts raised. |
| `triggered_sensors` | set[str] / sorted list | Distinct sensors with ≥1 alert; empty when no alerts. |
| `skipped_rows` | int | Count of malformed rows skipped (surfaced for transparency). |

**Rules**:

- When `alert_count == 0`, the report clearly states no sensors triggered alerts (FR-008).
- `total_readings` and `alert_count` MUST match the input data exactly (SC-002).

## Relationships

```text
Config (Thresholds) ──applied to──> Reading.values ──produces──> Alert(s)
Reading (many) ──aggregated into──> Summary Report
Alert (0..n) ──optionally annotated by──> AI diagnosis (diagnose_alert)
```
