
<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 → 3.0.0
Bump rationale: MAJOR. The CS50P-specific principle set is removed entirely and replaced by
  principles appropriate to this project — a sensor threshold monitoring system comprising the
  SentinelCLI command-line tool and the SentinelGUI desktop exhibition dashboard. This is a
  backward-incompatible redefinition of the whole principle set. The previous Standard-Library-Only
  and CLI-only mandates (CS50P submission constraints) are removed; third-party dependencies and a
  GUI are now first-class. Test discipline, human-readable errors, offline-first reliability, and
  secrets hygiene are retained and generalized.

Modified principles:
  - I. Python-Only & PEP 8 Style            → I. Python-First & PEP 8 Style (CS50P rationale removed)
  - II. Standard Library Only               → REMOVED (replaced by VI. Secure Config & Reproducible
                                              Dependencies — third-party deps are now permitted/pinned)
  - III. Test Coverage in test_project.py   → III. Automated Test Coverage (pytest) — generalized
                                              from "every project.py function" to all testable logic
  - IV. CLI via argparse                    → REMOVED (the project ships both a CLI and a GUI)
  - V. Human-Readable Error Messages        → V. Human-Readable Errors (retained, broadened to GUI)
  - (new) II. Testable Core, Thin UI
  - (new) IV. Offline-First & Graceful Degradation
  - (new) VI. Secure Configuration & Reproducible Dependencies

Added sections:
  - Core Principles I–VI (project-specific)
Removed sections:
  - All CS50P-specific framing (submission layout mandate, "gradable on clean environment", etc.)

Templates requiring updates:
  - .specify/templates/plan-template.md ........ ✅ aligned (Constitution Check is generic:
    "Gates determined based on constitution file"; no principle names hardcoded)
  - .specify/templates/spec-template.md ........ ✅ aligned (no constitution references)
  - .specify/templates/tasks-template.md ....... ✅ aligned (test-first ordering and project
    structure remain consistent with Principles II & III)
  - CLAUDE.md .................................. ✅ aligned (PHR/ADR guarantees and policies retained)

Follow-up TODOs: None. All placeholders resolved.
-->

# Sensor Threshold Monitor Constitution

This constitution governs the Sensor Threshold Monitor project, which comprises **SentinelCLI** (a
Python command-line tool for reading sensor data and checking it against thresholds) and
**SentinelGUI** (a desktop, SCADA-style monitoring and fault-diagnosis dashboard built for live
exhibition and teaching use). All code in the repository — CLI, GUI, and shared logic — is bound by
the principles below unless a principle states a narrower scope.

## Core Principles

### I. Python-First & PEP 8 Style

All source code MUST be written in Python 3 and conform to PEP 8 style: 4-space indentation,
`snake_case` for functions and variables, descriptive names, and readable line lengths. Any
additional languages (e.g. microcontroller firmware) are permitted only where the platform requires
it and MUST be isolated from the Python codebase. Rationale: a single primary language and a shared
style keep the codebase consistent, reviewable, and approachable for contributors and demonstrators.

### II. Testable Core, Thin UI

Business logic MUST live in importable, UI-independent modules; user interfaces (CLI handlers and GUI
widgets) MUST stay thin and delegate to that logic. No non-trivial decision-making, threshold
evaluation, fault classification, or I/O orchestration may be embedded directly in a GUI widget or
print statement. Rationale: separating logic from presentation is what makes the system unit-testable
(Principle III) and lets the same core power both SentinelCLI and SentinelGUI.

### III. Automated Test Coverage (pytest) — NON-NEGOTIABLE

Every logic module MUST have `pytest` coverage exercising a normal case and at least one edge or
error case; the full suite MUST pass (`pytest` green) before a change is considered complete. Test
names SHOULD follow the `test_<function_or_behavior>` convention. Thin UI/view code containing no
business logic is exempt from unit testing and is validated manually against the relevant
quickstart/acceptance scenarios. Rationale: per-module tests are the project's primary correctness
guarantee, especially for fault-diagnosis logic that must behave predictably during a live demo.

### IV. Offline-First & Graceful Degradation

