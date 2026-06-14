# Implementation Plan: Sensor Threshold Monitor

**Branch**: `001-sensor-monitor` | **Date**: 2026-06-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-sensor-monitor/spec.md`

## Summary

A command-line tool that reads a CSV of industrial sensor readings (temperature, pressure, flow
rate), evaluates each value against configurable inclusive safe ranges loaded from a `config.json`
file, records a timestamped alert for every out-of-range value, and prints an end-of-run summary
(total readings, alert count, distinct triggered sensors). An **optional** AI diagnosis layer
(Claude API) can annotate alerts with plain-language likely-cause guidance; it is off by default
and the tool is fully functional with `--no-ai` using only the Python standard library.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Standard library only for the core (`argparse`, `csv`, `json`,
  `datetime`, `sys`); `anthropic` SDK is an **optional, lazy-imported** dependency used solely by
  the AI diagnosis layer.
**Storage**: Filesystem — CSV input, `config.json` thresholds; no database.
**Testing**: `pytest` in `test_project.py` at repository root (one test per custom function).
**Target Platform**: Cross-platform CLI (CS50P clean environment).
**Project Type**: Single project — CS50P final-project layout (`project.py` + `test_project.py`
  at repository root).
**Performance Goals**: Single-pass, in-memory processing of files up to ~1M rows in a few
  seconds; no real-time/streaming requirement.
**Constraints**: stdlib-only default path (no `pip install` required to run/grade); human-readable
  errors only (no tracebacks for anticipated failures); secrets (`ANTHROPIC_API_KEY`) via env var,
  never hardcoded; smallest viable diff.
**Scale/Scope**: ~6 custom functions in `project.py`; thousands to low-millions of CSV rows.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.specify/memory/constitution.md` v2.0.0:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Python-Only & PEP 8 Style | ✅ PASS | Python 3.11+, PEP 8, `snake_case`, argparse `--help`. |
| II. Standard Library Only | ⚠️ DEVIATION (justified) | Core is stdlib-only; optional `anthropic` is lazy-imported and never required for a run. See Complexity Tracking. |
| III. Test Coverage in test_project.py | ✅ PASS | Every custom function gets a `test_<name>` in `test_project.py`; pure functions designed for testability; AI layer isolated behind an injectable seam so tests need no network/key. |
| IV. CLI via argparse | ✅ PASS | Sole interface is an `argparse` CLI (`--config`, `--no-ai`/`--ai`, input path). |
| V. Human-Readable Error Messages | ✅ PASS | Anticipated errors → plain `stderr` messages / `sys.exit("...")`, no tracebacks. |

**Gate result**: PASS with one documented, justified deviation (Principle II). The deviation is
reconciled by making the AI layer optional and lazy-imported so the default run and the CS50P
autograder path remain 100% standard library. Recorded in Complexity Tracking; ADR recommended.

## Project Structure

### Documentation (this feature)

```text
specs/001-sensor-monitor/
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── cli.md           #   CLI argument contract
│   ├── config.schema.json  # config.json threshold schema
│   └── ai-diagnosis.md  #   optional AI layer contract
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /sp.specify)
└── tasks.md             # Phase 2 output (/sp.tasks — NOT created here)
```

### Source Code (repository root)

CS50P final-project layout — a single `project.py` with `main()` and required functions at the
top level (not nested), tests in `test_project.py`, both at the repository root:

```text
project.py               # main() + load_config, read_readings, check_reading,
                         #   format_summary, diagnose_alert (optional AI seam)
test_project.py          # pytest: one test_<function> per custom function
config.json              # default/sample thresholds (also serves as --config example)
requirements.txt         # documents OPTIONAL anthropic extra; empty/optional for core
sample_readings.csv      # sample input for quickstart and manual runs
README.md                # usage, per CS50P submission requirements
```

**Structure Decision**: Single-project CS50P layout is mandated by Principle (project constraints)
and the user's target. All logic lives in top-level functions of `project.py` so each is directly
importable and unit-testable from `test_project.py`. The AI layer is a single function
(`diagnose_alert`) guarded by a capability flag so the rest of the program never imports
`anthropic`.

## Complexity Tracking

> Filled because Constitution Check has one violation to justify.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| Optional `anthropic` third-party dependency (Principle II) | User explicitly requested an AI diagnosis layer that explains likely causes of alerts in plain language — value not achievable with stdlib. | Pure-stdlib heuristic "diagnosis" rejected because it cannot match LLM explanation quality the user asked for. Reconciled (not removed) by making AI **opt-in**, lazy-imported, and fully bypassed by `--no-ai`/default, so the CS50P-graded path stays stdlib-only. Dropping AI entirely rejected because it removes a requested feature. |

> Decision recorded in [ADR-0001: Optional AI Diagnosis Dependency](../../history/adr/0001-optional-ai-diagnosis-dependency.md).

## Phase 0 — Research

See [research.md](./research.md). Resolves: AI default on/off behavior, lazy-import + graceful
degradation pattern, config.json schema/validation approach, CSV column matching, timestamp
fallback, and testability seam for the AI layer.

## Phase 1 — Design & Contracts

- [data-model.md](./data-model.md) — Reading, Threshold/Config, Alert, Summary entities + rules.
- [contracts/cli.md](./contracts/cli.md) — argparse argument contract and exit codes.
- [contracts/config.schema.json](./contracts/config.schema.json) — threshold file schema.
- [contracts/ai-diagnosis.md](./contracts/ai-diagnosis.md) — optional AI layer interface + seam.
- [quickstart.md](./quickstart.md) — install (none required for core), run, and `--ai` usage.

**Agent context update**: `update-agent-context.ps1` not run — PowerShell runtime unavailable in
this environment. `CLAUDE.md` already reflects the relevant stack; no manual edit required.

## Post-Design Constitution Re-Check

After Phase 1 design, the gate status is unchanged: Principles I, III, IV, V remain PASS, and
Principle II remains a justified, documented deviation contained to the optional AI seam. No new
violations introduced by the design. **Proceed to `/sp.tasks`.**
