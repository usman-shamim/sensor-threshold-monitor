---
id: 0010
title: SentinelGUI Feature Spec
stage: spec
date: 2026-06-18
surface: agent
model: claude-opus-4-8[1m]
feature: 002-sentinel-gui
branch: 002-sentinel-gui
user: usman-shamim
command: /sp.specify
labels: [spec, sentinel-gui, gui, monitoring, fault-diagnosis, arduino]
links:
  spec: specs/002-sentinel-gui/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-sentinel-gui/spec.md
 - specs/002-sentinel-gui/checklists/requirements.md
tests:
 - none (specification stage; no code)
---

## Prompt

/sp.specify

Build a desktop application called SentinelGUI for the SentinelCLI project.

The application is an AI-assisted reactor cooling loop monitoring and fault diagnosis system for chemical process industries.

The GUI receives real-time sensor data from an Arduino Nano over USB serial communication.

The system monitors:
- Temperature (DS18B20)
- Flow Rate (YF-S201)
- Pressure Sensor

The dashboard should display:

1. Live sensor cards
   - Temperature
   - Flow Rate
   - Pressure

2. Real-time trend charts

3. Industrial process mimic diagram
   Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir

4. Alarm panel
   - Warning
   - Critical

5. Fault history log

6. Data recording to CSV

7. Emergency shutdown button

8. AI diagnosis panel

The AI diagnosis panel should explain:
- Blockages
- Fouling
- Pump failure
- Cavitation
- Thermal runaway
- Cooling system failure

Users should be able to simulate faults using physical valves on the exhibition model and immediately see dashboard updates.

The application should work offline using rule-based diagnosis and optionally use SentinelCLI AI analysis when available.

The target users are chemical technology students, exhibition judges, educators, and industrial visitors.

## Response snapshot

Created feature branch `002-sentinel-gui` and authored the full specification at
`specs/002-sentinel-gui/spec.md` plus the quality checklist at
`specs/002-sentinel-gui/checklists/requirements.md`.

Two scope-defining decisions were resolved with the user before drafting:
- **Emergency Shutdown**: latch the dashboard into a clearly marked SHUTDOWN safe state AND attempt
  a best-effort physical stop command, with a clear fallback message when hardware cannot be
  actuated (FR-020/FR-021).
- **No-hardware operation**: include a built-in fault simulator that drives the full dashboard with
  no Arduino attached (User Story 3, FR-003).

Spec contents:
- 7 prioritised, independently testable user stories: P1 live monitoring + Warning/Critical alarms;
  P2 offline rule-based diagnosis; P2 hardware-free fault simulator; P3 trends + process mimic;
  P3 recording + fault history; P3 emergency shutdown; P4 optional SentinelCLI AI diagnosis.
- 25 functional requirements grouped (acquisition/sources, monitoring/alarms, diagnosis,
  visualisation, recording/history, safety/shutdown, general/offline/secrets).
- 10 key entities, 8 edge cases, 8 measurable technology-agnostic success criteria, and explicit
  Assumptions / Dependencies / Out-of-Scope sections.

All checklist items pass; no `[NEEDS CLARIFICATION]` markers remain. Spec is ready for `/sp.clarify`
(optional) or `/sp.plan`.

## Outcome

- ✅ Impact: Feature 002-sentinel-gui specified end-to-end and ready for planning.
- 🧪 Tests: N/A — specification stage, no code produced.
- 📁 Files: spec.md (created), checklists/requirements.md (created); branch + prompts dir scaffolded.
- 🔁 Next prompts: `/sp.plan` to design the technical approach (architecture, serial protocol,
  simulator, diagnosis rules, UI framework); optionally `/sp.clarify` first.
- 🧠 Reflection: Asked exactly two high-impact scope questions up front (E-stop semantics, no-HW
  mode) rather than guessing, keeping the spec free of clarification markers.

## Evaluation notes (flywheel)

- Failure modes observed: `create-new-feature.ps1` failed on Windows PowerShell 5.1 (`Join-Path`
  3-argument form unsupported) after creating the branch and spec scaffold; the prompts directory
  was created manually as a workaround. Branch + spec.md were created correctly.
- Graders run and results (PASS/FAIL): Spec quality checklist — PASS (all 16 items).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): patch `create-new-feature.ps1` to nest `Join-Path`
  calls so it works on PowerShell 5.1, or add a bash equivalent under `.specify/scripts/bash/`.
