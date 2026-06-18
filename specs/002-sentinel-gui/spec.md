# Feature Specification: SentinelGUI — Reactor Cooling Loop Monitoring & Diagnosis Dashboard

**Feature Branch**: `002-sentinel-gui`
**Created**: 2026-06-17
**Status**: Draft
**Input**: User description: "Build a desktop application called SentinelGUI for the SentinelCLI project. The application is an AI-assisted reactor cooling loop monitoring and fault diagnosis system for chemical process industries. The GUI receives real-time sensor data from an Arduino Nano over USB serial communication. The system monitors: Temperature (DS18B20), Flow Rate (YF-S201), Pressure Sensor. The dashboard should display: 1. Live sensor cards (Temperature, Flow Rate, Pressure); 2. Real-time trend charts; 3. Industrial process mimic diagram (Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir); 4. Alarm panel (Warning, Critical); 5. Fault history log; 6. Data recording to CSV; 7. Emergency shutdown button; 8. AI diagnosis panel. The AI diagnosis panel should explain: Blockages, Fouling, Pump failure, Cavitation, Thermal runaway, Cooling system failure. Users should be able to simulate faults using physical valves on the exhibition model and immediately see dashboard updates. The application should work offline using rule-based diagnosis and optionally use SentinelCLI AI analysis when available. The target users are chemical technology students, exhibition judges, educators, and industrial visitors."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live monitoring of the reactor cooling loop (Priority: P1)

A demonstrator stands the exhibition rig up, plugs in the Arduino, and launches SentinelGUI.
Within a few seconds the dashboard shows current temperature, flow rate, and pressure on
three large sensor cards, with trend charts updating continuously and a mimic diagram of the
cooling loop highlighting the active flow path. Visitors approaching the stand can read the
current state of the process at a glance.

**Why this priority**: This is the irreducible exhibition value. Without live, visible,
trustworthy sensor readout the rest of the system has nothing to react to and nothing to
show. Every other feature presumes this works.

**Independent Test**: Connect the Arduino streaming valid readings, launch the app, and
confirm that all three sensor cards show non-stale values updating at least once per second,
the trend chart accumulates points over time, and the mimic diagram renders the full
Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir path.

**Acceptance Scenarios**:

1. **Given** the Arduino is connected and streaming nominal readings, **When** the operator
   launches the app, **Then** within 3 seconds all three sensor cards show current values
   with units and a "healthy" visual state, and the trend chart begins plotting.
2. **Given** the app is running and the cooling loop is operating nominally, **When** 30
   seconds pass, **Then** each trend chart shows at least 30 plotted samples and the mimic
   diagram shows all components in the healthy state.
3. **Given** the Arduino is disconnected mid-session, **When** the next expected sample
   does not arrive, **Then** the sensor cards display a clear "sensor offline" state without
   crashing, and the app automatically resumes when the Arduino is reconnected.

---

### User Story 2 - Detect a process fault and raise alarms (Priority: P1)

While the system is running, a visitor closes a physical valve on the exhibition rig to
simulate a blockage. The flow rate drops, the pressure rises, and within one second the
alarm panel raises a Warning, then a Critical alarm as thresholds are crossed. The
corresponding component on the mimic diagram changes colour, and a fault entry appears in
the fault history log with a timestamp.

**Why this priority**: Demonstrating that the system *reacts* to a real, physical change is
the central educational moment of the exhibition. This is also P1 because alarms must be
trustworthy: a missed alarm undermines the entire safety story.

**Independent Test**: With the app running, force one sensor reading out of its safe range
(by closing a valve, or by replaying a recorded fault feed). Confirm that within 1 second a
matching alarm appears in the alarm panel, the mimic component changes state, and the fault
history log gains a new entry with the correct sensor, value, severity, and timestamp.

**Acceptance Scenarios**:

1. **Given** the flow rate is within its safe range, **When** the value drops below the
   warning threshold, **Then** a Warning alarm appears in the alarm panel within 1 second
   identifying the sensor, the offending value, the threshold breached, and the timestamp.
2. **Given** a Warning alarm is active, **When** the value crosses the critical threshold,
   **Then** the alarm is escalated to Critical and the corresponding mimic component is
   rendered in the critical visual state.
