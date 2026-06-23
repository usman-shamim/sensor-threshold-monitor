# Feature Specification: SentinelGUI — Reactor Cooling Loop Monitor & Fault Diagnosis

**Feature Branch**: `002-sentinel-gui`  
**Created**: 2026-06-18  
**Status**: Draft  
**Input**: User description: "Build a desktop application called SentinelGUI for the SentinelCLI project. An AI-assisted reactor cooling loop monitoring and fault diagnosis system for chemical process industries. The GUI receives real-time sensor data from an Arduino Nano over USB serial. Monitors Temperature (DS18B20), Flow Rate (YF-S201), Pressure. Dashboard: live sensor cards, real-time trend charts, industrial process mimic diagram (Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir), alarm panel (Warning/Critical), fault history log, data recording to CSV, emergency shutdown button, AI diagnosis panel. AI explains blockages, fouling, pump failure, cavitation, thermal runaway, cooling system failure. Users simulate faults using physical valves and see immediate dashboard updates. Works offline using rule-based diagnosis, optionally uses SentinelCLI AI analysis when available. Target users: chemical technology students, exhibition judges, educators, industrial visitors."

## Overview

SentinelGUI is a desktop monitoring and fault-diagnosis dashboard for a physical reactor
cooling-loop demonstration rig. It consumes a live stream of temperature, flow-rate, and pressure
readings produced by an Arduino microcontroller over a USB serial connection, evaluates each
reading against configurable safe operating ranges, raises Warning and Critical alarms, and
explains the likely physical fault behind an alarm in plain language — first with always-available
rule-based diagnosis, and optionally with richer narrative diagnosis from the existing SentinelCLI
AI capability when it is available.

The product is built for **live exhibition and teaching use**: a presenter (or a visitor) opens or
closes a physical valve on the rig to induce a fault, and the dashboard must visibly react within a
couple of seconds — sensor cards change, a trend line moves, the process mimic highlights the
affected stage, an alarm fires, and a diagnosis appears. The application must also run convincingly
with **no hardware attached**, using a built-in fault simulator, so it can be developed, tested, and
demonstrated as a backup.

## Clarifications

### Session 2026-06-18

- Q: SentinelCLI's `config.json` has only one min/max band per sensor — how should the GUI's
  Warning vs Critical limits be defined? → A: Two explicit bands per sensor — a `warning {min,max}`
  nested inside a `critical {min,max}`. Critical limits are seeded from the existing config values;
  Warning defaults to ~10% inside each bound. Both bands are operator-configurable.
- Q: What sensor sample / UI refresh rate should the system target? → A: ~1 Hz — one combined
  reading per second from the data source; sensor cards, trend charts, and the simulator all operate
  at this cadence.
- Q: What information should the rule-based fault classifier use? → A: Hybrid — current values vs
  thresholds **plus** short-term rate-of-change/trend over a rolling window of recent readings
  (a small rolling buffer is retained to distinguish dynamic faults).
- Q: Is a distinct Exhibition/Kiosk mode required? → A: Yes — fullscreen, enlarged fonts, simplified
  controls, confirmation guards on destructive actions (Emergency Shutdown, resume, reset), and
  automatic recovery into simulation mode if the serial link drops.
- Q: When should the optional SentinelCLI AI diagnosis run, and what timeout before fallback? → A:
  On-demand — rule-based diagnosis shows instantly on every alarm; AI runs only when the user
  requests it ("Explain with AI"), asynchronously, with a ~10s timeout then graceful fallback to
  the rule-based result. Never blocks the dashboard.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live monitoring with Warning/Critical alarms (Priority: P1)

A chemical-technology student watches the dashboard while the rig runs. Three live sensor cards
(Temperature, Flow Rate, Pressure) update continuously with the latest value and a clear
normal / warning / critical status. When a reading leaves its safe range, the corresponding card
changes state and an entry appears in the alarm panel labelled Warning or Critical.

