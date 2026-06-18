<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 → 3.0.0
Bump rationale: MAJOR. The five CS50P-specific principles (Python-Only & PEP 8 Style,
  Standard Library Only, Test Coverage in test_project.py, CLI via argparse,
  Human-Readable Error Messages) are removed and replaced by seven principles for an
  industrial chemical-process monitoring exhibition system (SentinelGUI). This is a
  backward-incompatible redefinition of the entire principle set and rescopes the
  project from a single-file CS50P submission to a modular exhibition application.

Modified principles:
  - I. Python-Only & PEP 8 Style                        → REMOVED (folded into VIII. Maintainable Python)
  - II. Standard Library Only                           → REMOVED (project now uses PySerial, Pandas, CustomTkinter, Matplotlib)
  - III. Test Coverage in test_project.py               → VII. Testability (broadened to hardware-independent logic tests)
  - IV. CLI via argparse                                → REMOVED (primary surface is GUI dashboard)
  - V. Human-Readable Error Messages                    → folded into IV. Safety & Fault Transparency
  - (new) I. Exhibition First
  - (new) II. Modular Architecture
  - (new) III. Offline Reliability (NON-NEGOTIABLE)
  - (new) IV. Safety & Fault Transparency
  - (new) V. Industrial User Experience
  - (new) VI. Real-Time Performance
  - (new) VII. Testability
  - (new) VIII. Maintainable Python

Added sections:
  - Core Principles I–VIII (industrial-monitoring-specific)
  - Technology Stack (backend, frontend, hardware, AI)
Removed sections:
  - CS50P-specific Project Constraints (single-file layout, no third-party deps)
Renamed/condensed sections:
  - Development Workflow & Quality Gates (rescoped from CS50P submission to exhibition readiness)
  - Governance (rescoped to emphasise exhibition impact over CS50P submission gates)

Templates requiring updates:
  - .specify/templates/plan-template.md ........ ✅ aligned (Constitution Check references
    constitution generically; no hardcoded principle names)
  - .specify/templates/spec-template.md ........ ✅ aligned (no constitution refs)
  - .specify/templates/tasks-template.md ....... ⚠ review (single-project / test-first ordering
    still consistent, but modular architecture may warrant module-grouped task layout in future
    revisions)
  - CLAUDE.md .................................. ✅ aligned (PHR/ADR guarantees retained;
    no principle names hardcoded)
  - README.md / specs/001-sensor-monitor ....... ⚠ review (existing CLI-only "Sensor Threshold
    Monitor" feature predates SentinelGUI scope; plan/spec/tasks may need realignment as the
    project evolves toward the full exhibition system)

Follow-up TODOs: None. All placeholders resolved.
-->

# SentinelGUI Exhibition Constitution

## Core Principles

### I. Exhibition First

Every feature MUST contribute directly to the value of the exhibition: a reliable, visually
impressive, and educational demonstration of chemical process monitoring, fault detection,
and AI-assisted diagnostics. Work that does not advance demo readiness, visual clarity, or
educational impact MUST be deferred or dropped.
Rationale: the system's purpose is to demonstrate chemical engineering, process safety,
instrumentation, digital twins, and AI-assisted operations to a live audience; scope decisions
are judged against that audience, not against generic software-engineering ideals.

### II. Modular Architecture

The system MUST be decomposed into independent, loosely coupled, individually replaceable
modules covering at minimum: Sensor Acquisition, Serial Communication, Data Processing,
Fault Detection, ReAct Agent, SentinelCLI Integration, Dashboard, and Data Logging. Modules
MUST communicate through explicit interfaces and MUST NOT reach into each other's internals.
Rationale: modular boundaries let the team swap mock sensors for real hardware (and back),
demonstrate one subsystem at a time during the exhibition, and recover quickly when a single
module fails on the show floor.

### III. Offline Reliability (NON-NEGOTIABLE)

The core system — Sensor Monitoring, Fault Detection, Alarm Generation, and Dashboard
Updates — MUST continue functioning with no internet access and no external service
availability. AI features (ReAct Agent, SentinelCLI diagnostics) are enhancements and MUST
be optional; failure or absence of any AI service MUST NOT degrade core monitoring,
alarms, or the dashboard.
Rationale: exhibition venues frequently have unreliable or absent connectivity; a system
that goes dark when Wi-Fi drops fails its single most important moment.

### IV. Safety & Fault Transparency

Every detected fault MUST be surfaced to the operator with, at minimum: Fault Name,
Severity Level, Probable Cause, and Recommended Action. The system MUST NOT silently
swallow exceptions, drop alarms, or mask failures behind generic UI states; error and
failure output MUST be expressed in clear, human-readable language.
Rationale: the exhibition demonstrates process safety; opaque or silent failures would
undermine the educational message and erode trust in the demo.

