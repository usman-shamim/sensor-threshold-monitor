# Contract: SentinelCLI Integration Bridge (Module 5)

SentinelGUI **reuses** the existing `project.py` (SentinelCLI) rather than reimplementing range
checks or AI. `project.py` is imported as a module; it is **not modified**.

## Reused SentinelCLI surface (from `project.py`)
```python
load_config(path=None) -> dict[str, {"min": float, "max": float}]
check_reading(reading, thresholds) -> list[alert dict]
diagnose_alert(alert, client=None) -> str | None     # Gemini over urllib; client is injectable
```
SentinelCLI alert dict shape:
```python
{"sensor": str, "value": float, "limit": "min"|"max", "bound": float, "timestamp": str}
```
SentinelCLI reading shape: `{"timestamp": str|None, "row": int, "values": {sensor: float}}`.

## 1. Threshold reuse (zone evaluation)
For each band (warning, critical), build a SentinelCLI-style thresholds dict
(`{sensor: {"min", "max"}}`) and call `check_reading(reading, band)`:
- breach against **critical** band → `critical` zone
- else breach against **warning** band → `warning` zone
- else → `normal`

This guarantees GUI and CLI agree on "in range" and reuses tested, inclusive-bound logic.

## 2. Alarm → CLI alert mapping
```python
def alarm_to_cli_alert(alarm) -> dict:
    return {
        "sensor":    alarm.sensor,
        "value":     alarm.value,
        "limit":     alarm.limit,      # "min" | "max"
        "bound":     alarm.bound,
        "timestamp": alarm.raised_at,
    }
```

## 3. On-demand AI diagnosis (off the UI thread)
```python
def ai_diagnose(alarm, timeout_s=10.0, client=None) -> str | None:
    alert = alarm_to_cli_alert(alarm)
    # run project.diagnose_alert(alert, client) in a worker thread; join with timeout_s
    # return the string, or None on timeout / unavailability (never raises)
```
- Triggered **only** when the user presses "Explain with AI" (FR-014); rule-based text is already
  shown.
- Runs in a worker thread; the UI `after()` loop collects the result. A ~10 s timeout (config
  `ai.timeout_s`) bounds it; on timeout/None the panel keeps the rule-based explanation and notes AI
  was unavailable (SC-006). The dashboard and E-stop never block.
- Credentials: `diagnose_alert` reads `GEMINI_API_KEY` from the environment (SentinelCLI behaviour).
  SentinelGUI hardcodes no key (FR-024). Missing key → `None` → graceful fallback.
- Testability: inject a fake `client` callable (as SentinelCLI's tests do) to test the bridge with
  no network — canned string → returned; raising client → `None`.

## 4. Failure isolation
Any import or call failure in the bridge degrades to rule-based-only operation with an on-screen
note; it never crashes the dashboard and never affects SentinelCLI's own CLI behaviour or tests.
