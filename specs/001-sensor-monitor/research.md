# Phase 0 Research: Sensor Threshold Monitor

All unknowns from the Technical Context are resolved below. Format: Decision / Rationale /
Alternatives considered.

## R1. AI layer: default state and CLI flag semantics

- **Decision**: The AI diagnosis layer is **OFF by default**. `--ai` enables it; `--no-ai` is
  accepted and explicitly disables it (also the default). When `--ai` is set but no
  `ANTHROPIC_API_KEY` env var is present or the `anthropic` package is not installed, the tool
  prints a plain-language warning and continues without AI (non-fatal).
- **Rationale**: Keeps the default and CS50P autograder path 100% standard library (Constitution
  Principle II), requires no secrets to run, and still honors the user's `--no-ai` requirement.
  Graceful degradation satisfies Principle V (human-readable errors) and FR-010 (a run still
  completes).
- **Alternatives considered**: AI on-by-default with `--no-ai` to disable — rejected because it
  would make a clean run depend on a third-party package + API key, breaking gradeability. Hard
  error when `--ai` lacks a key — rejected as user-hostile; warning + continue is friendlier.

## R2. Lazy import + testability seam for `anthropic`

- **Decision**: `import anthropic` happens **inside** `diagnose_alert(...)` (or a thin client
  factory it calls), never at module top level. `diagnose_alert` accepts an injectable
  `client`/callable parameter (default `None`) so tests pass a fake and never hit the network or
  require a key.
- **Rationale**: Top-level import would force the dependency on every run and break stdlib-only
  execution. Dependency injection lets Principle III hold (every function unit-tested) without
  network access.
- **Alternatives considered**: `try/except ImportError` at top of module — still couples import to
  load and complicates the global namespace; rejected in favor of function-local import. Mocking
  via `unittest.mock.patch` only — works but injection keeps the function pure and the test
  simpler.

## R3. Threshold configuration format and validation

- **Decision**: Thresholds live in a JSON file passed via `--config PATH`, parsed with the stdlib
  `json` module. Schema: a top-level object keyed by sensor name (`temperature`, `pressure`,
  `flow_rate`), each mapping to `{"min": <number>, "max": <number>}`. On load, validate that
  required keys exist, values are numeric, and `min <= max`; on failure raise a clear message and
  exit non-zero. If `--config` is omitted, use built-in documented defaults.
- **Rationale**: JSON is stdlib-native, human-editable, and matches the user's `config.json`
  requirement. Explicit validation supports Principle V and FR-004/FR-003.
- **Alternatives considered**: INI via `configparser` — values are strings needing manual casting;
  JSON is cleaner for numeric ranges. Per-sensor CLI flags only — clumsier for three ranges and
  not persistable; JSON file chosen, CLI override deferred (not in scope).

## R4. CSV parsing and column matching

- **Decision**: Use `csv.DictReader` (stdlib). Match sensor columns case-insensitively by known
  names with light aliasing: `temperature`/`temp`, `pressure`, `flow_rate`/`flow`/`flowrate`. A
  `timestamp`/`time`/`date` column supplies the alert timestamp. Unknown extra columns are
  ignored. Rows with missing/non-numeric sensor values are reported (row number) and skipped, and
  processing continues (FR-007).
- **Rationale**: `DictReader` makes column access order-independent and readable; alias matching
  tolerates real-world headers without third-party schema libraries.
- **Alternatives considered**: Fixed positional columns with `csv.reader` — brittle to column
  reordering; rejected. `pandas` — third-party, prohibited by Principle II.

## R5. Timestamp source and fallback

- **Decision**: The alert timestamp is the reading's own timestamp string from the CSV, used
  verbatim. If absent/blank, fall back to `row <N>` (1-based data row index) so no alert is lost
  (FR-005, edge case). `datetime` is used only if/where a parsed/normalized time is needed for
  display; raw passthrough is the default to avoid format guessing.
- **Rationale**: Avoids brittle datetime-format assumptions while keeping alerts actionable.
- **Alternatives considered**: Generating processing-time timestamps — misrepresents when the
  reading occurred; rejected. Strict datetime parsing with rejection on unknown format — too
  fragile for arbitrary CSVs.

## R6. Function decomposition for CS50P + testability

- **Decision**: Top-level functions in `project.py`: `main()`, `load_config(path)`,
  `read_readings(csv_path)`, `check_reading(reading, thresholds)`, `format_summary(total, alerts)`,
  and `diagnose_alert(alert, client=None)`. Pure functions (`load_config` parsing,
  `check_reading`, `format_summary`) take inputs and return values with no I/O side effects beyond
  what is necessary, enabling direct assertions in `test_project.py`.
- **Rationale**: Satisfies CS50P (`main` + ≥3 functions at top level) and Principle III (one
  `test_<function>` each). Separating evaluation (`check_reading`) from I/O keeps the core logic
  trivially testable.
- **Alternatives considered**: A single monolithic `main()` — untestable per-function, violates
  Principle III and CS50P structure; rejected. Class-based design — unnecessary complexity for the
  scope (Governance: simplicity default); rejected.

## R7. Exit codes and output streams

- **Decision**: Alerts and the summary go to `stdout`; warnings and anticipated errors go to
  `stderr`. Exit `0` on a completed run (including zero alerts or rows skipped); exit non-zero
  (e.g., `1`) only when the run cannot be performed (missing/unreadable input, invalid config).
- **Rationale**: Standard CLI convention; supports scripting and satisfies FR-009/FR-010.
- **Alternatives considered**: Non-zero exit when alerts exist — conflates "tool worked" with
  "process out of range"; rejected to keep tool success orthogonal to data findings. (Could be a
  future `--strict` flag; out of scope.)

## Open items

None. All Technical Context unknowns resolved; ready for Phase 1 design.
