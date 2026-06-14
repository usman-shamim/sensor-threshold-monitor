---
description: "Task list for Sensor Threshold Monitor"
---

# Tasks: Sensor Threshold Monitor

**Input**: Design documents from `/specs/001-sensor-monitor/`
**Prerequisites**: plan.md (required), spec.md (user stories), research.md, data-model.md, contracts/

**Tests**: REQUIRED. Tests are explicitly requested (constitution Principle III is NON-NEGOTIABLE
test-first: every custom function in `project.py` has a `test_<function>` in `test_project.py`,
written and confirmed FAILING before implementation).

**Structure decision**: CS50P single-project layout. ALL functions live in `project.py` at the
repo root; tests in `test_project.py` at the repo root. The user's seven groupings
(reader/analyzer/reporter/agent/CLI) are LOGICAL task groups inside `project.py`, not separate
files. Build order (per user constraints): core logic → CLI → AI; the `--no-ai`/default path MUST
be fully working before any AI task begins.

**Two-file limit**: every task edits at most one code file (`project.py` OR `test_project.py`) or a
single standalone data/doc file, satisfying the "no task touches more than 2 files" constraint.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: US1 (out-of-range detection, P1), US2 (configurable thresholds, P2),
  US3 (summary report, P3). Setup/Foundational/AI/Polish carry no story label.

## Path Conventions

- Repository root: `project.py`, `test_project.py`, `config.json`, `sample_readings.csv`,
  `requirements.txt`, `README.md`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and sample data.

- [X] T001 Create `requirements.txt` at repo root documenting that the core needs NO third-party
  packages and `anthropic` is an OPTIONAL extra (for `--ai` only), with a comment to that effect.
- [X] T002 [P] Create `sample_readings.csv` at repo root: header `timestamp,temperature,pressure,flow_rate`
  plus rows mixing in-range and out-of-range values for each sensor, one malformed row, and one
  row with a blank timestamp.
- [X] T003 [P] Create `config.json` at repo root with the default ranges from data-model.md
  (temperature 0–100, pressure 1.0–5.0, flow_rate 10–50).
- [X] T004 Create `project.py` skeleton at repo root: module docstring, function stubs
  (`load_config`, `read_readings`, `check_reading`, `format_summary`, `diagnose_alert`, `main`),
  and `if __name__ == "__main__": main()`.
- [X] T005 [P] Create `test_project.py` skeleton at repo root: module docstring and
  `from project import load_config, read_readings, check_reading, format_summary, diagnose_alert`.

**Checkpoint**: Files exist and `pytest test_project.py` runs (collecting, even if empty).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared constants every later function depends on.

**⚠️ CRITICAL**: Must complete before Phase 3.

- [X] T006 Add `DEFAULT_THRESHOLDS` constant and sensor-name/alias constants to `project.py`
  (used by `load_config`, `read_readings`, and `check_reading`).

**Checkpoint**: Shared constants available; core function work can begin.

---

## Phase 3: Core Logic — `--no-ai` MVP (US1 + US2 + US3) 🎯 MVP

**Goal**: Pure-stdlib detection, configurable thresholds, and summary — no CLI, no AI yet.

**Independent Test**: Call the functions directly from `test_project.py` with crafted inputs and
assert alerts/summary; all assertions pass with zero third-party imports.

> Test-first: write the test, run it, confirm it FAILS, then implement to green.

### Reader group

- [X] T007 [US2] Write FAILING `test_load_config` in `test_project.py`: valid file, missing-key
  fallback to defaults, `min > max` → error, missing file → error.
- [X] T008 [US2] Implement `load_config(path)` in `project.py`: parse JSON, validate numeric
  `min<=max`, merge over `DEFAULT_THRESHOLDS`, raise human-readable error on invalid/missing.
- [X] T009 [US1] Write FAILING `test_read_readings` in `test_project.py`: well-formed rows parsed,
  malformed/non-numeric row skipped (and reported), blank timestamp → `row N` fallback, empty file
  → no readings.
- [X] T010 [US1] Implement `read_readings(csv_path)` in `project.py`: `csv.DictReader`,
  case-insensitive alias column matching, numeric coercion, skip+collect malformed rows, return
  readings (+ skipped count).

### Analyzer group

- [X] T011 [US1] Write FAILING `test_check_reading` in `test_project.py`: all in-range → no alerts,
  below `min` → alert(limit=min), above `max` → alert(limit=max), boundary equals bound → in-range,
  multiple breaches in one reading → multiple alerts.
- [X] T012 [US1] Implement `check_reading(reading, thresholds)` in `project.py`: pure inclusive
  range check returning a list of alert dicts (sensor, value, limit, bound, timestamp).

### Reporter group

- [X] T013 [US3] Write FAILING `test_format_summary` in `test_project.py`: zero alerts → "no
  sensors triggered" message, correct total/alert counts, distinct triggered sensors sorted.
- [X] T014 [US3] Implement `format_summary(total, alerts, skipped=0)` in `project.py`: return a
  human-readable summary string (total readings, alert count, distinct triggered sensors, skipped).

