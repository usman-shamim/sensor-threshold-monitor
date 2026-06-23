---
id: 0012
title: SentinelGUI Implementation Plan
stage: plan
date: 2026-06-18
surface: agent
model: claude-opus-4-8[1m]
feature: 002-sentinel-gui
branch: 002-sentinel-gui
user: usman-shamim
command: /sp.plan
labels: [plan, sentinel-gui, architecture, scada, customtkinter, pyserial, react-agent]
links:
  spec: specs/002-sentinel-gui/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-sentinel-gui/plan.md
 - specs/002-sentinel-gui/research.md
 - specs/002-sentinel-gui/data-model.md
 - specs/002-sentinel-gui/contracts/serial-protocol.md
 - specs/002-sentinel-gui/contracts/module-interfaces.md
 - specs/002-sentinel-gui/contracts/sentinelcli-bridge.md
 - specs/002-sentinel-gui/quickstart.md
 - CLAUDE.md
tests:
 - none (planning stage; test strategy defined for /sp.tasks)
---

## Prompt

/sp.plan

Technology Stack:

Backend:
- Python 3.12
- PySerial
- Pandas

Frontend:
- CustomTkinter
- Matplotlib

Architecture:

Module 1:
Serial Data Acquisition
Reads Arduino data via USB

Module 2:
Process Data Engine
Converts raw values into engineering units

Module 3:
Fault Detection Engine
Rule-based fault classification

Module 4:
ReAct Agent
Observe → Reason → Act workflow

Module 5:
SentinelCLI Integration
Uses SentinelCLI for advanced diagnosis

Module 6:
Industrial Dashboard
Modern dark theme
Live cards
Charts
Process mimic diagram

Module 7:
CSV Data Logger

Module 8:
Alarm Manager

Module 9:
Emergency Shutdown Controller

The application should resemble a small SCADA system used in chemical plants.

Design for a 15-inch laptop exhibition display.

## Response snapshot

Generated the full planning artifact set for feature 002-sentinel-gui:

- **plan.md** — Summary; Technical Context (Python 3.12 + PySerial/Pandas/CustomTkinter/Matplotlib,
  reuses SentinelCLI `project.py`); Constitution Check; 9-module `sentinelgui/` package structure +
  `sentinelgui/tests/`; Complexity Tracking; phase pointers; ADR suggestion.
- **research.md** — 10 decisions (R1–R10): serial CSV frame + `CMD:STOP` command @115200; Tk
  concurrency via background thread → `queue.Queue` → `root.after(250)` drain, AI on a worker thread
  with ~10 s timeout; two-band thresholds reusing `check_reading` per band; six fault signatures
  (values + rate-of-change); rule-based ReAct loop; deque for the live window + pandas for CSV;
  retention defaults (~5 min window, manual recording, timestamped files); kiosk layout for 15-inch.
- **data-model.md** — 11 entities (Reading, Sensor, ThresholdBand warning⊂critical, Alarm,
  FaultDiagnosis, FaultHistoryEntry, RecordingSession, DataSource, ProcessStage, ShutdownEvent,
  ReadingWindow); fault-signature table; alarm/recording/shutdown/source state transitions;
  validation rules; `gui_config.json` schema seeded from SentinelCLI `config.json`.
- **contracts/** — serial-protocol.md (frame + command + e-stop outcome mapping + simulator
  equivalence); module-interfaces.md (public signatures for all 9 modules + test contract);
  sentinelcli-bridge.md (reuse of `load_config`/`check_reading`/`diagnose_alert`, alarm→alert
  mapping, off-UI-thread AI with injectable `client`, failure isolation).
- **quickstart.md** — simulator/hardware/kiosk run commands, AI key setup, recording, e-stop, tests,
  SC-mapped validation checklist.
- Ran `update-agent-context.ps1 -AgentType claude` — CLAUDE.md updated with the new stack.

**Constitution Check = PASS WITH DOCUMENTED DEVIATIONS.** The CS50P constitution (stdlib-only, CLI-
only) intrinsically conflicts with a GUI/serial SCADA app. Deviations (Principle II third-party
deps; Principle IV GUI vs CLI) are justified in Complexity Tracking and **isolated** to
`sentinelgui/`; SentinelCLI (`project.py`/`test_project.py`/`config.json`) is untouched and remains
compliant and pytest-green. SentinelGUI imports `project` only for the AI bridge.

Surfaced an **ADR suggestion** for the stack/constitution-deviation decision.

## Outcome

- ✅ Impact: Feature 002-sentinel-gui is fully planned and ready for `/sp.tasks`; architecture,
  contracts, data model, and run/test story are defined; SentinelCLI reuse and isolation settled.
- 🧪 Tests: N/A this stage; per-module `pytest` strategy (test-first, headless-before-UI) defined for
  task generation.
- 📁 Files: plan.md, research.md, data-model.md, 3 contracts, quickstart.md (created); CLAUDE.md
  (updated by agent-context script).
- 🔁 Next prompts: `/sp.adr sentinelgui-stack-and-constitution-deviation` (recommended), then
  `/sp.tasks` to generate the dependency-ordered, test-first task list.
- 🧠 Reflection: Read `project.py` first to ground the bridge on the real `diagnose_alert(client=)`
  seam and alert/reading dict shapes, and chose an isolation strategy that keeps the CS50P submission
  constitution-clean while enabling the GUI stack.

## Evaluation notes (flywheel)

- Failure modes observed: none blocking. `update-agent-context.ps1` emitted mojibake on two emoji
  lines but completed successfully; `create-new-feature.ps1`'s earlier `Join-Path` bug (PS 5.1) was
  already worked around in the spec stage.
- Graders run and results (PASS/FAIL): Constitution gate — PASS (with documented, isolated
  deviations). Artifact completeness — PASS (plan + research + data-model + contracts + quickstart).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): in `/sp.tasks`, enforce the `--simulate` path green
  before any hardware-serial task, mirroring SentinelCLI's "no-AI MVP before AI" gate.