### V. Industrial User Experience

The dashboard MUST resemble a lightweight SCADA or Digital Twin interface and MUST provide
the following views: Live Process Dashboard, Process Mimic Diagram, Alarm Center, AI
Operator Panel, and Historical Trends. Layout, typography, and colour MUST follow
industrial-control conventions (e.g., red/amber/green alarm states, persistent status
banners) so that a process engineer recognises the interface immediately.
Rationale: visual familiarity is what makes the exhibition legible to industry visitors
and educational for students; an unfamiliar UI dilutes the demonstration.

### VI. Real-Time Performance

Sensor values MUST update at least once per second. Charts, alarm states, and AI
diagnostics MUST update without noticeable lag (target: visible refresh within ~1 second
of the underlying event). UI work that would block the event loop MUST run off the UI
thread.
Rationale: a monitoring dashboard that lags loses its credibility as a real-time system,
which is the central claim of the exhibition.

### VII. Testability

All business logic — fault-detection rules, alarm generation, diagnosis engines, and data
processing — MUST be testable independently of physical hardware. Modules that touch
sensors or serial ports MUST be designed so that they can be exercised against recorded
fixtures or in-memory fakes. Hardware-independent automated tests MUST exist for fault
detection and alarm generation and MUST pass before a demo build is released.
Rationale: hardware is unreliable and not always available; testable logic is the only way
to gain confidence before the exhibition without burning bench time.

### VIII. Maintainable Python

All Python code MUST be readable and maintainable: PEP 8 style, descriptive `snake_case`
identifiers, type hints on public module interfaces, and small focused functions. Secrets
and tokens MUST NOT be hardcoded; configuration belongs in `.env` or a documented config
file. Changes MUST be the smallest viable diff; unrelated refactoring is out of scope for a
given change.
Rationale: the team is small, the demo deadline is fixed, and the codebase is also a
teaching artifact; unmaintainable code costs both demo reliability and educational value.

## Technology Stack

The following stack is part of the constitution; substitutions require an ADR.

- **Backend**: Python, PySerial, Pandas
- **Frontend**: CustomTkinter, Matplotlib
- **Hardware**: Arduino Nano, DS18B20 (temperature), YF-S201 (flow), pressure sensor,
  relay module
- **AI (optional, never required for core operation)**: SentinelCLI, ReAct Agent

## Project Constraints

- The system MUST run end-to-end on a single demo machine without internet access.
- A Prompt History Record (PHR) MUST be recorded under `history/prompts/` for every user
  prompt, preserving the input verbatim and without truncation.
- Architecturally significant decisions MUST be surfaced as ADR suggestions and, on user
  consent, recorded under `history/adr/`. ADRs are never auto-created.
- AI features MUST be wrapped in failure-tolerant adapters: any exception, timeout, or
  missing dependency MUST degrade gracefully to the offline core (Principle III).
- Changes MUST cite affected modules explicitly; cross-module changes MUST justify the
  coupling against Principle II.

## Development Workflow & Quality Gates

- Hardware-independent automated tests for fault detection and alarm generation MUST pass
  before any demo build (Principle VII).
- A dry run of the dashboard with simulated sensor data MUST be performed before any
  exhibition or rehearsal, exercising at least one nominal scenario and one fault scenario
  per supported sensor.
- The offline mode MUST be verified by disconnecting all network interfaces and confirming
  that monitoring, alarms, and dashboard updates continue (Principle III).
- Every change MUST inline acceptance criteria as checkboxes or tests and MUST state
  explicit error paths and degradation behaviour.
- Code review MUST verify compliance with these principles; any deviation MUST be
  justified in writing (typically via an ADR) or the change MUST be corrected.

## Governance

This constitution supersedes all other development practices in this workspace. Amendments
MUST be documented in this file, accompanied by a version bump per the policy below, and
propagated to dependent templates (`plan-template.md`, `spec-template.md`,
`tasks-template.md`) and runtime guidance (`CLAUDE.md`) in the same change.

Versioning policy for this constitution:
- MAJOR: backward-incompatible governance changes or removal/redefinition of a principle.
- MINOR: a new principle or section is added, or existing guidance is materially expanded.
- PATCH: clarifications, wording, or typo fixes that do not change meaning.

When choosing between complexity and exhibition impact, prefer the simpler solution unless
the more complex solution provides significant demonstration value that cannot be achieved
otherwise; the added complexity MUST be justified against the simpler alternative that was
considered and rejected. Compliance review: all changes MUST verify adherence to these
principles. Use `CLAUDE.md` and the `.specify/` templates for runtime development guidance.

**Version**: 3.0.0 | **Ratified**: 2026-06-13 | **Last Amended**: 2026-06-17