**Why this priority**: This is the irreducible core of the product — without trustworthy live
values and alarm states, none of the other features have meaning. It is a complete, demonstrable
MVP on its own.

**Independent Test**: Feed a known sequence of readings (from the simulator or a connected rig) and
confirm each sensor card shows the correct value and status, and that crossing a warning/critical
boundary produces an alarm panel entry at the correct severity.

**Acceptance Scenarios**:

1. **Given** a connected data source streaming in-range readings, **When** a new reading arrives,
   **Then** the matching sensor card shows the value and a "normal" status within 2 seconds.
2. **Given** a temperature reading above its warning limit but below critical, **When** it arrives,
   **Then** the temperature card shows "warning" and a Warning alarm appears in the alarm panel.
3. **Given** a reading beyond its critical limit, **When** it arrives, **Then** the card shows
   "critical" and a Critical alarm appears, visually distinct from warnings.
4. **Given** a reading returns to its safe range, **When** it arrives, **Then** the card returns to
   "normal" and the active alarm clears (the historical record of it is retained — see US5).

---

### User Story 2 - Offline rule-based fault diagnosis (Priority: P2)

When an alarm fires, the diagnosis panel names the most likely physical fault — blockage, fouling,
pump failure, cavitation, thermal runaway, or cooling-system failure — and explains in one or two
plain sentences why the current readings point to it, using only built-in logic with no network
or external service.

**Why this priority**: Diagnosis is the feature's differentiator and the teaching payload, and it
must work with zero connectivity so an exhibition is never dependent on internet or an API key.

**Independent Test**: Present each fault's characteristic reading pattern (e.g. flow drops while
pressure rises → blockage) to the diagnosis logic and confirm it selects the expected fault and a
relevant explanation, with no external calls.

**Acceptance Scenarios**:

1. **Given** flow rate falls sharply while pressure rises, **When** the alarm fires, **Then** the
   diagnosis panel identifies a blockage and explains the flow/pressure relationship.
2. **Given** temperature climbs while flow and cooling indicators stay nominal, **When** the alarm
   fires, **Then** the panel identifies thermal runaway / cooling failure with a plain explanation.
3. **Given** no internet connection and no AI configured, **When** any alarm fires, **Then** a
   rule-based diagnosis still appears and the panel indicates it is offline/rule-based.
4. **Given** a reading pattern that matches no known fault signature, **When** the alarm fires,
   **Then** the panel states the alarm severity and that no specific fault could be determined.

---

### User Story 3 - Run with no hardware via fault simulator (Priority: P2)

A presenter without the rig (or with a failed serial connection) switches the app into simulation
mode. The simulator produces a realistic live stream and lets the presenter inject any of the
supported faults on demand, driving the entire dashboard exactly as real hardware would.

**Why this priority**: Enables development, automated testing, rehearsal, and a reliable fallback
if the physical rig fails mid-exhibition — high value for a demonstration product.

**Independent Test**: Launch the app with no Arduino present, start the simulator, inject each
fault, and confirm cards, charts, mimic, alarms, and diagnosis all respond identically to the
hardware path.

**Acceptance Scenarios**:

1. **Given** no serial device is detected, **When** the app starts, **Then** it offers/enters
   simulation mode rather than failing.
2. **Given** simulation mode is running, **When** the presenter injects a chosen fault, **Then** the
   relevant sensors trend toward that fault's signature and the matching alarm and diagnosis appear.
3. **Given** simulation mode is running, **When** the presenter clears the injected fault, **Then**
   readings return to nominal and alarms clear.

---

### User Story 4 - Visual trends and process mimic diagram (Priority: P3)

A visitor sees real-time trend charts for each sensor and an industrial process mimic showing the
loop **Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir**, where the stage
associated with an active alarm is visually highlighted so the fault's location is obvious at a
glance.

**Why this priority**: This is the exhibition's visual impact and aids comprehension, but the system
is already useful (US1–US3) without it.

**Independent Test**: Stream changing readings and confirm each trend chart scrolls with new data
and that inducing a fault highlights the correct stage of the mimic diagram.

