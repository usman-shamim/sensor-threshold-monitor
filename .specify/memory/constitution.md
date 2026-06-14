<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 2.0.0
Bump rationale: MAJOR. The seven generic SDD principles (Library-First, CLI Interface,
  Test-First, Integration Testing, Observability, Versioning & Breaking Changes,
  Simplicity) are removed and replaced by five CS50P-specific principles. This is a
  backward-incompatible redefinition of the entire principle set.

Modified principles:
  - I. Library-First                  → REMOVED (replaced by Standard-Library-Only)
  - II. CLI Interface                 → I. CLI via argparse (narrowed to argparse)
  - III. Test-First (NON-NEGOTIABLE)  → III. Test Coverage in test_project.py (reframed
                                         to CS50P pytest-per-function requirement)
  - IV. Integration Testing           → REMOVED (out of scope for single-file CS50P project)
  - V. Observability                  → V. Human-Readable Error Messages (reframed)
  - VI. Versioning & Breaking Changes → REMOVED (not applicable to CS50P submission)
  - VII. Simplicity                   → folded into Governance guidance
  - (new) I. Python-Only & PEP 8 Style
  - (new) II. Standard Library Only (No Third-Party Dependencies)

Added sections:
  - Core Principles I–V (CS50P-specific)
Removed sections:
  - Spec-Driven Development Constraints (replaced by Project Constraints, slimmed)
Renamed/condensed sections:
  - Development Workflow & Quality Gates (rescoped to CS50P submission gates)

Templates requiring updates:
  - .specify/templates/plan-template.md ........ ✅ aligned (Constitution Check references
    the constitution generically; no principle names hardcoded)
  - .specify/templates/spec-template.md ........ ✅ aligned (no constitution refs)
  - .specify/templates/tasks-template.md ....... ✅ aligned (test-first ordering and
    single-project layout consistent with Principles III & I)
  - CLAUDE.md .................................. ✅ aligned (PHR/ADR guarantees retained
    under Project Constraints)

Follow-up TODOs: None. All placeholders resolved.
-->

# CS50P Final Project Constitution

## Core Principles

### I. Python-Only & PEP 8 Style

All source code MUST be written in Python 3. Code MUST conform to PEP 8 style: 4-space
indentation, `snake_case` for functions and variables, descriptive names, and lines kept to
a readable length. No other programming language may be introduced into the project.
Rationale: CS50P is a Python course; a single language and a shared style keep the codebase
consistent, gradable, and idiomatic for review.

### II. Standard Library Only (No Third-Party Dependencies)

The project MUST use only the Python standard library. Installing or importing third-party
packages (anything requiring `pip install`) is PROHIBITED. If a capability is not available
in the standard library, the project MUST either implement it directly or narrow its scope.
Rationale: CS50P requires submissions to run without external dependencies, ensuring the
project is reproducible and gradable on the course's clean environment.

### III. Test Coverage in test_project.py (NON-NEGOTIABLE)

Every custom function defined in `project.py` (other than `main`) MUST have at least one
corresponding `pytest` test in `test_project.py`. Test function names MUST follow the
`test_<function_name>` convention. Tests MUST cover normal cases and at least one edge or
error case, and the full suite MUST pass (`pytest` green) before the project is considered
complete. Rationale: per-function tests are a hard CS50P requirement and are the project's
primary correctness guarantee for an environment without integration infrastructure.

### IV. CLI via argparse

The project MUST present a command-line interface as its only user interface, and command-line
arguments MUST be parsed with the standard-library `argparse` module. Manual `sys.argv`
parsing for user-facing options, interactive-only flows with no CLI, or any GUI/web interface
are out of scope. Rationale: a uniform `argparse` CLI makes the program scriptable, gives
users automatic `--help` output, and matches CS50P's command-line orientation.

### V. Human-Readable Error Messages

All error and failure output MUST be expressed in clear, human-readable language that tells
the user what went wrong and how to correct it. Raw tracebacks, bare exception dumps, or
cryptic codes MUST NOT be the user-facing failure mode for anticipated errors; invalid input
MUST be caught and reported plainly (e.g., to `stderr` or via `sys.exit("message")`).
Rationale: a CLI tool is only usable if its failures are understandable without reading the
source.

## Project Constraints

- The project MUST follow the CS50P final project layout: a `project.py` containing `main()`
  and the required custom functions at the same indentation level (not nested), with tests in
  `test_project.py` at the project root.
- A Prompt History Record (PHR) MUST be recorded under `history/prompts/` for every user
  prompt, preserving the input verbatim and without truncation.
- Architecturally significant decisions MUST be surfaced as ADR suggestions and, on user
  consent, recorded under `history/adr/`. ADRs are never auto-created.
- Secrets and tokens MUST NOT be hardcoded; configuration belongs in `.env` and documentation.
- Changes MUST be the smallest viable diff (YAGNI); unrelated refactoring is out of scope for a
  given change.

## Development Workflow & Quality Gates

- Tests in `test_project.py` MUST be runnable and MUST pass via `pytest` before a change is
  considered complete (Principle III).
- Code MUST be checked against PEP 8 (e.g., a style check such as `style50`, `flake8`, or
  manual review) before submission (Principle I).
- The project MUST be confirmed to run end-to-end from the command line using only the standard
  library, with no `pip install` step required (Principles II & IV).
- Every change MUST inline its acceptance criteria as checkboxes or tests, and state explicit
  error paths and constraints.
- Code review MUST verify compliance with these principles; any deviation MUST be justified in
  writing or the change MUST be corrected.

## Governance

This constitution supersedes all other development practices in this workspace. Amendments
MUST be documented in this file, accompanied by a version bump per the policy below, and
propagated to dependent templates (`plan-template.md`, `spec-template.md`,
`tasks-template.md`) and runtime guidance (`CLAUDE.md`) in the same change.

Versioning policy for this constitution:
- MAJOR: backward-incompatible governance changes or removal/redefinition of a principle.
- MINOR: a new principle or section is added, or existing guidance is materially expanded.
- PATCH: clarifications, wording, or typo fixes that do not change meaning.

Simplicity is the default: prefer the smallest viable change that satisfies the requirement,
and justify any added complexity against a simpler alternative that was considered and
rejected for a concrete reason. Compliance review: all changes MUST verify adherence to these
principles. Use `CLAUDE.md` and the `.specify/` templates for runtime development guidance.

**Version**: 2.0.0 | **Ratified**: 2026-06-13 | **Last Amended**: 2026-06-14