3. **Given** an alarm is active, **When** the sensor returns to its safe range, **Then** the
   alarm is moved from the active alarm panel to the fault history log with a resolution
   timestamp, while remaining searchable in history.
4. **Given** multiple sensors breach thresholds simultaneously, **When** alarms are raised,
   **Then** every breach is recorded as its own distinct alarm; no alarm is dropped.

---

### User Story 3 - Explain the fault with AI-assisted diagnosis (Priority: P2)

When an alarm is raised, the AI diagnosis panel presents an explanation in plain language:
the likely fault category (e.g., blockage, fouling, pump failure, cavitation, thermal
runaway, cooling system failure), the probable cause, and the recommended action. The
demonstrator uses this panel to teach visitors what is happening inside the loop. If the
SentinelCLI AI service is available, the panel uses it; otherwise it falls back silently to
the offline rule-based engine.

**Why this priority**: This is the differentiator that turns a monitoring demo into an
*AI-assisted* monitoring demo. It is P2 (not P1) because the alarm itself is the safety
signal — diagnosis is the educational and decision-support layer.

**Independent Test**: Induce a known fault (e.g., a blockage) and confirm that the AI
diagnosis panel renders a non-empty explanation with fault category, probable cause, and
recommended action, both when SentinelCLI is reachable and when it is not.

**Acceptance Scenarios**:

1. **Given** a blockage-style fault pattern is present (low flow + rising pressure), **When**
   the diagnosis panel updates, **Then** it identifies "blockage" as the likely category and
   names probable cause and recommended action in plain language.
2. **Given** the SentinelCLI service is unreachable or absent, **When** a fault occurs,
   **Then** the diagnosis panel shows the rule-based explanation, clearly labelled as
   offline, with no degradation to alarms or monitoring.
3. **Given** the SentinelCLI service is reachable, **When** a fault occurs, **Then** the
   AI-generated explanation is shown, labelled as AI-assisted, and the panel still shows a
   value even if the call later times out.

---

### User Story 4 - Emergency shutdown (Priority: P2)

The demonstrator sees a runaway condition (real or simulated) and presses the prominent
Emergency Shutdown button on the dashboard. The system signals the Arduino to cut the pump
(via the relay), the dashboard records a shutdown event in the fault history log, and the
UI enters a locked "shutdown" state until the operator explicitly resets it.

**Why this priority**: Demonstrates the safety story tangibly; without an operator override
the exhibition cannot credibly claim process safety. P2 rather than P1 because the
underlying monitoring and alarming must already work for shutdown to be meaningful.

**Independent Test**: With the app running, press Emergency Shutdown and confirm that the
Arduino receives a documented shutdown command, the shutdown event is recorded in the
fault history log with a timestamp, and the UI shows a locked shutdown state.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** the operator presses Emergency Shutdown,
   **Then** within 1 second a shutdown command is issued, a corresponding "Shutdown"
   event appears in the fault history log, and the UI shows an unambiguous shutdown banner.
2. **Given** the system is in shutdown state, **When** sensor readings continue to arrive,
   **Then** monitoring and logging continue, but no new alarms are escalated to Critical
   automatically until the operator resets the shutdown state.

---

### User Story 5 - Record data for review and education (Priority: P3)

Throughout the exhibition day, every sensor reading, alarm, and shutdown event is recorded
to a CSV file. After the show, an educator opens the file to review what happened, walk
students through specific fault episodes, or include screenshots in a report.

**Why this priority**: Recording is required by Principle IV (Safety & Fault Transparency)
and supports the educational mission, but the system delivers exhibition value even before
the file is ever opened.

**Independent Test**: Run the app for at least 10 minutes through both a nominal period
and at least one induced fault, stop the app, and confirm a CSV file exists containing one
row per sensor sample plus rows for each alarm and shutdown event, with timestamps and
sensor identifiers that match what was visible on the dashboard.

**Acceptance Scenarios**:

1. **Given** the app is running, **When** sensor readings arrive, **Then** each reading is
   appended to the CSV log with timestamp, sensor identifier, value, and unit.
