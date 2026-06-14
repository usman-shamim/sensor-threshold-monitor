---
id: 0004
title: Sensor Monitor Implementation Plan
stage: plan
date: 2026-06-14
surface: agent
model: claude-opus-4-8[1m]
feature: 001-sensor-monitor
branch: 001-sensor-monitor
user: usman-shamim
command: /sp.plan
labels: [plan, cli, sensors, ai-optional, cs50p, constitution-deviation]
links:
  spec: specs/001-sensor-monitor/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-sensor-monitor/plan.md
 - specs/001-sensor-monitor/research.md
 - specs/001-sensor-monitor/data-model.md
 - specs/001-sensor-monitor/contracts/cli.md
 - specs/001-sensor-monitor/contracts/config.schema.json
 - specs/001-sensor-monitor/contracts/ai-diagnosis.md
 - specs/001-sensor-monitor/quickstart.md
tests:
 - none
---

## Prompt

/sp.plan

Tech stack: Python 3.11+, standard library only (argparse, csv, json, datetime).
No third-party libraries except anthropic for the AI diagnosis layer.
Thresholds defined in a config.json file passed via --config CLI flag.
AI diagnosis via Claude API is optional — tool must work with --no-ai flag.
Target: CS50P final project structure (project.py + test_project.py at root).

## Response snapshot

Produced the implementation plan and Phase 0/1 design artifacts agent-natively (PowerShell
setup-plan.ps1 / update-agent-context.ps1 unavailable in this environment).

CONSTITUTION CONFLICT SURFACED: the requested `anthropic` dependency violates v2.0.0 Principle II
(Standard Library Only — third-party PROHIBITED) and the no-`pip install` quality gate, risking
CS50P gradeability. Reconciled (not removed) by design: AI layer is OFF by default, opt-in via
`--ai`, `anthropic` lazy-imported only inside `diagnose_alert`, graceful degradation (warn +
continue) when package/key absent, and full `--no-ai`/default path is 100% stdlib. Recorded as a
justified deviation in Constitution Check + Complexity Tracking. Gate result: PASS with one
documented deviation; Principles I, III, IV, V PASS.

Artifacts:
- plan.md — Technical Context, Constitution Check table, CS50P single-project structure
  (project.py: main, load_config, read_readings, check_reading, format_summary, diagnose_alert),
  Complexity Tracking, post-design re-check.
- research.md — 7 decisions (AI default/flags, lazy-import+DI seam, config.json schema/validation,
  CSV DictReader + alias matching, timestamp passthrough+row fallback, function decomposition,
  exit codes/streams).
- data-model.md — Reading, Threshold/Config (+default ranges), Alert, Summary entities + rules.
- contracts/cli.md — argparse arg contract, mutually-exclusive --ai/--no-ai, exit codes/streams.
- contracts/config.schema.json — JSON Schema for thresholds (inclusive min/max, subset allowed).
- contracts/ai-diagnosis.md — diagnose_alert interface, activation rules, lazy import, env-var key,
  injectable client test seam.
- quickstart.md — no-install core run, optional --ai, pytest, acceptance checks mapped to spec.

## Outcome

- ✅ Impact: Feature 001-sensor-monitor planned; design resolves the stdlib-vs-AI conflict without breaking CS50P gradeability.
- 🧪 Tests: none (planning artifacts); test seam for AI layer designed (injectable fake client).
- 📁 Files: plan.md, research.md, data-model.md, contracts/{cli.md,config.schema.json,ai-diagnosis.md}, quickstart.md
- 🔁 Next prompts: /sp.adr to record the optional-third-party-AI decision; then /sp.tasks.
- 🧠 Reflection: User tech stack directly contradicted the just-ratified Principle II; surfaced it explicitly and reconciled via optional lazy-imported seam rather than silently complying.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.ps1 / update-agent-context.ps1 unrunnable (no PowerShell); used agent-native fallback. Constitution Principle II deviation required justification.
- Graders run and results (PASS/FAIL): Constitution Check PASS-with-justified-deviation; placeholder scan PASS; design covers all FRs/SCs.
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): consider amending constitution to formally permit opt-in, lazy-imported optional dependencies, or record via ADR.