**Acceptance Scenarios**:

1. **Given** readings are arriving, **When** time passes, **Then** each sensor's trend chart shows a
   moving recent-history line.
2. **Given** a blockage alarm at the flow sensor, **When** it is active, **Then** the flow-sensor
   stage of the mimic is highlighted in an alarm colour.
3. **Given** all readings are nominal, **When** the loop runs, **Then** the mimic shows all stages in
   a normal/healthy state.

---

### User Story 5 - Data recording and fault history log (Priority: P3)

The presenter records a session to a CSV file for later review, and every alarm event is captured in
an on-screen fault history log (timestamp, sensor, value, severity, diagnosis) that persists for the
session and can be reviewed after the demonstration.

**Why this priority**: Valuable for teaching, judging, and record-keeping, but not required for a
live demonstration to be compelling.

**Independent Test**: Start recording, drive several in-range and out-of-range readings, stop
recording, and confirm the CSV contains the readings and the fault history log lists every alarm
with its diagnosis.

**Acceptance Scenarios**:

1. **Given** recording is started, **When** readings arrive, **Then** each is appended to a CSV file
   with timestamp and all sensor values.
2. **Given** an alarm fires, **When** it is raised, **Then** a fault history entry is added with
   time, sensor, value, severity, and the diagnosis text.
3. **Given** recording is stopped, **When** the file is opened, **Then** it is well-formed CSV
   readable by common spreadsheet tools.

---

### User Story 6 - Emergency shutdown (Priority: P3)

The presenter (or a judge) presses a prominent Emergency Shutdown button. The dashboard immediately
enters a clearly marked SHUTDOWN safe state and attempts to command the rig to stop; if it cannot
actuate the hardware, it says so but still shows the safe state.

**Why this priority**: A safety affordance expected of an industrial-style monitoring tool and a
strong exhibition talking point, but secondary to monitoring and diagnosis.

**Independent Test**: Press the button in both simulation and (if available) hardware modes and
confirm the UI enters the shutdown state, the event is logged, and a physical-stop command is
attempted with a clear success/fallback message.

**Acceptance Scenarios**:

1. **Given** the app is monitoring, **When** Emergency Shutdown is pressed, **Then** the dashboard
   latches into a visually unmistakable SHUTDOWN state and records the event in the fault history.
2. **Given** a control channel to the rig exists, **When** shutdown is pressed, **Then** a stop
   command is sent and its outcome (sent / failed) is shown to the user.
3. **Given** no control channel exists, **When** shutdown is pressed, **Then** the UI still enters
   the safe state and clearly states that hardware could not be actuated.
4. **Given** the app is in SHUTDOWN state, **When** the presenter chooses to resume, **Then**
   monitoring restarts only after an explicit confirmation.

---

### User Story 7 - Optional AI diagnosis via SentinelCLI (Priority: P4)

When an alarm fires, the rule-based explanation appears immediately. The user may then request a
richer narrative by pressing "Explain with AI"; when SentinelCLI's AI analysis is available it
augments the rule-based result. When it is unavailable (offline, missing key, disabled, or slow),
the panel falls back to the rule-based explanation without error and without blocking.

**Why this priority**: A meaningful enhancement that reuses existing SentinelCLI capability, but
explicitly optional — the product is fully functional and demonstrable without it.

**Independent Test**: With AI available, trigger an alarm and confirm an AI narrative appears
attributed as AI-generated; disable/remove AI and confirm the panel gracefully shows the rule-based
explanation instead, with no crash or blocking delay.

**Acceptance Scenarios**:

1. **Given** SentinelCLI AI is available, **When** the user presses "Explain with AI" for an active
   alarm, **Then** the AI panel shows a richer explanation labelled as AI-generated within ~10s.
2. **Given** AI is unavailable or exceeds the ~10s timeout, **When** the user requests it, **Then**
   the panel keeps the rule-based explanation and indicates AI was not used, without freezing.
