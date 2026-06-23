---
id: 0013
title: SentinelGUI Task Breakdown
stage: tasks
date: 2026-06-19
surface: agent
model: claude-opus-4-8
feature: 002-sentinel-gui
branch: 002-sentinel-gui
user: usman-shamim
command: /sp.tasks
labels: [tasks, sentinel-gui, scada, tdd, customtkinter, pyserial, react-agent]
links:
  spec: specs/002-sentinel-gui/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-sentinel-gui/tasks.md
tests:
 - none (task-planning stage; defines test-first tasks T008/T010/T012/T014/T026/T029/T033/T037/T040/T043)
---

## Prompt

/sp.tasks

Break implementation into:

Phase 1
Project structure

Phase 2
Arduino serial communication

Phase 3
Sensor cards

Phase 4
Real-time charts

Phase 5
Process mimic diagram

Phase 6
Fault detection engine

Phase 7
Alarm system

Phase 8
CSV logger

Phase 9
ReAct agent

Phase 10
SentinelCLI integration

Phase 11
Emergency shutdown relay

Phase 12
Testing and exhibition mode

## Response snapshot

Generated `specs/002-sentinel-gui/tasks.md` — 51 tasks (T001–T051) across the user's requested
12-phase build order, mapped onto the SDD structure:

- **Phase 1 Setup (T001–T005)**: package skeleton, requirements.txt, gui_config.json, tests/conftest
  (adds repo root to sys.path so `import project` works), argparse `__main__`.
- **Phase 2 Foundational (T006–T018)** — BLOCKS all stories: models/dataclasses, ReadingWindow deque,
  acquisition (`parse_frame` + serial thread), process_engine, thresholds (reuses
  `project.check_reading` per band), baseline simulator, AppController (queue + `root.after(250)`),
  main-window shell, launcher wiring for both `--port` and `--simulate`.
- **Phases 3–12** = story-tagged increments: cards (US1), charts + mimic (US4), fault engine (US2),
  alarm system (US1, completes MVP), CSV logger (US5), ReAct agent (US2), SentinelCLI AI bridge (US7),
  emergency shutdown (US6), simulator injection + kiosk + full-suite validation (US3 + polish).

Key decisions baked in:
- Every task carries its spec **user-story label** (US1–US7) + exact file path, so the technical
  phase order stays traceable to the prioritized stories. Added a Story→Phase map table.
- **Tests included** (TDD): one `test_<module>.py` per headless module, written-to-fail before its
  implementation, per Constitution Principle III (adapted) and contracts/module-interfaces.md.
- **Critical path to MVP** called out: Phase 1 → 2 → 3 (cards) → 7 (alarms) ⇒ shippable US1.
- **Isolation guarantee** restated as tasks: nothing modifies `project.py`/`test_project.py`/
  `config.json`; T049 re-confirms `test_project.py` green. A baseline simulator lands in Phase 2 so
  every later phase is runnable headless (plan's "--simulate green before hardware" gate).
- Dependencies, parallel opportunities ([P] widgets/tests on distinct files), and MVP/incremental
  strategy sections completed.

## Outcome

- ✅ Impact: Feature 002-sentinel-gui has an executable, dependency-ordered, test-first task list;
  ready for `/sp.implement` (or `/sp.analyze` for a cross-artifact consistency check first).
- 🧪 Tests: N/A this stage; 10 module test tasks defined as the red gate before each implementation.
- 📁 Files: specs/002-sentinel-gui/tasks.md (created, 51 tasks / 12 phases).
- 🔁 Next prompts: `/sp.adr sentinelgui-stack-and-constitution-deviation` (still recommended from the
  plan), then `/sp.implement` to execute starting at T001, or `/sp.analyze` to validate
  spec↔plan↔tasks alignment.
- 🧠 Reflection: Reconciled the user's technical 12-phase ordering with the template's story-based
  organization by keeping the 12 phase headings verbatim and labelling every task with the story it
  serves — honouring explicit user input without losing spec traceability.

## Evaluation notes (flywheel)

- Failure modes observed: none. The user's phase list omitted a standalone "simulator" phase, which
  conflicts with the plan's gate that the `--simulate` path be green before hardware work; resolved by
  placing a baseline simulator in Foundational (Phase 2) and the fault-injection/kiosk work in
  Phase 12, preserving the user's 12 headings.
- Graders run and results (PASS/FAIL): Checklist format — PASS (every task has checkbox, ID, file
  path, and story label where applicable). Story coverage — PASS (US1–US7 all mapped to phases).
  Test-first ordering — PASS (test task precedes each headless implementation).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): during `/sp.implement`, enforce the red→green gate by
  running each new `test_<module>.py` and confirming failure before writing the module.
