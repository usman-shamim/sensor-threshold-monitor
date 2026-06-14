# CLI Contract: Sensor Threshold Monitor

The tool's sole interface is an `argparse`-based command line (Constitution Principle IV).

## Invocation

```text
python project.py INPUT [--config PATH] [--ai | --no-ai]
```

## Arguments

| Argument | Kind | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `INPUT` | positional | Yes | — | Path to the CSV file of sensor readings. |
| `--config PATH` | option | No | built-in defaults | Path to a `config.json` threshold file (see `config.schema.json`). |
| `--ai` | flag | No | off | Enable the optional Claude AI diagnosis layer (requires `ANTHROPIC_API_KEY` and the `anthropic` package). |
| `--no-ai` | flag | No | on (default) | Explicitly disable AI diagnosis; pure stdlib path. Mutually exclusive with `--ai`. |
| `-h`, `--help` | flag | No | — | Auto-generated usage help. |

- `--ai` and `--no-ai` are mutually exclusive (argparse mutually exclusive group); default is AI
  disabled.

## Behavior contract

1. Validate that `INPUT` exists and is readable → else error to `stderr`, exit non-zero.
2. Load thresholds (from `--config` or defaults); invalid config → error, exit non-zero.
3. Read and evaluate each reading; collect alerts; skip + report malformed rows, continue.
4. If `--ai` is active and available, annotate each alert with a diagnosis; if unavailable, warn
   to `stderr` and continue without diagnoses.
5. Print each alert (human-readable, with sensor, value, breached limit, timestamp) to `stdout`.
6. Print the summary report (total readings, alert count, triggered sensors, skipped rows) to
   `stdout`.

## Output streams & exit codes

| Stream | Content |
|--------|---------|
| `stdout` | Alerts and summary report. |
| `stderr` | Warnings (e.g., AI unavailable) and anticipated error messages. |

| Exit code | Meaning |
|-----------|---------|
| `0` | Run completed (including zero alerts and/or some skipped rows). |
| non-zero (`1`) | Run could not be performed: missing/unreadable input or invalid config. |

## Examples

```text
# Default (stdlib only, no AI), built-in thresholds
python project.py sample_readings.csv

# Custom thresholds
python project.py sample_readings.csv --config config.json

# Explicitly disable AI (same as default)
python project.py sample_readings.csv --no-ai

# Enable AI diagnosis (needs ANTHROPIC_API_KEY in environment)
python project.py sample_readings.csv --config config.json --ai
```
