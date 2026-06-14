# Feature Specification: Sensor Threshold Monitor

**Feature Branch**: `001-sensor-monitor`
**Created**: 2026-06-14
**Status**: Draft
**Input**: User description: "Build a CLI tool for monitoring industrial process sensor data. Users provide a CSV file with sensor readings (temperature, pressure, flow rate). The tool checks each reading against configurable safe thresholds. When a value is out of range, the tool logs an alert with timestamp. At the end it prints a summary report showing total readings, alert count, and which sensors triggered alerts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Detect out-of-range readings in a sensor log (Priority: P1)

A process engineer has a CSV export of sensor readings from a production run and needs to
know whether any temperature, pressure, or flow-rate value left its safe operating range. They
run the tool against the file and receive a list of timestamped alerts plus a summary.

**Why this priority**: This is the core value of the tool — without out-of-range detection and
a summary, the tool delivers nothing. It is the minimum viable product.

**Independent Test**: Provide a CSV containing at least one in-range and one out-of-range value
for each sensor type; confirm the tool reports exactly the out-of-range readings as alerts and
prints a summary with the correct total and alert counts.

**Acceptance Scenarios**:

1. **Given** a CSV where every reading is within the safe range, **When** the user runs the
   tool, **Then** zero alerts are reported and the summary shows total readings with an alert
   count of 0.
2. **Given** a CSV where a temperature reading exceeds its safe maximum, **When** the user runs
   the tool, **Then** an alert is recorded identifying the sensor, the offending value, and the
   reading's timestamp, and the summary lists temperature among the triggered sensors.
3. **Given** a CSV containing multiple out-of-range readings across different sensors, **When**
   the user runs the tool, **Then** each out-of-range reading produces its own alert and the
   summary reports the correct total alert count and the set of distinct sensors that triggered.

---

### User Story 2 - Configure safe thresholds (Priority: P2)

An engineer needs to apply ranges appropriate to a specific process line, because safe limits
for temperature, pressure, and flow rate differ between processes.

**Why this priority**: Configurability is what makes the tool reusable across processes, but a
working default set of thresholds already delivers value, so this ranks below P1.

**Independent Test**: Run the tool against the same CSV with two different threshold
configurations and confirm the set of alerts changes accordingly.

**Acceptance Scenarios**:

1. **Given** a custom safe range for pressure that is narrower than the default, **When** the
   user supplies it and runs the tool, **Then** readings that were previously in range and now
   fall outside the custom range are reported as alerts.
2. **Given** no custom thresholds are supplied, **When** the user runs the tool, **Then** the
   tool applies documented default safe ranges and still produces a valid report.

---

### User Story 3 - Review a run summary report (Priority: P3)

After a run, the engineer wants an at-a-glance summary they can record or share, showing how
many readings were processed, how many alerts fired, and which sensors were involved.

**Why this priority**: The per-alert detail (P1) already conveys the findings; the consolidated
summary improves reporting and record-keeping but is not required for detection to be useful.

**Independent Test**: Run the tool on a known CSV and confirm the printed summary's totals match
the input row count and the number of alerts produced.

**Acceptance Scenarios**:

1. **Given** a completed run, **When** the summary is printed, **Then** it shows the total number
   of readings processed, the total number of alerts, and the distinct sensors that triggered
   at least one alert.
2. **Given** a run with zero alerts, **When** the summary is printed, **Then** it clearly states
   that no sensors triggered alerts.

### Edge Cases

- **Missing input file**: The tool reports a clear, human-readable error and exits without a
  traceback.
- **Malformed CSV / wrong columns**: A row missing expected columns or with non-numeric sensor
  values is reported as a data error identifying the affected row, and processing continues with
  remaining rows (the row is not silently dropped).
- **Empty file or header-only file**: The tool reports zero readings and zero alerts rather than
  failing.
- **Boundary values**: A reading exactly equal to a safe minimum or maximum is treated as
  in-range (range is inclusive); a value just beyond the bound triggers an alert.