3. **Given** AI is producing a diagnosis, **When** it is in progress, **Then** the live monitoring,
   alarms, and charts continue updating uninterrupted.

---

### Edge Cases

- **Serial disconnect mid-session**: the data source disappears while running → the app shows a
  clear "disconnected" state, stops claiming live values are current, and offers simulation mode;
  it does not crash or silently freeze on a stale value.
- **Malformed / partial serial frame**: a corrupt or incomplete reading arrives → it is discarded
  (and counted/logged) without disrupting the stream or producing a false alarm.
- **Reading exactly on a boundary**: a value equal to a warning or critical limit is treated
  consistently with SentinelCLI (inclusive safe range; equal to a bound is in-range).
- **Rapid fault toggling**: a valve is opened and closed quickly → alarms must not flicker
  uncontrollably; brief debouncing/hysteresis keeps the alarm panel readable.
- **AI slow or hanging**: the optional AI call is slow → it must never block live monitoring or the
  Emergency Shutdown button; it times out and falls back.
- **CSV target not writable**: the recording location is read-only or full → the user is warned and
  monitoring continues without recording.
- **Multiple simultaneous breaches**: several sensors breach at once → each produces its own alarm
  and the diagnosis reflects the combined pattern where a known multi-sensor signature applies.
- **Emergency shutdown during recording**: pressing shutdown still flushes/closes the CSV cleanly
  and logs the shutdown event.

## Requirements *(mandatory)*

### Functional Requirements

**Data acquisition & sources**

- **FR-001**: System MUST receive a continuous stream of temperature, flow-rate, and pressure
  readings from an Arduino microcontroller over a USB serial connection.
- **FR-002**: System MUST detect when no serial device is available or when the connection is lost,
  and surface that state to the user without crashing.
- **FR-003**: System MUST provide a built-in simulation mode that generates a realistic live
  reading stream and allows on-demand injection and clearing of each supported fault, usable with
  no hardware attached.
- **FR-004**: System MUST discard malformed, partial, or non-numeric incoming readings without
  raising false alarms, and keep a count of discarded readings.
- **FR-026**: System MUST operate at a nominal ~1 Hz cadence — one combined reading (temperature,
  flow rate, pressure) per second from the active data source — and the simulator MUST emit at the
  same rate; sensor cards and trend charts refresh per reading.

**Monitoring, thresholds & alarms**

- **FR-005**: System MUST display three live sensor cards (Temperature, Flow Rate, Pressure) each
  showing the latest value, unit, and a normal / warning / critical status.
- **FR-006**: System MUST evaluate each reading against configurable per-sensor thresholds defined
  as two explicit nested bands — a `warning {min,max}` inside a `critical {min,max}`. Critical
  limits default to SentinelCLI's existing `config.json` values; Warning limits default to ~10%
  inside each critical bound. Both bands MUST be operator-configurable.
- **FR-007**: System MUST raise a Warning alarm when a reading crosses its warning limit and a
  Critical alarm when it crosses its critical limit, displaying both in an alarm panel that visually
  distinguishes the two severities.
- **FR-008**: System MUST clear an active alarm when its sensor returns to the safe range, while
  retaining the event in the fault history.
- **FR-009**: System MUST reflect new readings and alarm-state changes in the UI within 2 seconds of
  the reading being received.
- **FR-010**: System MUST treat thresholds as configurable and SHOULD reuse the SentinelCLI
  configuration ranges as defaults so CLI and GUI agree on what is in-range.

**Diagnosis**

- **FR-011**: System MUST provide always-available offline, rule-based fault diagnosis that maps
  reading patterns to the most likely fault among: blockage, fouling, pump failure, cavitation,
  thermal runaway, and cooling-system failure. Classification MUST be hybrid — combining current
  values against thresholds with short-term rate-of-change/trend computed over a rolling window of
  recent readings — so dynamic faults (e.g. blockage vs cavitation vs fouling) can be distinguished.
- **FR-012**: System MUST show, for each diagnosis, a plain-language explanation of why the current
  readings indicate that fault, suitable for students and non-specialist visitors.