**Checkpoint**: Core logic fully tested in isolation (US1, US2, US3 satisfied at function level).

---

## Phase 4: CLI Wiring — `--no-ai` fully working (US1/US2/US3 integration)

**Goal**: Make the tool runnable end-to-end on the standard-library path. This completes the MVP.

- [X] T015 [US1] Implement `main()` in `project.py`: `argparse` with positional `INPUT`,
  `--config PATH`, and a mutually-exclusive `--ai`/`--no-ai` group defaulting to no-AI; orchestrate
  `load_config` → `read_readings` → `check_reading` → `format_summary`; print alerts + summary to
  stdout, errors/warnings to stderr; exit 0 on completion, non-zero on unreadable input/invalid
  config. (Do NOT import or call the AI layer yet.)

**Checkpoint**: `python project.py sample_readings.csv --config config.json` produces alerts +
summary with no third-party packages. **MVP COMPLETE — `--no-ai` path fully working.**

---

## Phase 5: Optional AI Diagnosis Layer (AI last — only after Phase 4 is green)

**Goal**: Add opt-in Claude diagnoses without touching the stdlib default path.

**⚠️ Gate**: Do not start until the `--no-ai` MVP (Phase 4) is verified working.

- [X] T016 Write FAILING `test_diagnose_alert` in `test_project.py`: inject a fake `client`
  callable returning a canned string → returns that string; fake client raising → returns `None`
  (no exception). No network, no API key.
- [X] T017 Implement `diagnose_alert(alert, client=None)` in `project.py`: lazy `import anthropic`
  inside the function, read `ANTHROPIC_API_KEY` from env (never hardcoded), use injected `client`
  when provided, return diagnosis string or `None` on any anticipated failure.
- [X] T018 Wire `--ai` into `main()` in `project.py`: when `--ai` is active, call `diagnose_alert`
  per alert and include the diagnosis in output; if package/key missing, warn once to stderr and
  continue (exit 0).

**Checkpoint**: `--ai` annotates alerts when available; default/`--no-ai` behavior unchanged.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T019 [P] Add integration tests in `test_project.py` for `main()` via `capsys`/`tmp_path`:
  happy path (exit 0, summary printed), missing input file (non-zero exit, plain message), invalid
  config (non-zero exit).
- [X] T020 [P] Write `README.md` at repo root: purpose, usage, `--config`, `--ai`/`--no-ai`,
  how to run, how to run `pytest` (CS50P submission requirement).
- [X] T021 [P] PEP 8 / style pass over `project.py` (run a style check or manual review;
  Constitution Principle I).
- [X] T022 [P] PEP 8 / style pass over `test_project.py` (Constitution Principle I).
- [X] T023 Validate `quickstart.md` end-to-end: run the sample, confirm alerts/summary match and
  `pytest test_project.py` is fully green.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Phase 1; BLOCKS Phase 3.
- **Core Logic (Phase 3)**: depends on Phase 2.
- **CLI (Phase 4)**: depends on ALL Phase 3 functions (calls each).
- **AI (Phase 5)**: HARD GATE — depends on Phase 4 verified working.
- **Polish (Phase 6)**: depends on the features it covers (T019 after Phase 4; T021/T022 anytime
  after code exists; T023 after Phase 5 or after Phase 4 for the `--no-ai` subset).

### Within each function group

- The `test_<fn>` task MUST be written and FAILING before its implementation task
  (e.g., T007 before T008, T009 before T010, T011 before T012, T013 before T014, T016 before T017).

### Parallel opportunities

- **Phase 1**: T002, T003, T005 are `[P]` (distinct files). T001/T004 edit their own files too but
  keep them sequential-friendly as anchors.
- **Within Phase 3**: function groups all edit the SAME two files (`project.py`,
  `test_project.py`), so they are **NOT** parallel with each other — execute sequentially
  (reader → analyzer → reporter) to avoid edit conflicts.
- **Phase 6**: T019 (test file), T020 (README), T021/T022 (style, read-only-ish) can run `[P]`.

```text
# Phase 1 parallel batch (distinct files):
Task T002: sample_readings.csv
Task T003: config.json
Task T005: test_project.py skeleton
```

---

## Implementation Strategy

### MVP first (Phases 1–4)

1. Setup + Foundational.
2. Core logic test-first (US1 detection, US2 config, US3 summary) — all unit-tested.
3. CLI wiring → `python project.py ... --no-ai` fully working.
4. **STOP and VALIDATE**: this is a complete, CS50P-submittable, stdlib-only tool.

### Incremental delivery

- After MVP, add Phase 5 (optional AI) only once `--no-ai` is verified — keeps the graded path
  stdlib-only at all times.
- Finish with Phase 6 polish (integration tests, README, style, quickstart validation).

---

## Notes

- Every tested function is defined in `project.py` (CS50P + Constitution Principle III).
- Each task edits ≤ 2 files (in practice one code file or one data/doc file).
- Verify each test FAILS before implementing (test-first).
- `anthropic` is lazy-imported only in `diagnose_alert`; the default path imports no third-party
  packages (Constitution Principle II / documented deviation).
- Commit after each task or test→impl pair.
