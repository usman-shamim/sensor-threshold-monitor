"""Sensor Threshold Monitor.

A command-line tool that checks industrial process sensor readings (temperature,
pressure, flow rate) from a CSV file against configurable safe thresholds, logs a
timestamped alert for every out-of-range value, and prints a summary report.

The default and ``--no-ai`` paths use only the Python standard library. An optional AI
diagnosis layer (Google Gemini API) can annotate alerts with a likely cause when enabled
with ``--ai``; it is called over HTTPS with the standard-library ``urllib`` (no
third-party package), so the whole tool remains standard-library only.

Usage:
    python project.py INPUT.csv [--config config.json] [--ai | --no-ai]
"""

import argparse
import csv
import json
import os
import sys
import urllib.request


# Default inclusive safe ranges, used when --config is omitted or omits a sensor.
DEFAULT_THRESHOLDS = {
    "temperature": {"min": 0.0, "max": 100.0},
    "pressure": {"min": 1.0, "max": 5.0},
    "flow_rate": {"min": 10.0, "max": 50.0},
}

# Known sensors and the column-name aliases that map to them (matched case-insensitively).
SENSOR_ALIASES = {
    "temperature": ("temperature", "temp"),
    "pressure": ("pressure", "press"),
    "flow_rate": ("flow_rate", "flow", "flowrate", "flow rate"),
}

# Column-name aliases for the timestamp field (matched case-insensitively).
TIMESTAMP_ALIASES = ("timestamp", "time", "date", "datetime")

# Gemini model used by the optional AI diagnosis layer (called over HTTPS via urllib).
GEMINI_MODEL = "gemini-2.0-flash"


def load_config(path=None):
    """Load and validate sensor thresholds from a JSON file.

    Returns a dict mapping each sensor to ``{"min": float, "max": float}``. When
    *path* is None, returns a copy of DEFAULT_THRESHOLDS. A config may define a subset
    of sensors; unlisted sensors fall back to defaults.

    Raises FileNotFoundError if the file does not exist, or ValueError (with a
    human-readable message) if the contents are invalid.
    """
    thresholds = {name: dict(rng) for name, rng in DEFAULT_THRESHOLDS.items()}
    if path is None:
        return thresholds

    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Config file is not valid JSON: {exc}")

    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON object mapping sensors to ranges.")

    for sensor, rng in data.items():
        if not isinstance(rng, dict) or "min" not in rng or "max" not in rng:
            raise ValueError(
                f"Threshold for '{sensor}' must include numeric 'min' and 'max'."
            )
        try:
            low = float(rng["min"])
            high = float(rng["max"])
        except (TypeError, ValueError):
            raise ValueError(f"Threshold values for '{sensor}' must be numbers.")
        if low > high:
            raise ValueError(
                f"Threshold for '{sensor}' has min ({low}) greater than max ({high})."
            )
        thresholds[sensor] = {"min": low, "max": high}

    return thresholds