2. **Given** an alarm is raised, **When** the alarm event occurs, **Then** the event is
   recorded with timestamp, sensor, severity, threshold, and value.
3. **Given** the CSV file cannot be written (disk full or permission denied), **When**
   logging fails, **Then** the failure is surfaced as a visible warning in the dashboard
   without crashing the app or stopping monitoring.

---

### Edge Cases

- Arduino disconnected mid-demo: app must show "sensor offline", continue running, and
  resume cleanly when the Arduino is re-attached without restarting the app.
- Malformed or partial serial frame: discarded with a counted error; does not crash the
  application or freeze the dashboard.
- Implausible sensor values (e.g., negative absolute pressure, NaN): flagged as
  data-quality issues, not as process faults.
- SentinelCLI times out or is missing: the diagnosis panel transparently falls back to the
  offline rule-based engine.
- CSV log file becomes unwritable mid-session: surfaced as a dashboard warning; in-memory
  history is preserved and the app continues to monitor.
- Multiple simultaneous fault categories (e.g., blockage AND high temperature): each
  produces its own alarm; the diagnosis panel orders them by severity.
- Operator presses Emergency Shutdown repeatedly: only one shutdown event is logged per
  shutdown transition.
- App started before the Arduino is connected: shows "waiting for sensors" rather than
  failing.
- Sustained no-fault period at end of demo: trend charts retain a configurable rolling
  window without unbounded memory growth.

## Requirements *(mandatory)*

### Functional Requirements

**Sensor acquisition & display**

- **FR-001**: System MUST receive sensor data (temperature, flow rate, pressure) from an
  Arduino Nano over USB serial communication.
- **FR-002**: System MUST display, on three Live Sensor Cards, the current value, unit,
  and visual health state (healthy / warning / critical / offline) for temperature, flow
  rate, and pressure.
- **FR-003**: System MUST render real-time trend charts for each sensor across a
  configurable rolling time window.
- **FR-004**: System MUST render an industrial mimic diagram showing
  Reservoir → Pump → Flow Sensor → Pressure Sensor → Reactor → Reservoir, with
  per-component visual state reflecting the underlying sensor or fault status.
- **FR-005**: System MUST update sensor cards, trend charts, and the mimic diagram at
  least once per second under nominal load (Principle VI).

**Alarms & fault history**

- **FR-006**: System MUST detect threshold breaches per sensor and raise alarms at
  Warning and Critical severities.
- **FR-007**: System MUST display every active alarm in the Alarm Panel with sensor,
  value, threshold, severity, and timestamp.
- **FR-008**: System MUST record every raised alarm in the Fault History Log, including
  resolution timestamp once the sensor returns to its safe range.
- **FR-009**: System MUST guarantee that no alarm is silently dropped (Principle IV);
  every threshold breach produces exactly one alarm transition.

**AI diagnosis**

- **FR-010**: System MUST present an AI Diagnosis Panel that, for each active alarm,
  produces an explanation containing fault category, probable cause, and recommended
  action.
- **FR-011**: System MUST support at minimum these fault categories: blockages, fouling,
  pump failure, cavitation, thermal runaway, cooling system failure.
- **FR-012**: System MUST diagnose faults using a built-in rule-based engine that operates
  fully offline (Principle III).
- **FR-013**: System MAY use SentinelCLI for AI-assisted diagnosis when reachable, and
  MUST clearly label results as AI-assisted or offline.
- **FR-014**: System MUST gracefully degrade to the offline rule-based engine on any
  SentinelCLI failure (timeout, missing binary, network error) without affecting
  monitoring or alarms (Principle III).

**Safety controls**

- **FR-015**: System MUST provide a prominent Emergency Shutdown button on the dashboard.
- **FR-016**: System MUST, on shutdown activation, send a documented shutdown command to
  the Arduino to actuate the relay, record the event in the Fault History Log, and lock
  the UI into a clearly visible shutdown state until the operator explicitly resets it.

**Data recording**

- **FR-017**: System MUST record every sensor sample to a CSV log with timestamp, sensor
  identifier, value, and unit.
