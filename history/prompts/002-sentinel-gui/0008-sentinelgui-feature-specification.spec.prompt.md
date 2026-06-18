---
id: 0008
title: SentinelGUI Feature Specification
stage: spec
date: 2026-06-17
surface: agent
model: claude-opus-4-7
feature: 002-sentinel-gui
branch: 002-sentinel-gui
user: usman-shamim
command: /sp.specify
labels: [spec, sentinel-gui, dashboard, monitoring, fault-diagnosis, exhibition]
links:
  spec: specs/002-sentinel-gui/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-sentinel-gui/spec.md
  - specs/002-sentinel-gui/checklists/requirements.md
tests:
  - none (spec stage)
---

## Prompt

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

Created feature branch `002-sentinel-gui` and populated `specs/002-sentinel-gui/spec.md`
with five prioritized user stories (live monitoring P1, fault detection P1, AI-assisted
diagnosis P2, emergency shutdown P2, data recording P3), 24 functional requirements
grouped by Sensor Acquisition / Alarms & Fault History / AI Diagnosis / Safety Controls /
Data Recording / Reliability, key entities (Sensor Reading, Threshold Configuration,
Alarm, Fault History Entry, Diagnosis Result, Process Component, Shutdown Event), an
explicit Assumptions section (single Arduino, single operator, CSV is sufficient,
auto-resolving alarms, sensor thresholds deferred to `/sp.clarify`), nine edge cases, and
nine measurable success criteria. Validated against
`specs/002-sentinel-gui/checklists/requirements.md` — all checklist items pass on first
iteration, zero `[NEEDS CLARIFICATION]` markers.

## Outcome

- ✅ Impact: Feature branch and ready-for-planning spec established for the SentinelGUI exhibition dashboard.
- 🧪 Tests: Spec-stage; no automated tests. Checklist `requirements.md` validates 100%.
- 📁 Files: `specs/002-sentinel-gui/spec.md`, `specs/002-sentinel-gui/checklists/requirements.md`.
- 🔁 Next prompts: `/sp.clarify` (concrete per-sensor thresholds and shutdown reset workflow) → `/sp.plan` → `/sp.tasks`.
- 🧠 Reflection: Hardware identifiers (Arduino Nano, DS18B20, YF-S201) and external service name (SentinelCLI) were kept in the spec because they identify the physical system and integration boundary, not implementation choices; flagged this explicitly in the checklist Notes so it isn't mistaken for technology leakage.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell `create-new-feature.ps1` failed parsing the description as positional remaining args (likely whitespace/punctuation in the long string); branch was still created. Recovered by writing `spec.md` directly from the template.
- Graders run and results (PASS/FAIL): requirements.md checklist — PASS (all items).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): when calling `create-new-feature.ps1` with long multi-paragraph descriptions, pass a shorter summary as the positional description (the spec body captures the full input verbatim) to avoid the parameter-binding failure.