- **Missing timestamp on a reading**: The alert still records the reading using a fallback
  indicator (see Assumptions) so no alert is lost.
- **Unknown or extra sensor columns**: Columns beyond the three known sensors are ignored without
  error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST accept a path to a CSV file of sensor readings as input and report a
  clear error if the file does not exist or cannot be read.
- **FR-002**: The tool MUST process readings for three sensor types: temperature, pressure, and
  flow rate.
- **FR-003**: The tool MUST evaluate each sensor value in each reading against a configurable
  safe range (minimum and maximum) for that sensor type.
- **FR-004**: The tool MUST apply documented default safe ranges when no custom thresholds are
  provided, and MUST allow the user to override the safe range for any sensor type.
- **FR-005**: When a value falls outside its safe range, the tool MUST record an alert that
  identifies the sensor type, the offending value, the applicable limit that was breached, and
  the timestamp associated with the reading.
- **FR-006**: The tool MUST treat range boundaries as inclusive — a value equal to the minimum or
  maximum is in range.
- **FR-007**: The tool MUST continue processing subsequent readings after encountering a malformed
  or non-numeric row, and MUST surface a clear message identifying any row it could not evaluate.
- **FR-008**: At the end of a run the tool MUST print a summary report containing the total number
  of readings processed, the total number of alerts raised, and the distinct set of sensors that
  triggered at least one alert.
- **FR-009**: All error and alert output MUST be human-readable, stating what happened in plain
  language without exposing raw stack traces for anticipated error conditions.
- **FR-010**: The tool MUST exit with a success indication when it completes a run (including runs
  with zero alerts) and a distinct failure indication when it cannot perform the run at all (e.g.,
  unreadable input).

### Key Entities

- **Sensor Reading**: A single observation in time consisting of a timestamp and one or more
  sensor values (temperature, pressure, flow rate).
- **Threshold (Safe Range)**: The inclusive minimum and maximum allowed value for a given sensor
  type; configurable, with documented defaults.
- **Alert**: A record produced when a sensor value is outside its safe range; includes the sensor
  type, the value, the breached limit, and the reading's timestamp.
- **Summary Report**: An end-of-run aggregate covering total readings, total alerts, and the
  distinct sensors that triggered alerts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a labeled test file, the tool identifies 100% of out-of-range readings and
  raises zero alerts for in-range readings (no false positives or false negatives).
- **SC-002**: The end-of-run summary's total-readings and total-alerts counts exactly match the
  input data in 100% of runs.
- **SC-003**: A user can change a sensor's safe range and re-run without editing the input data,
  and the alert results reflect the new range.
- **SC-004**: For every anticipated error (missing file, malformed row, empty file), the user
  receives a plain-language message and never an unhandled crash/traceback.
- **SC-005**: A new user can run the tool against a sample file and interpret the alerts and
  summary without external documentation beyond the tool's built-in help.

## Assumptions

- **Input format**: The CSV has a header row and includes a timestamp column plus columns for
  temperature, pressure, and flow rate. Exact column names are resolved during planning; the tool
  matches the three known sensor types by recognizable column names.
- **Timestamp source**: The timestamp recorded in an alert is the reading's own timestamp from the
  CSV. If a reading has no timestamp, the alert uses a clear fallback indicator (e.g., the row
  number) so the alert is still actionable.
- **Threshold configuration**: Custom thresholds are supplied through a documented configuration
  mechanism (e.g., command-line options and/or a small config file); the precise mechanism is a
  planning decision. Sensible default ranges ship with the tool.
- **Alert destination**: Alerts are surfaced to the user as part of the run output; persistence of
  alerts to a separate file is optional and deferred to planning.
- **Scale**: Input files are sized to be processed in a single pass in memory (thousands to low
  millions of rows), not streamed continuously in real time.

## Out of Scope

- Real-time/streaming ingestion directly from live sensors or hardware.
- Notifications via email, SMS, or external alerting systems.
- A graphical or web interface (the tool is command-line only).
- Historical trend analysis, charting, or predictive analytics.
- Multi-file or multi-run aggregation across separate invocations.
