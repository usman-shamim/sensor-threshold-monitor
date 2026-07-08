# Feature Specification: Exhibition Polish — Fault Buttons, PDF Summary, Shutdown Toggle

**Feature Branch**: `006-exhibition-polish`
**Created**: 2026-07-08
**Status**: Implemented
**Input**: Exhibition-ready UI improvements: replace the fault injection dropdown with clickable buttons, auto-generate a one-page PDF report on session end, and make the emergency stop button toggle to Resume.

## Overview

Three small changes that make the dashboard more exhibition-friendly:
1. **Fault injection buttons** — the dropdown "Inject Fault" menu is replaced with a horizontal
   strip of color-coded buttons, one per fault type, visible at a glance. Exhibition presenters
   don't need to open a menu.
2. **PDF batch summary** — when the user presses Emergency Stop or closes the window, a one-page
   PDF is auto-generated with scenario name, duration, readings count, alarm breakdown, fault
   counts, and an event timeline. Judges get a physical artifact to take away.
3. **Shutdown toggle button** — the Emergency Shutdown button changes to a green "RESUME" button
   after shutdown is latched. Pressing RESUME restores monitoring and changes the button back.
   No separate banner interaction needed.

## Feature 1: Fault Injection Buttons

### What changed

| Before | After |
|--------|-------|
| Dropdown menu "Inject Fault" with `(clear)` + 6 fault names | 6 color-coded buttons (Blockage, Pump Failure, Cavitation, Fouling, Thermal Runaway, Cooling Failure) + "Clear Fault" button, all on a dedicated strip below the topbar |

### How it works

- A `_build_fault_bar()` method creates a horizontal `CTkFrame` strip below the topbar.
- Each button is a `CTkButton` with a distinct color and a lambda binding the fault name.
- The "Clear Fault" button calls `producer.clear_fault()`.
- On scenario switch, buttons still work because `_on_inject` calls the current `controller._producer` at click time.

### Files changed

- `sentinelgui/dashboard/main_window.py` — added `_build_fault_bar()`, updated `_on_inject()`, removed dropdown logic.

---

## Feature 2: PDF Batch Summary Report

### What it does

Generates `sentinelgui_report_YYYYMMDD_HHMMSS.pdf` in the working directory when:
- Emergency Stop is pressed
- The dashboard window is closed

### Report contents

| Section | Content |
|---------|---------|
| Title | SENTINELGUI - Batch Run Summary |
| Meta | Scenario name, duration, readings processed, generation timestamp |
| Alarm Summary | Total alarms, critical count, warning count, emergency shutdown count |
| Faults Detected | Per-fault occurrence count |
| Event Timeline | Table: time, severity (CRIT/WRN), sensor, detail (truncated explanation) |

### How it works

- `sentinelgui/report.py` — `generate(scenario_name, started_at, seq, fault_history)` builds the PDF using `fpdf2`.
- `AppController.start()` stamps `started_at`.
- `AppController.stop()` calls `_generate_report()`.
- `MainWindow._on_estop()` calls `controller._generate_report()`.
- All text is ASCII-normalized via `_s()` helper for the built-in Helvetica font.

### New dependency

- `fpdf2>=2.8` added to `sentinelgui/requirements.txt`.

### Files

- `sentinelgui/report.py` — new, PDF generation
- `sentinelgui/app.py` — `started_at`, `_generate_report()`, calls in `start()` and `stop()`
- `sentinelgui/dashboard/main_window.py` — call in `_on_estop()`
- `sentinelgui/requirements.txt` — added `fpdf2>=2.8`

---

## Feature 3: Shutdown / Resume Toggle Button

### What changed

| Before | After |
|--------|-------|
| Separate EMERGENCY SHUTDOWN button + banner to click for resume | Single button toggles: SHUTDOWN (red) → RESUME (green) → SHUTDOWN (red) |

### How it works

- `_on_estop()` — after shutdown, the button reconfigures to "RESUME" with green color and `command=self._confirm_resume`.
- `_confirm_resume()` — after resume confirmation, the button reconfigures back to "EMERGENCY SHUTDOWN" with red color and `command=self._on_estop`.
- The red shutdown banner is retained as a visual indicator but no longer needs to be clickable.

### Files changed

- `sentinelgui/dashboard/main_window.py` — `_on_estop()` and `_confirm_resume()` modified, `_show_shutdown()` removed.

---

## Success Criteria

- **SC-001**: Clicking each fault button injects the correct fault and updates the status bar within 1 second.
- **SC-002**: Pressing Emergency Stop generates a `sentinelgui_report_*.pdf` file in the current directory.
- **SC-003**: The PDF opens correctly on any OS with a PDF viewer and contains at least 5 sections.
- **SC-004**: After shutdown, the button shows "RESUME" (green); after resume, it shows "EMERGENCY SHUTDOWN" (red).
- **SC-005**: 58 tests pass.