- **FR-013**: System MUST state when no known fault signature matches and report the alarm severity
  only, rather than guessing.
- **FR-027**: System MUST maintain a short rolling buffer of recent readings (sized to the trend
  window) to compute the rate-of-change/trend signals used by both diagnosis (FR-011) and the trend
  charts (FR-015).
- **FR-014**: System MUST show the rule-based explanation immediately on every alarm, and MUST offer
  on-demand AI enrichment via an "Explain with AI" action that runs SentinelCLI's AI analysis
  asynchronously with a ~10s timeout. AI-generated content MUST be clearly labelled, and the system
  MUST fall back to the rule-based explanation when AI is unavailable, disabled, or exceeds the
  timeout — without blocking live monitoring, alarms, or the Emergency Shutdown control.

**Visualisation**

- **FR-015**: System MUST display a real-time trend chart per sensor showing recent reading history.
- **FR-016**: System MUST display a process mimic diagram of the loop
  Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir, and MUST highlight the
  stage associated with an active fault.

**Recording & history**

- **FR-017**: Users MUST be able to start and stop recording the reading stream to a CSV file that
  is readable by common spreadsheet tools.
- **FR-018**: System MUST maintain an on-screen fault history log capturing, per alarm event,
  timestamp, sensor, value, severity, and diagnosis text, reviewable during and after a session.
- **FR-019**: System MUST warn the user and continue monitoring (without recording) if the CSV
  destination cannot be written.

**Safety / shutdown**

- **FR-020**: System MUST provide a prominent Emergency Shutdown control that immediately latches
  the dashboard into a clearly marked SHUTDOWN safe state and records the event.
- **FR-021**: System MUST attempt to send a physical stop command to the rig when a control channel
  is available, and MUST clearly report whether the hardware stop succeeded or could not be actuated.
- **FR-022**: System MUST require an explicit user confirmation to resume monitoring after a
  shutdown.

**Exhibition / Kiosk mode**

- **FR-028**: System MUST provide an Exhibition/Kiosk mode offering: fullscreen presentation,
  enlarged fonts and sensor cards, a simplified control set, confirmation guards on destructive
  actions (Emergency Shutdown, resume, reset/clear), and automatic recovery into simulation mode if
  the serial link drops mid-session. Standard (non-kiosk) operation MUST remain available for
  development and configuration.

**General**

- **FR-023**: System MUST run as an offline desktop application; all core capabilities (monitoring,
  alarms, rule-based diagnosis, charts, mimic, recording, shutdown) MUST function with no network.
- **FR-024**: System MUST never hardcode secrets or API keys; any AI credentials MUST come from
  environment/configuration as SentinelCLI already requires.
- **FR-025**: System MUST be operable by a non-technical visitor for the core monitoring flow
  without written instructions.

### Key Entities *(include if feature involves data)*

- **Sensor Reading**: one timestamped sample carrying temperature, flow rate, and pressure values
  (and the source/sequence it arrived from).
- **Sensor**: a monitored quantity (Temperature, Flow Rate, Pressure) with a display unit and a
  configured safe range.
- **Threshold / Alarm Rule**: per-sensor thresholds as two explicit nested bands — `warning
  {min,max}` inside `critical {min,max}` — defining normal, warning, and critical zones; configurable,
  with critical seeded from SentinelCLI's ranges and warning defaulting to ~10% inside each bound.
- **Reading Window (rolling buffer)**: the bounded set of most-recent readings retained to drive
  trend charts and the rate-of-change signals used by hybrid fault classification.
- **Alarm / Alert**: an event raised when a reading breaches a limit, carrying sensor, value, the
  breached limit, severity (Warning/Critical), and time; has active and cleared states.
- **Fault Diagnosis**: the identified fault type (blockage, fouling, pump failure, cavitation,
  thermal runaway, cooling-system failure, or "undetermined"), its plain-language explanation, and
  its source (rule-based or AI).