- **FR-018**: System MUST record every alarm and shutdown event to the same or a
  related CSV log with timestamp and identifying fields.
- **FR-019**: System MUST surface CSV write failures as visible warnings on the dashboard
  without halting monitoring.

**Reliability & operability**

- **FR-020**: System MUST operate end-to-end without internet connectivity (Principle III).
- **FR-021**: System MUST handle Arduino disconnection and reconnection mid-session
  without restart, showing "sensor offline" while disconnected.
- **FR-022**: System MUST discard malformed serial frames safely, counting them as
  data-quality events rather than process faults.
- **FR-023**: Configuration (per-sensor safe ranges, CSV path, sample window) MUST be
  read from a documented configuration file; no secrets or tokens may be hardcoded.
- **FR-024**: System MUST run on a single demo machine and remain responsive (no visible
  UI lag) for a continuous exhibition session of at least 30 minutes.

### Key Entities

- **Sensor Reading**: a single measurement; carries timestamp, sensor identifier
  (temperature / flow rate / pressure), value, and unit.
- **Threshold Configuration**: per-sensor safe range boundaries — warning low/high and
  critical low/high — used to classify readings.
- **Alarm**: an active fault condition raised when a reading breaches a threshold; carries
  triggered timestamp, sensor, value, severity (Warning / Critical), and a link to its
  diagnosis.
- **Fault History Entry**: a closed alarm with resolution timestamp, preserved for review
  and CSV export.
- **Diagnosis Result**: an explanation associated with an alarm; carries fault category,
  probable cause, recommended action, and source (rule-based vs AI-assisted).
- **Process Component (Mimic Node)**: a visible node on the mimic diagram
  (Reservoir, Pump, Flow Sensor, Pressure Sensor, Reactor); carries current health state
  derived from one or more sensors.
- **Shutdown Event**: a recorded operator action; carries timestamp and reset timestamp.

### Assumptions

- One Arduino Nano on one USB serial port; one cooling-loop topology as described.
- A single operator drives the demo at a time; no multi-user concurrency.
- Deployment target is a single demo laptop / mini-PC; no remote access required.
- Per-sensor thresholds are read from a configuration file with defaults chosen for the
  exhibition rig; refining concrete values is a job for `/sp.clarify` or `/sp.plan`.
- Alarms auto-resolve when the underlying value returns to its safe range; explicit
  operator acknowledgement is not required to clear an alarm but resolved alarms remain in
  the Fault History Log.
- CSV is sufficient persistence for an exhibition day; no database is required.
- SentinelCLI is invoked locally (binary or local endpoint); its own configuration is out
  of scope for this spec.
- "Offline" means no internet; USB to the Arduino is always required.
- Only the three sensor types listed are in scope for v1; the architecture is expected to
  accommodate more later (Principle II — Modular Architecture).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A sensor reading produced at the Arduino is visible on the dashboard within
  1 second under nominal load.
- **SC-002**: When a reading breaches a threshold, the corresponding alarm appears in the
  Alarm Panel within 1 second.
- **SC-003**: A first-time visitor with no prior briefing can identify whether the process
  is healthy or faulted from the mimic diagram alone within 10 seconds.
- **SC-004**: The system runs a continuous 30-minute exhibition session with no crashes,
  no frozen UI, and no missed sensor samples beyond the data-quality budget.
- **SC-005**: 100% of induced fault scenarios (at least one per sensor, plus a blocked-flow
  scenario) produce both an alarm in the Alarm Panel and a diagnosis in the AI Diagnosis
  Panel.
- **SC-006**: With SentinelCLI unreachable, all of monitoring, alarms, the mimic diagram,
  CSV logging, and rule-based diagnosis continue to function with no visible degradation
  to the operator.
- **SC-007**: Every sensor reading shown on the dashboard during a session is recoverable
  from the CSV log after the session ends.
- **SC-008**: Emergency Shutdown actuates the Arduino relay and surfaces a visible
  shutdown banner within 1 second of the operator pressing the button.
- **SC-009**: Across at least three rehearsal runs prior to the exhibition, zero alarms
  are silently dropped (every threshold breach observed in raw data also appears in the
  Fault History Log).
