# Feature Specification: ReAct Agent Visibility — Reasoning Trace Panel

**Feature Branch**: `003-react-visibility`
**Created**: 2026-07-04
**Status**: Draft
**Input**: The existing ReAct agent (`sentinelgui/react_agent.py`) runs silently — it evaluates alarms, classifies faults, and computes stage health, but exhibition judges cannot see it think. Add a visible reasoning trace panel on the dashboard that logs each Observe→Reason→Act step when alarms fire, alarms clear, or the diagnosis changes.

## Overview

The ReAct agent currently produces an `AgentResult` (alarms + diagnosis + stage health) consumed
by the `AppController` and rendered by the `MainWindow`. None of the agent's internal reasoning —
*which sensor values triggered which fault rule, at what confidence, with what action* — is
visible on screen.

A **scrolling reasoning trace panel** is added to the dashboard, driven directly by the
`AgentResult` the agent already produces. Each trace entry captures the agent's decision path
in three lines (Observe / Reason / Act) with inline sensor values, zones, and fault reasoning.
The panel is silent during steady-state operation and lights up only when the agent detects
something worth showing — a fault fires, a fault clears, or the diagnosis changes.

The feature is purely display-side: it does not alter the agent's logic, the fault engine, or
the data pipeline. It is one new widget (`TracePanel`), one new field on `AgentResult` (`trace`),
and one new `append_trace()` method on `ReActAgent`.

## Clarifications

### Session 2026-07-04 (grilling)

- Q: Where does the trace data originate? → A: Inside `ReActAgent.step()` — append trace strings to a `trace: list[str]` field on `AgentResult`.
- Q: Trace every step or only interesting events? → A: Only when alarms fire, alarms clear, or diagnosis changes. Silent during nominal steady state.
- Q: Format of each entry? → A: A 3-step Observe→Reason→Act block with inline sensor values and zones.
- Q: Where on the dashboard? → A: Full-width row below the mimic diagram on the left column.
- Q: How many entries visible? → A: Last 50 — circular buffer, oldest auto-drop. The fault log already holds the full history.
- Q: Severity colour coding? → A: Yes — amber badge for warning, red for critical, green for cleared.
- Q: Controls? → A: A single "Clear" button to wipe the trace between demo scenarios.
- Q: Cleared-alarm entries format? → A: Short single-line notice (green), not the full 3-step block.

## User Scenarios & Testing

### User Story 1 — Exhibition judge sees the agent think (Priority: P1)

A chemical-technology exhibition judge watches the dashboard during a fault-injection demo.
When the presenter injects a blockage by partially closing a valve, the sensor cards update, an
alarm fires in the alarm panel, and — below the process mimic diagram — a new reasoning trace entry
appears showing exactly what the agent observed, how it reasoned about the readings, and what action
it took.

**Why this priority**: This is the whole point. The agent currently works invisibly. Making its
reasoning visible is the feature. Without it, nothing else in this feature matters.

**Independent Test**: Inject a fault via the simulator; confirm a trace entry appears within one tick,
contains the correct sensor values, the correct fault name, and uses the correct severity colour.

**Acceptance Scenarios**:

1. **Given** the dashboard is running and all sensors are nominal, **When** a reading arrives that
   is in-range, **Then** no trace entry appears (the panel stays silent).
2. **Given** a sensor crosses its warning threshold, **When** the agent processes the reading,
   **Then** a trace entry appears with an amber severity badge and a 3-step Observe→Reason→Act block.
3. **Given** a sensor crosses its critical threshold while already in warning, **When** the agent
   processes the reading, **Then** a new trace entry appears with a red severity badge, and the prior
   amber entry remains visible.
4. **Given** a fault clears (readings return to normal), **When** the agent processes the reading,
   **Then** a short single-line green entry appears: "temperature returned to normal zone."
5. **Given** a fault is active and a new reading arrives that does *not* change alarms or diagnosis,
   **When** the agent processes the reading, **Then** no new trace entry is produced.

---

### User Story 2 — Clear between demo scenarios (Priority: P2)

The presenter finishes one fault scenario and wants to start the next with a clean trace panel.
They press the "Clear" button; all entries are removed and the panel is blank, ready for the
next scenario.

**Why this priority**: The fault log already holds the full timestamped history. The trace panel is
a live "what's happening right now" view. A Clear button keeps it scannable across demo runs.

**Independent Test**: Let the trace accumulate 5 entries, press Clear, confirm the panel is empty.

**Acceptance Scenarios**:

1. **Given** the trace panel contains several entries, **When** the presenter presses "Clear",
   **Then** all entries are removed and the panel shows no content.

---

### User Story 3 — Trace stays under the mimic in kiosk mode (Priority: P2)

In exhibition kiosk mode (`--kiosk`), the trace panel must remain visible below the mimic
diagram with appropriately enlarged text for the exhibition display.

**Why this priority**: The exhibition is the primary use case for this feature.

**Independent Test**: Launch with `--kiosk`, inject a fault, confirm the trace entry text is
readable at exhibition screen sizes.

**Acceptance Scenarios**:

