---
description: "Task list for SentinelGUI implementation"
---

# Tasks: SentinelGUI — Reactor Cooling Loop Monitor & Fault Diagnosis

**Input**: Design documents from `/specs/002-sentinel-gui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED. Constitution Principle III (adapted) and `contracts/module-interfaces.md` mandate a
`test_<module>.py` per headless module covering a normal case + at least one edge/error case. UI
widgets (`dashboard/*`) are validated manually via quickstart.md, not unit-tested.

**Organization**: Tasks follow the user's requested 12-phase build order. Every task carries the
user-story label (`[US1]`–`[US7]`) it serves so each spec story remains independently traceable and
testable. Phase 1 = Setup, Phase 2 = Foundational (blocks all stories), Phases 3–12 = increments.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different file, no dependency on an incomplete task)
- **[USn]**: Maps to spec user story (US1 P1, US2 P2 diagnosis, US3 P2 simulator, US4 P3 visuals,
  US5 P3 recording, US6 P3 shutdown, US7 P4 AI)
- All paths are repo-root-relative (`C:\Users\DELL\Desktop\SDD\sensor-threshold-monitor\`)

## Story → Phase map

| Spec story (priority) | Delivered by phases |
|-----------------------|---------------------|
| US1 Live monitoring + alarms (P1) 🎯 MVP | 2, 3, 7 |
| US2 Offline rule-based diagnosis (P2) | 6, 9 |
| US3 Fault simulator / no-hardware (P2) | 2 (baseline), 12 |
| US4 Trends + process mimic (P3) | 4, 5 |
| US5 CSV recording + fault history (P3) | 8 |
| US6 Emergency shutdown (P3) | 11 |
| US7 Optional AI via SentinelCLI (P4) | 10 |

---

## Phase 1: Project structure  *(Setup)*

**Purpose**: Create the `sentinelgui/` package, config, and test scaffold per plan.md.

- [X] T001 Create the `sentinelgui/` package skeleton — empty module files (`acquisition.py`, `simulator.py`, `process_engine.py`, `thresholds.py`, `alarm_manager.py`, `fault_engine.py`, `react_agent.py`, `sentinelcli_bridge.py`, `data_logger.py`, `shutdown_controller.py`, `app.py`, `models.py`, `reading_window.py`) plus `sentinelgui/__init__.py` and `sentinelgui/dashboard/__init__.py` per plan.md "Source Code" tree
- [X] T002 [P] Add `sentinelgui/requirements.txt` pinning `pyserial`, `pandas`, `customtkinter`, `matplotlib`
- [X] T003 [P] Create `sentinelgui/config/gui_config.json` with the `serial` / `thresholds` (two nested bands) / `window` / `alarm` / `ai` / `recording` sections exactly as in data-model.md §Configuration
- [X] T004 [P] Create `sentinelgui/tests/__init__.py` and `sentinelgui/tests/conftest.py` that adds the repo root to `sys.path` so `import project` resolves in tests
- [X] T005 [P] Create `sentinelgui/__main__.py` argparse launcher parsing `--simulate`, `--port`, `--kiosk` (stub that just echoes parsed args for now)

**Checkpoint**: `python -m sentinelgui --help` lists the three flags; package imports cleanly.

---

## Phase 2: Arduino serial communication  *(Foundational — ⚠️ BLOCKS all user stories)*

**Purpose**: The source→queue→UI data backbone plus shared models, thresholds, and a baseline
simulator so every later phase is runnable and testable. No story is complete until this phase is.

- [X] T006 [P] Define core domain dataclasses (`Reading`, `Alarm`, `FaultDiagnosis`, `FaultHistoryEntry`, `RecordingSession`, `DataSource`, `ProcessStage`, `ShutdownEvent`) in `sentinelgui/models.py` per data-model.md §Entities
- [X] T007 [P] Implement `ReadingWindow` rolling buffer (`collections.deque(maxlen=window_samples)`, per-sensor series accessor, latest reading) in `sentinelgui/reading_window.py`
- [X] T008 [P] [US1] Write `test_acquisition.py` for `parse_frame` (valid 3-field frame; `#`-comment/empty line ignored; wrong token count → None; non-finite/NaN → None) in `sentinelgui/tests/test_acquisition.py`
- [X] T009 [US1] Implement `parse_frame` and `SerialDataAcquisition` (background read thread, queue push, `send_command`, `status` property) in `sentinelgui/acquisition.py` per contracts/serial-protocol.md
- [X] T010 [P] [US1] Write `test_process_engine.py` (raw→engineering units; non-finite raw → reading discarded) in `sentinelgui/tests/test_process_engine.py`
- [X] T011 [US1] Implement `to_engineering` and `build_reading` in `sentinelgui/process_engine.py`
- [X] T012 [P] [US1] Write `test_thresholds.py` (nesting-invariant validation error; `zone_of` normal/warning/critical; inclusive boundary = in-range) in `sentinelgui/tests/test_thresholds.py`
- [X] T013 [US1] Implement `thresholds.py` — `load_thresholds` (validates `critical.min ≤ warning.min ≤ warning.max ≤ critical.max`) and `zone_of` reusing `project.check_reading` once per band, in `sentinelgui/thresholds.py` (see contracts/sentinelcli-bridge.md §1)
- [X] T014 [P] [US3] Write `test_simulator.py` baseline (nominal `next_frame` yields three finite floats at the configured cadence) in `sentinelgui/tests/test_simulator.py`
- [X] T015 [US3] Implement `FaultSimulator` baseline nominal 1 Hz stream (`start`/`stop`/`next_frame` onto the same queue+dict path; `inject`/`clear_fault` stubs) in `sentinelgui/simulator.py` per serial-protocol.md §4
- [X] T016 Implement `AppController` owning the `queue.Queue`, the `root.after(250, drain)` loop, and `DataSource` state, in `sentinelgui/app.py`
- [X] T017 Build the CustomTkinter dark-theme main-window shell (status bar + grid regions for cards/charts/mimic/alarms/diagnosis) in `sentinelgui/dashboard/main_window.py`
- [X] T018 Wire `__main__.py` to construct `AppController` with either serial or simulator source and launch the window; verify `python -m sentinelgui --port COMx` and `--simulate` both open and tick

**Checkpoint**: Readings flow source→queue→UI tick at 1 Hz in both serial and simulate modes;
foundation ready — user-story phases can begin.

---

## Phase 3: Sensor cards  *(US1 — P1 🎯 MVP core)*

**Goal**: Three live sensor cards showing value, unit, and normal/warning/critical status.
**Independent test**: Stream known readings; each card shows the correct value and zone within 2 s.

- [X] T019 [P] [US1] Implement `SensorCard` widget (value, unit, zone colour) in `sentinelgui/dashboard/sensor_card.py`
- [X] T020 [US1] Render the three cards in `main_window.py` and bind each to the latest `Reading` + `zone_of` in the `AppController` drain loop (FR-005, FR-009)
- [X] T021 [US1] Add malformed-frame counter and "disconnected" status to the status bar (FR-002, FR-004)

**Checkpoint**: Live cards reflect readings/zones within 2 s (SC-001 partial).

---

## Phase 4: Real-time charts  *(US4 — P3)*

**Goal**: A scrolling trend chart per sensor.
**Independent test**: Stream changing readings; each chart shows a moving recent-history line.

- [X] T022 [P] [US4] Implement `TrendChart` (Matplotlib `FigureCanvasTkAgg`, scrolling series from `ReadingWindow`) in `sentinelgui/dashboard/trend_chart.py`
- [X] T023 [US4] Add one trend chart per sensor to `main_window.py`, fed from `ReadingWindow` each tick (FR-015)

---

## Phase 5: Process mimic diagram  *(US4 — P3)*

**Goal**: Reservoir→Pump→Flow→Pressure→Reactor loop with the active-fault stage highlighted.
**Independent test**: Induce a fault; the correct stage highlights; all-nominal shows all healthy.

- [X] T024 [P] [US4] Implement `MimicDiagram` (ordered loop nodes, per-stage health colour) in `sentinelgui/dashboard/mimic_diagram.py`
- [X] T025 [US4] Map sensor zones / active alarms to `ProcessStage.health` and highlight the affected stage in `main_window.py` (FR-016)

**Checkpoint**: US4 complete — trends scroll and the mimic localises the fault.

---

## Phase 6: Fault detection engine  *(US2 — P2)*

**Goal**: Hybrid rule-based classifier (values + rate-of-change) naming the likely fault.
**Independent test**: Feed each fault's signature; classifier picks the expected fault; unknown → undetermined.

- [X] T026 [P] [US2] Write `test_fault_engine.py` covering `slope()` and `classify()` for all six signatures + `undetermined` + the documented resolution order, in `sentinelgui/tests/test_fault_engine.py`
- [X] T027 [US2] Implement `slope()` and `classify()` over `ReadingWindow` per the data-model.md fault-signature table and resolution order, in `sentinelgui/fault_engine.py` (FR-011, FR-013)
- [X] T028 [US2] Implement `ai_panel.py` rule-based rendering (fault name + plain-language explanation + source="rule"; disabled "Explain with AI" button placeholder) in `sentinelgui/dashboard/ai_panel.py` (FR-012)

**Checkpoint**: US2 partial — correct rule diagnosis text computed for each signature (SC-002).

---

## Phase 7: Alarm system  *(US1 — P1 🎯 completes MVP)*

**Goal**: Warning/Critical alarms with debounce, clear-on-return, and history retention.
**Independent test**: Cross warning then critical then return; panel shows correct severities and clears.

- [X] T029 [P] [US1] Write `test_alarm_manager.py` (raise warning→critical, clear on safe return, debounce ≥N samples, history retained after clear) in `sentinelgui/tests/test_alarm_manager.py`
- [X] T030 [US1] Implement `AlarmManager` (`evaluate` returns state changes; `active`/`history` properties; debounce per `gui_config.json`) in `sentinelgui/alarm_manager.py` (FR-007, FR-008)
- [X] T031 [P] [US1] Implement `AlarmPanel` widget with visually distinct Warning vs Critical rows in `sentinelgui/dashboard/alarm_panel.py`
- [X] T032 [US1] Wire `AlarmManager` into the `AppController` tick; drive `AlarmPanel`, sensor-card zone, and mimic highlight from active alarms

**Checkpoint**: ✅ US1 COMPLETE — deployable MVP (live cards + alarms within 2 s, SC-001); US2
diagnosis is shown alongside fired alarms.

---

## Phase 8: CSV logger  *(US5 — P3)*

**Goal**: Start/stop CSV recording + on-screen fault history log.
**Independent test**: Record across in/out-of-range readings; CSV has one row per reading; log lists each alarm.

- [X] T033 [P] [US5] Write `test_data_logger.py` (start opens timestamped file; `write` appends one row per reading; unwritable dir → `RecordingSession.state == "error"`) in `sentinelgui/tests/test_data_logger.py`
- [X] T034 [US5] Implement `DataLogger` (pandas-backed `start`/`write`/`stop`, timestamped `sentinelgui_YYYYMMDD_HHMMSS.csv`, `RecordingSession`) in `sentinelgui/data_logger.py` (FR-017)
- [X] T035 [P] [US5] Implement `FaultLog` widget (timestamp, sensor, value, severity, diagnosis) in `sentinelgui/dashboard/fault_log.py` (FR-018)
- [X] T036 [US5] Add Start/Stop Recording controls and `FaultHistoryEntry` capture on each alarm; warn-and-continue when the CSV target is unwritable (FR-019)

**Checkpoint**: US5 complete — well-formed CSV (SC-007) and session fault history.

---

## Phase 9: ReAct agent  *(US2 — P2, completes diagnosis loop)*

**Goal**: Observe→Reason→Act loop tying alarms + fault engine + window into one `AgentResult`.
**Independent test**: Step the agent over a fault sequence; result carries new/cleared alarms, diagnosis, stage health.

- [X] T037 [P] [US2] Write `test_react_agent.py` (`step` yields new/cleared alarms + diagnosis + stage_health with no AI call) in `sentinelgui/tests/test_react_agent.py`
- [X] T038 [US2] Implement `ReActAgent` (`step` observe→reason→act; `request_ai(diagnosis, on_done)` async hook) wiring `AlarmManager` + `fault_engine` + `ReadingWindow` + bridge, in `sentinelgui/react_agent.py`
- [X] T039 [US2] Route the `AppController` tick through `ReActAgent.step`; the `AgentResult` drives cards, alarms, mimic, diagnosis panel, and fault log

**Checkpoint**: ✅ US2 COMPLETE — every alarm gets an immediate, correct rule-based diagnosis.

---

## Phase 10: SentinelCLI integration  *(US7 — P4, optional AI)*

**Goal**: On-demand "Explain with AI" reusing `project.diagnose_alert`, off the UI thread, with fallback.
**Independent test**: Inject a fake client → AI text appears labelled; raising/slow client → rule-based kept, no freeze.

- [X] T040 [P] [US7] Write `test_sentinelcli_bridge.py` (`alarm_to_cli_alert` mapping; `ai_diagnose` with injected fake client → string; raising client → None; timeout → None) in `sentinelgui/tests/test_sentinelcli_bridge.py`
- [X] T041 [US7] Implement `alarm_to_cli_alert` and `ai_diagnose` (worker thread, ~10 s `ai.timeout_s`, injectable `client`, never raises) reusing `project.diagnose_alert`, in `sentinelgui/sentinelcli_bridge.py` (contracts/sentinelcli-bridge.md)
- [X] T042 [US7] Wire the "Explain with AI" button → `ReActAgent.request_ai` → bridge off the UI thread; label AI text as AI-generated; on timeout/unavailable keep rule-based text with an "AI unavailable" note; key comes only from `GEMINI_API_KEY` env (FR-014, FR-024, SC-006)

**Checkpoint**: US7 complete — AI enriches when available, silent graceful fallback otherwise.

---

## Phase 11: Emergency shutdown relay  *(US6 — P3)*

**Goal**: Latching SHUTDOWN safe state + best-effort `CMD:STOP`, with confirmed resume.
**Independent test**: Press in sim and hardware modes; UI latches <1 s, event logged, outcome reported.

- [X] T043 [P] [US6] Write `test_shutdown_controller.py` (`trigger` latches `ui_safe_state`; outcome maps to `acked`/`sent`/`failed`/`no_channel` via fake source) in `sentinelgui/tests/test_shutdown_controller.py`
- [X] T044 [US6] Implement `ShutdownController` (`trigger` latch + `CMD:STOP` + ≤1 s `ACK:STOP` wait + `ShutdownEvent`; `resume`) in `sentinelgui/shutdown_controller.py` per serial-protocol.md §2
- [X] T045 [US6] Add the prominent Emergency Shutdown button + unmistakable SHUTDOWN overlay + resume-with-confirmation; log the event to fault history and flush/close any open CSV (FR-020, FR-021, FR-022, SC-008)

**Checkpoint**: US6 complete — shutdown latches <1 s regardless of hardware presence.

---

## Phase 12: Testing and exhibition mode  *(US3 — P2 + cross-cutting polish)*

**Goal**: Full fault-injection simulator, kiosk mode, auto-recovery, and end-to-end validation.
**Independent test**: No-hardware launch; inject/clear each fault; drop serial → auto-sim; full pytest green.

- [X] T046 [US3] Implement `FaultSimulator.inject`/`clear_fault` driving readings toward each data-model.md signature; add Inject Fault / Clear controls and no-serial auto-enter-simulation (FR-003, SC-003)
- [X] T047 [US3] Implement serial-drop auto-recovery in `AppController` (two consecutive missed frames → `disconnected` → `simulating`) per serial-protocol.md §3 (FR-002, FR-028)
- [X] T048 [P] Implement Kiosk/Exhibition mode (fullscreen, enlarged fonts/cards, simplified controls, confirmation guards on shutdown/resume/reset) toggled by `--kiosk` in `main_window.py` (FR-028)
- [X] T049 Run the full suite `pytest sentinelgui/tests/` and confirm `pytest test_project.py` is still green (SentinelCLI unaffected — isolation guarantee)
- [X] T050 [P] Execute the quickstart.md validation checklist and record SC-001…SC-008 pass/fail
- [X] T051 [P] Add `sentinelgui/README.md` (install, `--simulate`, `--port`, `--kiosk`, AI key, tests) distilled from quickstart.md

**Checkpoint**: ✅ All stories US1–US7 complete; offline-first, simulator-equivalent, exhibition-ready.

---

## Dependencies & Execution Order

### Phase dependencies
- **Phase 1 (Setup)**: no dependencies.
- **Phase 2 (Foundational)**: depends on Phase 1; **blocks every later phase**.
- **Phases 3–12**: depend on Phase 2. Within them the natural order is the user's numbering, but the
  true story dependencies are:
  - US1 MVP = Phase 2 → Phase 3 → Phase 7 (cards need alarms to be fully meaningful).
  - US2 = Phase 6 → Phase 9 (ReAct consumes the fault engine; both need the alarm manager from Phase 7).
  - US4 (Phases 4–5), US5 (Phase 8), US6 (Phase 11) are independent of each other once Phase 2 is done.
  - US7 (Phase 10) depends on US2's diagnosis path (Phase 9) for the "Explain with AI" hook.
  - US3 injection/kiosk (Phase 12) depends on the simulator baseline (Phase 2) and the widgets it drives.

### Critical path to MVP
Phase 1 → Phase 2 → Phase 3 → Phase 7  ⇒ shippable US1 demo.

### Within each story
- The `test_<module>.py` task is written **first and must fail** before its implementation task (TDD;
  Constitution Principle III adapted). Models/window before engines; engines before controller wiring;
  logic before its thin widget.

### Parallel opportunities
- Setup: T002, T003, T004, T005 in parallel.
- Foundational: T006, T007 in parallel; each test task (T008/T010/T012/T014) parallel with the others;
  each implementation follows its own test.
- Widgets marked [P] (T019, T022, T024, T031, T035) are independent files and can be built in parallel.
- After Phase 2, independent stories US4 / US5 / US6 can proceed concurrently if staffed.

---

## Parallel Example: Phase 2 foundational tests

```bash
# Author the failing headless tests together (different files):
Task: "test_acquisition.py — parse_frame cases"        # T008
Task: "test_process_engine.py — unit conversion"        # T010
Task: "test_thresholds.py — zone_of + nesting invariant" # T012
Task: "test_simulator.py — nominal stream"              # T014
```

---

## Implementation Strategy

### MVP first (User Story 1)
1. Phase 1 Setup → 2. Phase 2 Foundational (CRITICAL — blocks all) → 3. Phase 3 Cards → 4. Phase 7
   Alarms → **STOP & VALIDATE** US1 independently (SC-001) → demo-ready.

### Incremental delivery
Add US2 (Phases 6+9 diagnosis) → US4 (Phases 4–5 visuals) → US5 (Phase 8 recording) → US6 (Phase 11
shutdown) → US7 (Phase 10 AI) → US3 polish + kiosk (Phase 12). Each phase ends at a green checkpoint
and adds value without breaking earlier stories.

### Isolation guarantee (Constitution)
No task modifies `project.py`, `test_project.py`, or `config.json`. SentinelGUI only **imports**
`project` (T013 thresholds, T041 AI bridge). T049 re-confirms `test_project.py` stays green — the
CS50P submission remains standard-library-only and pytest-green throughout.

---

## Notes
- [P] = different file, no incomplete-task dependency.
- Every task names an exact file path and its user story.
- Verify each test fails before implementing it; commit after each task or logical group.
- Stop at any checkpoint to validate that story independently against its spec acceptance scenarios.
- Total: 51 tasks across 12 phases (5 Setup · 13 Foundational · 33 story/polish).
