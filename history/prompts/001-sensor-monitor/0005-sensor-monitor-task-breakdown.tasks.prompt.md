---
id: 0005
title: Sensor Monitor Task Breakdown
stage: tasks
date: 2026-06-14
surface: agent
model: claude-opus-4-8[1m]
feature: 001-sensor-monitor
branch: 001-sensor-monitor
user: usman-shamim
command: /sp.tasks
labels: [tasks, cs50p, test-first, cli, ai-optional]
links:
  spec: specs/001-sensor-monitor/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-sensor-monitor/tasks.md
tests:
 - none
---

## Prompt

/sp.tasks

Break the plan into atomic, testable tasks following CS50P structure.

Constraints:
- Each task must be independently completable and testable
- Every function must have a corresponding test in test_project.py
- Tasks should follow this order: core logic first, CLI second, AI layer last
- The --no-ai mode must be fully working before any AI tasks begin
- No task should touch more than 2 files at once

Task grouping I expect:
1. Project setup (folder structure, requirements.txt, sample data files)
2. reader.py — CSV parsing and config.json loading
3. analyzer.py — threshold checking logic (pure Python, no AI)
4. reporter.py — summary report formatting
5. agent.py — Claude API diagnosis (optional layer)
6. project.py — CLI entry point wiring everything together
7. test_project.py — pytest tests for all functions

## Response snapshot

Surfaced a structural conflict before generating: the user's separate-module grouping
(reader.py/analyzer.py/reporter.py/agent.py) contradicts CS50P (tested functions must be defined
in project.py), Constitution Principle III, and the approved plan. Asked via AskUserQuestion; user
chose "All in project.py" — the seven groupings become LOGICAL task groups inside project.py.

Generated `specs/001-sensor-monitor/tasks.md`: 23 tasks (T001–T023) across 6 phases, strict
checklist format with story labels (US1 detection / US2 config / US3 summary).
- Phase 1 Setup (T001–T005): requirements.txt, sample_readings.csv, config.json, project.py +
  test_project.py skeletons.
- Phase 2 Foundational (T006): DEFAULT_THRESHOLDS + alias constants.
- Phase 3 Core Logic / MVP (T007–T014): test-first pairs for load_config, read_readings,
  check_reading, format_summary.
- Phase 4 CLI (T015): argparse main(), mutually-exclusive --ai/--no-ai (default no-ai), wiring →
  --no-ai MVP fully working.
- Phase 5 Optional AI (T016–T018): GATED behind Phase 4; test_diagnose_alert (injected fake
  client), lazy-imported diagnose_alert, --ai wiring with graceful degradation.
- Phase 6 Polish (T019–T023): main() integration tests (capsys/tmp_path), README, PEP 8 passes,
  quickstart validation.
Honored all constraints: test-first ordering (test before impl per function), each task ≤2 files
(one code or one data/doc file), AI strictly last, --no-ai working before AI. Noted that Phase 3
groups edit the same two files so they are NOT parallel; real [P] is limited to distinct data/doc
files.

## Outcome

- ✅ Impact: Executable, CS50P-compliant task plan ready; MVP = Phases 1–4 (stdlib-only, submittable).
- 🧪 Tests: none yet (this is the task list); every function has a planned test_<fn> task.
- 📁 Files: specs/001-sensor-monitor/tasks.md
- 🔁 Next prompts: /sp.adr optional-ai-diagnosis-dependency; then /sp.implement (or begin T001).
- 🧠 Reflection: User's module-split grouping conflicted with CS50P/constitution; resolved via a structure question rather than silently splitting files.

## Evaluation notes (flywheel)

- Failure modes observed: user grouping (separate modules) vs CS50P single-file requirement — surfaced and resolved by AskUserQuestion.
- Graders run and results (PASS/FAIL): format validation PASS (all tasks have checkbox+ID+path; story labels on story tasks); constraint check PASS (≤2 files, test-first, AI last).
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): add a /sp.implement run that executes T001–T005 to verify scaffolding.