def read_readings(csv_path):
    """Read sensor readings from a CSV file.

    Returns a tuple ``(readings, skipped)`` where *readings* is a list of dicts with
    keys ``timestamp`` (str or None), ``row`` (1-based int), and ``values`` (dict of
    sensor -> float), and *skipped* is a list of ``(row_number, reason)`` for rows that
    could not be parsed. Malformed rows are skipped rather than fatal.

    Raises FileNotFoundError if the file does not exist.
    """
    try:
        handle = open(csv_path, newline="", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    readings = []
    skipped = []
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return readings, skipped

        # Map actual column names to canonical sensor keys and find the timestamp column.
        colmap = {}
        timestamp_col = None
        for col in reader.fieldnames:
            key = (col or "").strip().lower()
            for sensor, aliases in SENSOR_ALIASES.items():
                if key in aliases:
                    colmap[col] = sensor
            if timestamp_col is None and key in TIMESTAMP_ALIASES:
                timestamp_col = col

        for index, raw in enumerate(reader, start=1):
            values = {}
            malformed = False
            for col, sensor in colmap.items():
                cell = (raw.get(col) or "").strip()
                if cell == "":
                    malformed = True
                    break
                try:
                    values[sensor] = float(cell)
                except ValueError:
                    malformed = True
                    break
            if malformed or not values:
                skipped.append((index, "missing or non-numeric sensor value"))
                continue
            timestamp = (raw.get(timestamp_col) or "").strip() if timestamp_col else ""
            readings.append(
                {
                    "timestamp": timestamp if timestamp else None,
                    "row": index,
                    "values": values,
                }
            )
    return readings, skipped


def check_reading(reading, thresholds):
    """Return a list of alert dicts for any out-of-range values in *reading*.

    Range bounds are inclusive: a value equal to min or max is in range. Each alert has
    keys ``sensor``, ``value``, ``limit`` ("min" or "max"), ``bound``, and ``timestamp``.
    When the reading has no timestamp, ``row N`` is used so no alert loses context.
    """
    alerts = []
    timestamp = reading.get("timestamp") or f"row {reading.get('row', '?')}"
    for sensor, value in reading.get("values", {}).items():
        rng = thresholds.get(sensor)
        if rng is None:
            continue
        if value < rng["min"]:
            alerts.append(
                {
                    "sensor": sensor,
                    "value": value,
                    "limit": "min",
                    "bound": rng["min"],
                    "timestamp": timestamp,
                }
            )
        elif value > rng["max"]:
            alerts.append(
                {
                    "sensor": sensor,
                    "value": value,
                    "limit": "max",
                    "bound": rng["max"],
                    "timestamp": timestamp,
                }
            )
    return alerts


def format_summary(total, alerts, skipped=0):
    """Return a human-readable summary report string.

    *total* is the number of readings evaluated, *alerts* is the list of alert dicts,
    and *skipped* is the count of malformed rows that were skipped.
    """
    triggered = sorted({alert["sensor"] for alert in alerts})
    lines = [
        "Summary",
        f"  Total readings : {total}",
        f"  Alerts         : {len(alerts)}",
    ]
    if triggered:
        lines.append(f"  Triggered      : {', '.join(triggered)}")
    else:
        lines.append("  Triggered      : none (no sensors triggered alerts)")
    lines.append(f"  Skipped rows   : {skipped}")
    return "\n".join(lines)


def diagnose_alert(alert, client=None):
    """Return a short plain-language diagnosis for an out-of-range *alert*, or None.

    *client* is an injectable callable taking a prompt string and returning a string;
    when None, the function calls the Google Gemini REST API over HTTPS using the
    standard-library ``urllib``, authenticated with the GEMINI_API_KEY environment
    variable. Returns None (never raises) when AI is unavailable (missing key) or the
    call fails, so a run always completes.
    """
    prompt = (
        f"A {alert['sensor']} sensor reading of {alert['value']} breached its "
        f"{alert['limit']} limit of {alert['bound']} at {alert['timestamp']}. "
        f"In one sentence, state the single most likely cause."
    )

    if client is not None:
        try:
            return client(prompt)
        except Exception:
            return None

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except Exception:
        return None


def _format_alert_line(alert):
    """Return the human-readable one-line representation of an alert."""
    direction = "exceeds max" if alert["limit"] == "max" else "below min"
    return (
        f"ALERT  {alert['sensor']}={alert['value']} {direction} "
        f"{alert['bound']}  @ {alert['timestamp']}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Monitor industrial sensor readings against safe thresholds."
    )
    parser.add_argument("input", help="Path to the CSV file of sensor readings.")
    parser.add_argument(
        "--config", help="Path to a config.json file of sensor thresholds."
    )
    ai_group = parser.add_mutually_exclusive_group()
    ai_group.add_argument(
        "--ai", action="store_true", help="Enable the optional Claude AI diagnosis layer."
    )
    ai_group.add_argument(
        "--no-ai", action="store_true", help="Disable AI diagnosis (this is the default)."
    )
    args = parser.parse_args()

    try:
        thresholds = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        sys.exit(f"Error: {exc}")

    try:
        readings, skipped = read_readings(args.input)
    except FileNotFoundError as exc:
        sys.exit(f"Error: {exc}")

    for row, reason in skipped:
        print(f"Warning: skipped row {row} ({reason}).", file=sys.stderr)

    alerts = []
    for reading in readings:
        alerts.extend(check_reading(reading, thresholds))

    ai_warned = False
    for alert in alerts:
        diagnosis = None
        if args.ai:
            diagnosis = diagnose_alert(alert)
            if diagnosis is None and not ai_warned:
                print(
                    "Warning: AI diagnosis unavailable (set GEMINI_API_KEY); "
                    "continuing without diagnoses.",
                    file=sys.stderr,
                )
                ai_warned = True
        line = _format_alert_line(alert)
        if diagnosis:
            line += f"\n       diagnosis: {diagnosis}"
        print(line)

    print()
    print(format_summary(len(readings), alerts, len(skipped)))
    return 0


if __name__ == "__main__":
    main()