All core capabilities — data acquisition, threshold/alarm evaluation, rule-based diagnosis,
visualization, recording, and emergency shutdown — MUST function with no network connection. Any
optional external service (e.g. AI-assisted diagnosis) MUST run without blocking the core, MUST be
bounded by a timeout, and MUST fall back cleanly to offline behavior when unavailable, disabled, or
slow. Rationale: an exhibition or teaching environment cannot depend on connectivity or an API key;
the product must be compelling and safe even fully offline.

### V. Human-Readable Errors

All error and failure output MUST be expressed in clear, human-readable language that tells the user
what went wrong and how to proceed. Raw tracebacks, bare exception dumps, or cryptic codes MUST NOT
be the user-facing failure mode for anticipated errors: in the CLI, report plainly (e.g. to `stderr`
or via `sys.exit("message")`); in the GUI, surface a status banner or message rather than crashing.
Rationale: both a CLI tool and an exhibition dashboard are only usable if their failures are
understandable without reading the source.

### VI. Secure Configuration & Reproducible Dependencies

Secrets and credentials (e.g. AI API keys) MUST NOT be hardcoded or committed; they MUST come from
environment variables or untracked configuration (`.env`) and be documented. Third-party dependencies
are permitted and MUST be declared and version-pinned in a manifest (e.g. `requirements.txt`) so any
environment can be reproduced; prefer the smallest set of well-maintained libraries that satisfy the
requirement. Rationale: keeping secrets out of the repository and dependencies explicit makes the
project safe to share publicly and reliable to set up on demo hardware.

## Project Constraints

- The repository hosts two cooperating deliverables: the SentinelCLI tool and the SentinelGUI
  desktop application. Shared logic SHOULD be importable by both; the GUI MAY import and reuse CLI
  logic, and MUST NOT break the CLI when doing so.
- A Prompt History Record (PHR) MUST be recorded under `history/prompts/` for every user prompt,
  preserving the input verbatim and without truncation.
- Architecturally significant decisions MUST be surfaced as ADR suggestions and, on user consent,
  recorded under `history/adr/`. ADRs are never auto-created.
- Secrets and tokens MUST NOT be hardcoded; configuration belongs in environment/`.env` and
  documentation (Principle VI).
- Changes MUST be the smallest viable diff (YAGNI); unrelated refactoring is out of scope for a
  given change.

## Development Workflow & Quality Gates

- The `pytest` suite for all logic modules MUST be runnable and MUST pass before a change is
  considered complete (Principle III).
- Code MUST be checked against PEP 8 (e.g. a style check such as `flake8` or manual review) before a
  change is finalized (Principle I).
- Offline behavior MUST be verified for any change touching core capabilities: the affected feature
  is confirmed to work with networking disabled, and any optional online path falls back cleanly
  (Principle IV).
- Third-party dependencies introduced by a change MUST be pinned in the appropriate manifest and the
  run/install steps documented (Principle VI).
- Every change MUST inline its acceptance criteria as checkboxes or tests, and state explicit error
  paths and constraints.
- Code review MUST verify compliance with these principles; any deviation MUST be justified in
  writing (and, if significant, captured as an ADR) or the change MUST be corrected.

## Governance

This constitution supersedes all other development practices in this workspace. Amendments MUST be
documented in this file, accompanied by a version bump per the policy below, and propagated to
dependent templates (`plan-template.md`, `spec-template.md`, `tasks-template.md`) and runtime
guidance (`CLAUDE.md`) in the same change.

Versioning policy for this constitution:
- MAJOR: backward-incompatible governance changes or removal/redefinition of a principle
  (including a change to a principle's applicability scope).
- MINOR: a new principle or section is added, or existing guidance is materially expanded.
- PATCH: clarifications, wording, or typo fixes that do not change meaning.

Simplicity is the default: prefer the smallest viable change that satisfies the requirement, and
justify any added complexity against a simpler alternative that was considered and rejected for a
concrete reason. Compliance review: all changes MUST verify adherence to these principles. Use
`CLAUDE.md` and the `.specify/` templates for runtime development guidance.

**Version**: 3.0.0 | **Ratified**: 2026-06-13 | **Last Amended**: 2026-06-19
