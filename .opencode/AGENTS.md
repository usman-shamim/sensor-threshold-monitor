# Sensor Threshold Monitor — Project Context

## Project
Two cooperating Python tools for industrial process monitoring:
- **SentinelCLI** (`project.py`) — CLI batch CSV monitor, stdlib only
- **SentinelGUI** (`sentinelgui/`) — desktop SCADA dashboard (customtkinter)

## Project Structure
- `project.py`, `test_project.py` — SentinelCLI
- `sentinelgui/` — SentinelGUI package
- `specs/<feature>/` — spec, plan, tasks, contracts, checklists
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts
- `config.json` — sensor thresholds
- `sample_readings.csv` — test data

## SDD Workflow
Spec-Driven Development: constitution → spec → clarify → plan → tasks → implement → test.

## Code Standards
- Python 3.12+, standard library preferred
- Pytest for tests (no pytest plugins)
- No hardcoded secrets; use env vars (GEMINI_API_KEY)
- Smallest viable diff; no unrelated refactoring
- Dataclasses for models; threading via queue.Queue for GUI

## PHR Recording
After completing requests, create a Prompt History Record:
- Stage: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general
- Path: `history/prompts/<stage>/<ID>-<slug>.<stage>.prompt.md`
- Include: title, date, user prompt, response, files changed, tests run

## ADR Suggestions
When an architecturally significant decision is detected (impactful, alternatives considered, cross-cutting), suggest documenting it. Wait for user consent.

## Agent skills

### Issue tracker

GitHub Issues tracked via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels using the default vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one CONTEXT.md at root + ADRs in docs/adr/. See `docs/agents/domain.md`.

## Key Contracts
- Serial protocol: CSV frames at 115200 baud, `CMD:STOP` / `ACK:STOP`
- SentinelGUI reuses `project.check_reading()` and `project.diagnose_alert()`
- GUI never modifies `project.py`