- **Fault History Entry**: a persisted-for-session record of an alarm and its diagnosis for review.
- **Recording Session**: a start/stop CSV capture of the reading stream with its file location and
  status.
- **Data Source**: the active origin of readings — a live serial connection or the simulator —
  with connection status.
- **Process Stage**: a node of the mimic loop (Reservoir, Pump, Flow Sensor, Pressure Sensor,
  Reactor) with a health/alarm state used for highlighting.
- **Shutdown Event**: a record of an emergency shutdown, including time, whether a hardware stop was
  attempted, and its outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a monitored value crosses a threshold, the corresponding sensor card and alarm
  panel reflect the new state within 2 seconds in at least 95% of cases.
- **SC-002**: For each of the six supported faults, inducing its characteristic reading pattern
  (via physical valve or simulator) produces the correct fault identification in the diagnosis
  panel in 100% of scripted test cases.
- **SC-003**: The application starts and runs the full dashboard (cards, charts, mimic, alarms,
  rule-based diagnosis) with no hardware connected, using the simulator, with no errors.
- **SC-004**: A first-time visitor can identify which sensor is in alarm and read its diagnosis
  within 15 seconds of an alarm firing, without assistance.
- **SC-005**: All core capabilities operate with networking disabled (airplane mode), confirming
  offline-first behaviour.
- **SC-006**: Rule-based diagnosis appears on every alarm immediately; when AI is requested but
  unavailable or slow, the panel falls back to the rule-based result within the ~10s AI timeout,
  with live monitoring uninterrupted and zero dashboard freezes.
- **SC-007**: A recorded session opens cleanly in common spreadsheet software with one row per
  reading and correct timestamps and values.
- **SC-008**: Pressing Emergency Shutdown latches the UI into the SHUTDOWN state within 1 second and
  records the event in 100% of presses, regardless of hardware presence.

## Assumptions

- Thresholds use two nested bands per sensor (resolved in Clarifications): critical limits are
  seeded from SentinelCLI's existing `config.json` values and warning limits default to ~10% inside
  each critical bound; both remain operator-configurable.
- Data retention (default — to confirm during planning, not separately clarified): the trend
  window / rolling buffer defaults to ~5 minutes of readings (~300 samples at 1 Hz); the on-screen
  fault history is session-only; CSV recording is manually started/stopped (not auto-started) and
  written to a user-chosen location with a timestamped filename.
- "Optionally use SentinelCLI AI analysis" means SentinelGUI reuses SentinelCLI's existing diagnosis
  capability (the same project's AI layer) rather than reimplementing it; the GUI does not introduce
  a new AI provider or contract.
- The Arduino emits one combined frame per sample containing all three sensor values; exact framing
  and the physical-stop command protocol are an implementation/contract concern for the plan, not a
  scope question. A read-only mode is fully supported when no control channel exists.
- "Real-time" for this exhibition context means human-perceptible immediacy (≤2 s), not hard
  real-time guarantees.
- Fault history persists for the duration of a session (and to the CSV when recording); long-term
  cross-session persistence is not required.
- The simulator's fault signatures are intended to be representative for teaching, not a validated
  physical model of the rig.

## Dependencies

- The existing **SentinelCLI** project (`project.py`) for threshold configuration defaults and the
  optional AI diagnosis capability.
- A physical demonstration rig with an Arduino microcontroller, DS18B20 temperature sensor,
  YF-S201 flow sensor, and a pressure sensor, connected over USB serial (for live mode; not required
  for simulation mode).
- Optional AI credentials/configuration as already used by SentinelCLI (for US7 only).

## Out of Scope

- Closed-loop automatic control of the rig (the system monitors, diagnoses, and offers emergency
  stop; it does not regulate the process automatically beyond the shutdown command).
- Multi-rig / multi-station aggregation or a central server; this is a single-station desktop app.
- User accounts, authentication, or role-based permissions.
- Long-term historical analytics, dashboards, or databases beyond per-session CSV recording.
- Replacing or re-architecting SentinelCLI's diagnosis logic.
