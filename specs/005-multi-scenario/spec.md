# Feature Specification: Multi-Scenario Industrial Process Support

**Feature Branch**: `005-multi-scenario`
**Created**: 2026-07-04
**Status**: Implementing
**Input**: The dashboard is hardcoded to a reactor cooling loop. Allow switching between multiple industrial processes (Reactor, Distillation Column, Steam Boiler) via a topbar dropdown, changing sensor labels, mimic diagram stages, thresholds, simulator behaviour, and fault explanations without restarting.

## Overview

The SentinelGUI dashboard currently hardcodes the reactor cooling loop in five places:
`models.py` (sensor labels/units/stages), `gui_config.json` (thresholds), `simulator.py`
(nominal operating points and fault targets), `fault_engine.py` (fault explanation strings),
and `mimic_diagram.py` (process stage labels).

This feature introduces a **scenario system**: each industrial process is defined in a
self-contained JSON file under `sentinelgui/config/scenarios/`. A dropdown in the dashboard
topbar lets the presenter switch processes during the exhibition. On switch, the system
performs a full reset (clears alarms, trace history, charts, and fault log) and the
dashboard instantly reflects the new process — new labels on sensor cards, new stage names
on the mimic diagram, and new threshold bands.

## Clarifications (Session 2026-07-04, grilling)

- Q: How do you switch scenarios? → A: Dropdown in the topbar (left side, next to status text).
- Q: What changes on switch? → A: Labels, mimic stages, thresholds. Same three sensors, same fault engine logic.
- Q: What happens to existing state on switch? → A: Full reset — clear alarms, trace, charts, fault log.
- Q: Where do scenario definitions live? → A: One JSON file per scenario in `sentinelgui/config/scenarios/`.
- Q: How many scenarios? → A: Three — Reactor Cooling Loop, Distillation Column, Steam Boiler.
- Q: How are fault explanations handled? → A: Each scenario JSON overrides the fault_engine explanation strings. Same classification logic.
- Q: Mimic diagram layout? → A: Same 5-stage linear flow, renamed per scenario.

## User Scenarios & Testing

### User Story 1 — Exhibition presenter switches processes live (Priority: P1)

A chemical technology exhibition presenter is demonstrating the reactor cooling loop.
A judge asks "does this work for other processes too?" The presenter opens the scenario
dropdown, selects "Steam Boiler", and within one tick the dashboard reconfigures: sensor
cards show "Stack Temp / Feed Water / Steam Press", the mimic shows boiler stages, and
threshold bands adapt to boiler-safe ranges.

**Acceptance**: Select scenario → verify all labels, mimic stages, and thresholds match the
selected scenario JSON within one tick.

### User Story 2 — Drop a new JSON to add a scenario (Priority: P2)

A student drops a new ` bioreactor.json ` into the `scenarios/` folder, restarts the app,
and the dropdown now lists four processes. No Python code was changed.

**Acceptance**: Add a valid scenario JSON → restart → dropdown shows the new entry.

### User Story 3 — Full reset on switch (Priority: P2)

When switching scenarios, all active alarms clear, the trace panel empties, trend charts
reset, and the fault log shows only entries from the current scenario. No data from the
previous process leaks into the new one.

**Acceptance**: Run reactor with faults → switch to distillation → alarms list is empty,
trace is empty, charts are blank.

## Requirements

### Functional

- **FR-001**: Each scenario MUST be defined in a JSON file under `sentinelgui/config/scenarios/`.
- **FR-002**: A scenario JSON MUST define: `name`, `description`, `sensors` (labels + units per key), `stages` (ordered list of 5 stage names), `stage_sensor` (which stage maps to which sensor key), `nominal` simulator values, `fault_targets` simulator fault signatures, `thresholds` (warning/critical bands), and `fault_explanations` (overriding fault_engine strings).
- **FR-003**: The dashboard topbar MUST display a dropdown listing all available scenarios in the `scenarios/` folder, positioned on the left next to the status text.
- **FR-004**: Selecting a scenario MUST trigger a full reset: clear active alarms, trace history, trend chart buffers, and fault log. The title bar MUST update to reflect the new scenario name.
- **FR-005**: After a scenario switch, the sensor cards MUST display the new scenario's labels and units. The mimic diagram MUST render the new scenario's stage names. Threshold evaluation MUST use the new scenario's bands.
- **FR-006**: The `FaultSimulator` MUST use the active scenario's `nominal` and `fault_targets` values, not hardcoded module-level constants.
- **FR-007**: The `fault_engine.classify()` function MUST use the active scenario's `fault_explanations` map when available, falling back to the hardcoded defaults.
- **FR-008**: Existing test suite (58 tests) MUST continue to pass. No existing functionality broken.

### Key Entities

- **Scenario**: a named industrial process definition loaded from JSON, carrying sensor labels/units, process stages, threshold bands, nominal simulator values, fault targets, and chemistry-aware fault explanations.

## Success Criteria

- **SC-001**: Switching from Reactor → Distillation → Boiler updates all 3 sensor card labels and all 5 mimic stage labels within one dashboard tick.
- **SC-002**: After switching, zero active alarms, zero trace entries, and empty trend chart buffers.
- **SC-003**: Injecting the same fault (e.g., blockage) in each of the 3 scenarios produces different fault explanation text matching the scenario's JSON.
- **SC-004**: Adding a new `.json` file to the scenarios folder and restarting adds the scenario to the dropdown with zero code changes.
- **SC-005**: 58 tests pass after all changes.

## Out of Scope

- Scenario-specific fault classification logic (same engine, different explanations only)
- Varying number of stages per scenario (always 5)
- Changing the number or type of sensors (always temp/flow/pressure)
- Saving/loading scenario state across sessions
