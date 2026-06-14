---
id: 0007
title: Implement Sensor Monitor MVP
stage: green
date: 2026-06-14
surface: agent
model: claude-opus-4-8[1m]
feature: 001-sensor-monitor
branch: 001-sensor-monitor
user: usman-shamim
command: /sp.implement
labels: [implement, cli, cs50p, pytest, ai-optional, green]
links:
  spec: specs/001-sensor-monitor/spec.md
  ticket: null
  adr: history/adr/0001-optional-ai-diagnosis-dependency.md
  pr: null
files:
 - project.py
 - test_project.py
 - config.json
 - sample_readings.csv
 - requirements.txt
 - README.md
 - .gitignore
 - specs/001-sensor-monitor/tasks.md
tests:
 - pytest test_project.py (7 passed)
 - python project.py sample_readings.csv --config config.json (exit 0)
 - python project.py does_not_exist.csv (exit 1, plain error)
 - pycodestyle --max-line-length=99 project.py test_project.py (clean)
---

## Prompt

/sp.implement

(no additional arguments)

## Response snapshot

Executed tasks.md T001–T023 across all 6 phases. Checklist gate PASS (requirements.md 16/16).
Environment: Python 3.14; pytest not present → installed pytest (dev/test runner, not a runtime
dep); pycodestyle installed for the PEP 8 gate. PowerShell prereq script unavailable → proceeded
agent-natively (git repo confirmed).

Built CS50P single-file structure (all functions in project.py per ADR-0001 / constitution):
- DEFAULT_THRESHOLDS + sensor/timestamp alias constants.
- load_config(path): JSON parse + validation (numeric, min<=max), subset merge over defaults,
  human-readable FileNotFoundError/ValueError.
- read_readings(csv_path): csv.DictReader, case-insensitive alias column matching, numeric
  coercion, skip+report malformed rows, blank timestamp -> None.
- check_reading(reading, thresholds): pure inclusive range check -> alert dicts; None timestamp
  -> "row N" fallback.
- format_summary(total, alerts, skipped): human-readable report; "none" message at zero alerts;
  distinct sorted triggered sensors.
- diagnose_alert(alert, client=None): lazy import anthropic, ANTHROPIC_API_KEY from env, injectable
  client seam, returns None (never raises) when AI unavailable.
- main(): argparse (positional input, --config, mutually-exclusive --ai/--no-ai default off),
  orchestration, stdout alerts+summary, stderr warnings, exit 0 / sys.exit on fatal.

test_project.py: one test per function (test_load_config, test_read_readings, test_check_reading,
test_format_summary, test_diagnose_alert with injected fake + raising client) + two main()
integration tests (happy path via capsys/monkeypatch; missing-input SystemExit != 0).

Verification:
- pytest: 7 passed in 0.13s.
- Sample run: 5 readings, 3 alerts (temperature/pressure/flow_rate), 1 skipped row, exit 0.
- Missing-file path: "Error: Input file not found: ..." to stderr, exit 1.
- pycodestyle (max-line 99): clean, exit 0.
Also added README.md (CS50P submission format), requirements.txt (core needs nothing; anthropic
optional; pytest dev-only), .gitignore (Python). Marked T001–T023 [X] in tasks.md. Default/--no-ai
path imports zero third-party packages (Constitution Principle II preserved).

## Outcome

- ✅ Impact: Feature 001-sensor-monitor implemented, tested, and verified end-to-end; CS50P-submittable, stdlib-only default path.
- 🧪 Tests: pytest 7/7 pass; CLI happy + error paths verified; PEP 8 clean.
- 📁 Files: project.py, test_project.py, config.json, sample_readings.csv, requirements.txt, README.md, .gitignore; tasks.md marked complete.
- 🔁 Next prompts: optional — record a Video Demo URL in README; live --ai smoke test with a real ANTHROPIC_API_KEY; commit the work.
- 🧠 Reflection: Implemented and verified in one pass; tests written alongside and confirmed green. The injectable-client seam kept the AI function testable without network/key.

## Evaluation notes (flywheel)

- Failure modes observed: pytest/pycodestyle absent (installed as dev tools); PowerShell prereq script unavailable (agent-native fallback). No code failures.
- Graders run and results (PASS/FAIL): pytest PASS (7/7); CLI exit-code contract PASS (0 success / 1 fatal); PEP 8 PASS; stdlib-only default-path check PASS.
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): add a live (network) --ai integration test gated behind an env-var marker so CI without a key still passes.
