# Implementation Plan: SentinelGUI — Reactor Cooling Loop Monitor & Fault Diagnosis

**Branch**: `002-sentinel-gui` | **Date**: 2026-06-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-sentinel-gui/spec.md`

## Summary

SentinelGUI is a desktop, SCADA-style monitoring and fault-diagnosis dashboard for a physical
reactor cooling-loop demonstration rig. It ingests a ~1 Hz stream of temperature, flow-rate, and
pressure readings from an Arduino over USB serial (or from a built-in fault simulator when no
hardware is present), evaluates each reading against two-band (Warning/Critical) thresholds, raises
alarms, and explains the likely physical fault. A rule-based hybrid classifier (current values +
short-term rate-of-change over a rolling window) provides always-available offline diagnosis; an
on-demand "Explain with AI" action reuses the existing **SentinelCLI** (`project.py`) Gemini layer
for a richer narrative with graceful fallback. The app records sessions to CSV, keeps a fault
history log, offers an Emergency Shutdown that latches a UI safe state and best-effort sends a
physical stop command, and ships an Exhibition/Kiosk mode tuned for a 15-inch laptop display.

Technical approach: a single Python package (`sentinelgui/`) of nine cooperating modules. A
background acquisition thread reads the data source at 1 Hz and pushes readings onto a thread-safe
queue; the CustomTkinter UI thread drains the queue via Tk `after()` polling (never blocking on
serial or AI). Matplotlib charts are embedded via `FigureCanvasTkAgg`. The existing CS50P
SentinelCLI (`project.py` / `test_project.py`) is **left untouched and importable**, preserving its
standard-library-only, CLI submission.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: PySerial (USB serial I/O), Pandas (CSV logging / tabular handling),
CustomTkinter (dark-theme UI widgets over Tkinter), Matplotlib (embedded trend charts). Reuses the
existing SentinelCLI `project.py` (standard-library + `urllib` Gemini call) for AI diagnosis.
**Storage**: Local filesystem — session CSV logs (timestamped filenames), a JSON GUI config for
two-band thresholds + serial settings; no database. Fault history is in-memory (session-only).
**Testing**: `pytest` for the headless modules (acquisition parsing, process engine, fault engine,
thresholds, alarm manager, simulator, data logger, ReAct agent, SentinelCLI bridge). UI widgets are
validated manually against the quickstart; logic is extracted from widgets to stay unit-testable.
**Target Platform**: Windows/macOS/Linux desktop (Python 3.12). Primary target: a 15-inch laptop
(≥1920×1080) at an exhibition; offline-first.
**Project Type**: Single desktop application (new `sentinelgui/` package) alongside the existing
CS50P CLI; not web/mobile.
**Performance Goals**: Sustain 1 Hz ingest with UI reflecting new readings/alarm state ≤2 s
(SC-001); chart redraw and queue drain comfortably within a ~250 ms UI tick; AI calls bounded by a
~10 s timeout off the UI thread.
**Constraints**: Offline-capable for all core features (SC-005); UI thread must never block on
serial or AI; memory bounded by the rolling window (~5 min ≈ 300 samples) plus the open CSV writer;
must run on a single laptop with no server.
**Scale/Scope**: Single rig, 3 sensors, 1 operator/presenter at a time; 9 modules; ~6 fault classes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The active constitution (v3.0.0, "Sensor Threshold Monitor Constitution") governs this project's CLI
and GUI deliverables together. SentinelGUI aligns with every principle.

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Python-First & PEP 8 | ✅ Pass | All SentinelGUI code is Python 3.12, PEP 8. |
| II. Testable Core, Thin UI | ✅ Pass | Logic lives in importable modules (`acquisition`, `thresholds`, `fault_engine`, etc.); `dashboard/*` widgets are thin and delegate to the core. |
| III. Automated Test Coverage (pytest) | ✅ Pass | Every headless logic module has a `test_<module>.py` (normal + edge/error case) under `sentinelgui/tests/`; thin UI is validated via quickstart. |
| IV. Offline-First & Graceful Degradation | ✅ Pass | All core features (acquisition, alarms, rule-based diagnosis, charts, mimic, recording, e-stop) work with no network; optional AI is timeout-bounded with clean fallback. |
| V. Human-Readable Errors | ✅ Pass | Serial/CSV/AI failures surface as plain on-screen banners and status text, never raw tracebacks. |
| VI. Secure Config & Reproducible Deps | ✅ Pass | No hardcoded secrets (`GEMINI_API_KEY` from env only); third-party deps pinned in `sentinelgui/requirements.txt`. |

**Gate result: PASS.** No deviations. (Under the prior CS50P-specific constitution v2.0.0 this feature
required documented exceptions for third-party deps and a GUI; constitution v3.0.0 makes those
first-class, so no exception or deviation ADR is needed.)

## Project Structure

### Documentation (this feature)

```text
specs/002-sentinel-gui/
├── plan.md              # This file (/sp.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (serial + module + bridge contracts)
│   ├── serial-protocol.md
│   ├── module-interfaces.md
│   └── sentinelcli-bridge.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks — NOT created here)
```

### Source Code (repository root)

```text
sentinelgui/
├── __init__.py
├── __main__.py              # argparse launcher (--simulate / --port / --kiosk); builds app
├── app.py                   # AppController: wires modules, owns the reading queue + Tk after() loop
├── acquisition.py           # Module 1: SerialDataAcquisition (PySerial) — background read thread
├── simulator.py             # Module 1b: FaultSimulator data source (no hardware), injectable faults
├── process_engine.py        # Module 2: raw frame -> engineering-unit Reading
├── thresholds.py            # Two-band (warning/critical) model; loads gui_config.json
├── alarm_manager.py         # Module 8: zone evaluation, debounce/hysteresis, active+history alarms
├── fault_engine.py          # Module 3: hybrid rule-based fault classification over rolling window
├── react_agent.py           # Module 4: Observe -> Reason -> Act loop tying engine+alarms+AI
├── sentinelcli_bridge.py    # Module 5: adapts Reading/Alarm to project.py; on-demand AI diagnosis
├── data_logger.py           # Module 7: pandas-backed CSV session recorder (start/stop)
├── shutdown_controller.py   # Module 9: e-stop — UI safe state + best-effort serial stop command
├── config/
│   └── gui_config.json      # warning+critical bands per sensor, serial port/baud, retention defaults
└── dashboard/               # Module 6: CustomTkinter UI (thin views over the logic above)
    ├── __init__.py
    ├── main_window.py       # SCADA layout, kiosk mode, status bar, E-stop button
    ├── sensor_card.py       # live value + zone colour per sensor
    ├── trend_chart.py       # Matplotlib FigureCanvasTkAgg per sensor
    ├── mimic_diagram.py     # Reservoir->Pump->Flow->Pressure->Reactor->Reservoir, stage highlight
    ├── alarm_panel.py       # Warning/Critical list
    ├── fault_log.py         # session fault history table
    └── ai_panel.py          # rule-based text + "Explain with AI" action

sentinelgui/tests/
├── test_process_engine.py
├── test_thresholds.py
├── test_alarm_manager.py
├── test_fault_engine.py
├── test_react_agent.py
├── test_simulator.py
├── test_data_logger.py
├── test_acquisition.py      # frame parsing only (no real port)
└── test_sentinelcli_bridge.py

# Untouched CS50P submission (still stdlib-only, CLI, pytest-green):
project.py
test_project.py
config.json
```

**Structure Decision**: A single new `sentinelgui/` package at the repo root, with logic split into
nine importable modules and a thin `dashboard/` view layer. All non-UI logic is unit-tested under
`sentinelgui/tests/`. SentinelCLI (`project.py`, `test_project.py`, `config.json`) is **not modified**
— SentinelGUI imports `project` for the AI bridge — so the CS50P deliverable stays constitution-
compliant while the GUI gets its own dependency set and structure.

## Complexity Tracking

No constitution violations to track — the Constitution Check above is a plain PASS under v3.0.0.

> Note: SentinelGUI lives in its own `sentinelgui/` package and reuses SentinelCLI (`project.py`) by
> import only; `project.py` / `test_project.py` are not modified by this feature. Third-party
> dependencies are confined to `sentinelgui/requirements.txt` (Principle VI).

## Phase 0 — Research

See [research.md](./research.md). Resolves: serial frame + command protocol and baud; CustomTkinter
+ Matplotlib concurrency with a 1 Hz background thread (queue + `after()`); two-band threshold reuse
of SentinelCLI `check_reading`; the six fault signatures (values + rate-of-change); the ReAct agent
shape; pandas vs `deque` for the rolling window and CSV; and the deferred data-retention defaults.

## Phase 1 — Design & Contracts

- [data-model.md](./data-model.md): Reading, Sensor, ThresholdBand (warning⊂critical), Alarm,
  FaultDiagnosis, FaultHistoryEntry, RecordingSession, DataSource, ProcessStage, ShutdownEvent,
  ReadingWindow; with fault-signature table and alarm/shutdown state transitions.
- [contracts/serial-protocol.md](./contracts/serial-protocol.md): Arduino→GUI frame format and
  GUI→Arduino command (`CMD:STOP`) for Emergency Shutdown.
- [contracts/module-interfaces.md](./contracts/module-interfaces.md): public function/class
  signatures per module (the "API" of this internal-only app).
- [contracts/sentinelcli-bridge.md](./contracts/sentinelcli-bridge.md): how SentinelGUI maps a
  Reading/Alarm to a SentinelCLI alert dict and calls `diagnose_alert(...)` off the UI thread.
- [quickstart.md](./quickstart.md): install, run with simulator, run with hardware, run tests.

## Phase 2 — Next

`/sp.tasks` will derive the test-first task list (one module group at a time, headless logic before
UI, `--simulate` path working before the hardware path), mirroring the SentinelCLI build order.

---

*Note: Under constitution v3.0.0 the third-party GUI/serial stack and the GUI itself are
first-class, so the previously-suggested constitution-deviation ADR is no longer required. An ADR may
still be recorded later for any genuinely significant design choice (e.g. the concurrency model) if
desired.*
