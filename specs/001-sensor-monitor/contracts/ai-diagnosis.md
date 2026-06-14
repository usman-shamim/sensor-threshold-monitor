# Contract: Optional AI Diagnosis Layer

The AI layer annotates an alert with a short, plain-language likely-cause explanation using the
Google Gemini API. It is **optional, opt-in, and isolated** so the rest of the tool never depends
on it, and it is called over HTTPS with the standard-library `urllib` — no third-party package.

## Function interface

```python
def diagnose_alert(alert, client=None):
    """Return a short plain-language diagnosis string for an out-of-range alert.

    alert:  dict with keys sensor, value, limit, bound, timestamp (see data-model.md).
    client: an injectable object/callable that performs the model call. When None,
            the function calls the Gemini REST API over HTTPS via urllib, authenticated
            with the GEMINI_API_KEY environment variable.

    Returns a diagnosis string, or None if AI is unavailable (missing key or API error).
    Never raises for these anticipated conditions.
    """
```

## Activation rules

| Condition | Behavior |
|-----------|----------|
| `--ai` not set (default / `--no-ai`) | `diagnose_alert` is not called. |
| `--ai` set, key present | Each alert annotated with `diagnosis`. |
| `--ai` set, `GEMINI_API_KEY` missing | Warn to `stderr` once, continue without diagnoses (exit 0). |
| API call error / timeout | Warn to `stderr`, that alert's `diagnosis` stays `None`, run continues. |

## Constraints

- **Standard library only**: the Gemini call uses `urllib.request` over HTTPS; no third-party
  package is imported on any path (Constitution Principle II is fully satisfied — no deviation).
- **No secrets in code**: the API key is read from the `GEMINI_API_KEY` environment variable;
  never hardcoded (Constitution + default policies).
- **Model**: default to a current Gemini model id (e.g. `gemini-2.0-flash` for low latency/cost),
  defined as the `GEMINI_MODEL` constant; configurable later if needed.
- **Testability seam**: tests pass a fake `client` (a callable returning a canned string) so unit
  tests assert prompt-building/return handling with no network and no key (Principle III).
- **Graceful degradation**: anticipated failures return `None` and emit a human-readable warning;
  they never crash the run (Principle V, FR-009/FR-010).

## Example (illustrative) test seam

```python
def test_diagnose_alert():
    fake = lambda prompt: "Temperature likely exceeded max due to coolant flow loss."
    alert = {"sensor": "temperature", "value": 130, "limit": "max",
             "bound": 100, "timestamp": "2026-06-14T10:00:00"}
    result = diagnose_alert(alert, client=fake)
    assert isinstance(result, str) and "temperature" in result.lower()
```