1. **Given** the app is in kiosk mode, **When** a trace entry appears, **Then** its text uses
   the kiosk font scaling (same as other dashboard widgets).

---

### Edge Cases

- **Trace buffer full (50 entries)**: when a 51st entry is appended, the oldest entry is silently
  dropped from the panel.
- **Multiple simultaneous alarms**: if two sensors breach in the same tick, a single trace entry
  captures all breached sensors in its Observe step (e.g. "temp 98°C → critical, flow 12 L/min → warning").
- **Diagnosis changes without new alarms**: if the fault engine reclassifies from "undetermined"
  to "blockage" as the signature becomes clearer, a new entry is produced even though no new alarm fired.
- **AI explanation requested**: the trace panel is rule-based only — it does not include AI
  enrichment text. The AI panel remains the home for that.
- **Panel empty at startup**: the trace panel shows a subtle placeholder ("No alerts yet — trace
  will appear when alarms fire.") so the empty panel doesn't look broken.
- **"Clear" during an active fault**: clearing the trace does not clear alarms or diagnosis. The
  next tick that changes state will produce a new trace entry.

## Requirements

### Functional Requirements

- **FR-001**: `ReActAgent.step()` MUST populate a `trace: list[str]` field on `AgentResult` with
  one or more trace entries whenever alarms fire, alarms clear, or the diagnosis changes.
  No entry is produced when nothing changes.
- **FR-002**: Each trace entry for alarm-fire / diagnosis-change events MUST follow a 3-step
  format:
  - **Observe**: per-sensor value + zone (e.g. "temp 98.2°C → critical, flow 28 L/min → normal")
  - **Reason**: the fault rule that matched + supporting data (e.g. "temp ≥ 100°C → thermal_runaway;
    rate of rise 2.3°C/s → high confidence")
  - **Act**: the action taken (e.g. "raised critical alarm 'temperature', diagnosis: thermal_runaway")
- **FR-003**: Each trace entry for alarm-cleared events MUST be a short single line
  (e.g. "temperature returned to normal zone") with a green badge.
- **FR-004**: The trace panel widget (`sentinelgui/dashboard/trace_panel.py`) MUST display entries
  in a scrollable, read-only text area, newest entry at the bottom.
- **FR-005**: The widget MUST apply severity colour coding: amber badge for warning entries, red
  badge for critical entries, green badge for cleared entries.
- **FR-006**: The buffer MUST hold a maximum of 50 entries; the 51st entry silently drops the oldest.
- **FR-007**: The widget MUST provide a "Clear" button that removes all trace entries from the
  display (and the underlying buffer).
- **FR-008**: When empty, the widget MUST show placeholder text: "No alerts yet — trace will appear
  when alarms fire."
- **FR-009**: The widget MUST be placed full-width below the mimic diagram on the left column of
  the dashboard.
- **FR-010**: The widget MUST respect the kiosk `self.kiosk` flag for font scaling, consistent with
  all other dashboard widgets.
- **FR-011**: The trace panel MUST be purely display-side — it MUST NOT alter the ReAct agent's
  logic, fault engine, or data pipeline.

### Key Entities

- **TraceEntry**: a single reasoning trace event carrying a timestamp, severity (warning/critical/cleared), a 3-step text block (observe/reason/act lines), and the sensor(s) involved. Produced inside `ReActAgent.step()` and carried on `AgentResult.trace`.
- **TracePanel** (widget): the customtkinter component that renders trace entries with colour-coded badges and a Clear button, placed below the mimic diagram.

## Success Criteria

- **SC-001**: When a fault is injected via the simulator, a colour-coded trace entry appears
  within one dashboard tick (≤250 ms after the reading is processed), with the correct fault
  name in the Reason step.
- **SC-002**: During 60 seconds of nominal (in-range) readings, zero trace entries are produced.
- **SC-003**: After 55 injected fault events, the trace panel shows exactly the 50 most recent
  entries (oldest 5 dropped).
- **SC-004**: Pressing "Clear" removes all entries and shows the placeholder within one frame.
- **SC-005**: The trace panel text is readable at a distance of 3 metres in kiosk mode on a 15-inch
  or larger display.
- **SC-006**: Existing test suite (`pytest sentinelgui/tests/ test_project.py`) remains 58 passed;
  the trace feature does not break any existing functionality.

## Dependencies

- The existing `ReActAgent` class in `sentinelgui/react_agent.py` — `step()` is the injection point
  for trace generation.
- The existing `AgentResult` dataclass — one new field `trace`.
- The existing `MainWindow` layout in `sentinelgui/dashboard/main_window.py` — one new widget
  instantiation and `update()` call.
- The existing `AppController` in `sentinelgui/app.py` — `_build_state()` passes `trace` through.
- The existing `theme.py` — colour constants may need one addition for "cleared" green.

## Out of Scope

- AI-enriched trace entries (AI explanations remain in the existing `AIPanel`).
- Exporting the trace to a file or clipboard.
- Searching/filtering trace entries.
- Trace entries for events that do not involve alarms or diagnosis changes (e.g. source connect/disconnect).
- Cross-session persistence of trace entries.
