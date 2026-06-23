# Phase 0 Research: SentinelGUI

All unknowns from Technical Context resolved below. Format: Decision / Rationale / Alternatives.

## R1 — Serial frame format (Arduino → GUI)

**Decision**: Newline-delimited ASCII CSV, one frame per line at ~1 Hz:
`temperature,flow_rate,pressure\n` (three floats in engineering or raw units). The GUI parser
tolerates extra whitespace, ignores blank/comment lines (`#...`), and discards any line that does
not parse into three numbers (counted as a malformed frame, never an alarm).

**Rationale**: Trivial to emit from an Arduino Nano `Serial.println`, human-debuggable in a serial
monitor, and matches SentinelCLI's existing CSV mental model (`temperature,flow_rate,pressure`).
Fixed field order avoids per-frame key parsing at 1 Hz.

**Alternatives**: JSON per line (more robust/self-describing but heavier to emit on an 8-bit MCU and
overkill for three fixed fields); binary packed struct (fastest, but undebuggable and brittle to
endianness — unjustified at 1 Hz).

## R2 — Command channel (GUI → Arduino) for Emergency Shutdown

**Decision**: A line command `CMD:STOP\n` written to the same serial port. The firmware is expected
to cut the pump relay on receipt and may reply `ACK:STOP`. The GUI treats the write as best-effort:
success = bytes written (and ACK if present within ~1 s); otherwise it reports "hardware not
actuated" while still latching the UI safe state (FR-020/FR-021).

**Rationale**: Reuses the one open port, requires no extra wiring, and gives a clean
success/fallback signal. Read-only rigs simply never ACK and the GUI degrades gracefully.

**Alternatives**: Separate control port/GPIO (more wiring, not available on a single USB link);
no command at all / UI-only (rejected — the user chose "Both, with graceful fallback").

## R3 — Baud rate & connection handling

**Decision**: 115200 baud, 8N1, configurable in `gui_config.json` (`serial.port`, `serial.baud`).
On startup, if no port is configured/openable, the app enters simulation mode. A read timeout
(~1 s) lets the background thread detect disconnects and surface a "disconnected" state; in kiosk
mode it auto-falls back to the simulator (FR-028).

**Rationale**: 115200 is reliable on the Nano's USB-serial and leaves ample headroom over 1 Hz×3
floats. Configurable port avoids hard-coding `COM3`/`/dev/ttyUSB0` across machines.

**Alternatives**: 9600 (works but needlessly slow); auto-detect port by scanning (nice-to-have,
deferred — explicit config is more predictable for an exhibition).

## R4 — UI concurrency model (CustomTkinter + Matplotlib + 1 Hz thread)

**Decision**: One **background acquisition thread** owns the serial port (or simulator) and pushes
`Reading` objects onto a `queue.Queue`. The **Tk main thread** polls the queue on a periodic
`root.after(250, ...)` tick, draining all available readings and updating widgets/charts. No Tk
call is ever made from the background thread. AI runs in a **separate worker thread** with a ~10 s
timeout, delivering its result back via the same queue/`after` mechanism.

**Rationale**: Tkinter is not thread-safe; the queue + `after()` pattern is the canonical, robust
way to feed a Tk UI from a producer thread, and keeps the UI responsive and the E-stop button live
regardless of serial/AI latency (Constraints, SC-006, SC-008).

**Alternatives**: `root.after`-driven blocking serial reads on the UI thread (would freeze the UI on
disconnect); `asyncio` integration with Tk (added complexity for a 1 Hz workload); multiprocessing
(unneeded — work is I/O-bound, not CPU-bound).

## R5 — Two-band thresholds and reuse of SentinelCLI `check_reading`

**Decision**: `gui_config.json` stores, per sensor, a `critical {min,max}` (seeded from SentinelCLI
`config.json`) and a `warning {min,max}` nested inside it (default ~10% inside each bound). Zone
evaluation reuses SentinelCLI's `check_reading(reading, thresholds)` **twice** — once against the
critical band, once against the warning band — to classify each value as normal/warning/critical
without reimplementing range logic. Bounds remain inclusive (equal to a bound = inside), matching
SentinelCLI and the spec edge case.

**Rationale**: Maximises reuse of already-tested SentinelCLI logic, guarantees CLI/GUI agree on
"in-range", and keeps the two-band rule declarative in config.

**Alternatives**: A bespoke GUI range checker (duplicates tested code, risks divergence); a single
band with derived warning (rejected in clarification in favour of two explicit, tunable bands).

## R6 — Fault classification (hybrid: values + rate-of-change)

**Decision**: `fault_engine` consumes the current `Reading` plus a `ReadingWindow` (rolling buffer)
and computes, per sensor, the current zone and a short-term slope (Δ over the last N samples). It
matches against ordered signatures (first strong match wins; otherwise "undetermined"):

| Fault | Signature (values + trend) |
|-------|----------------------------|
| Blockage | flow ↓ (low/critical) **and** pressure ↑ (rising/high) |
| Pump failure | flow ↓↓ (near zero) **and** pressure ↓ (dropping) together |
| Cavitation | pressure low **and** high variance/oscillation in pressure (and/or flow) |
| Fouling | temperature slowly ↑ **and** flow mildly ↓ over a sustained window (gradual) |
| Thermal runaway | temperature ↑↑ with high positive slope, breaching critical, flow ~normal |
| Cooling failure | temperature sustained ↑ above limit while flow is adequate (no cooling effect) |

Thermal runaway vs cooling failure are disambiguated by **rate** (runaway = fast slope; cooling
failure = slower, sustained). Multiple simultaneous matches are ranked by severity.

**Rationale**: Pure absolute thresholds cannot separate blockage (flow↓/pressure↑) from pump
failure (flow↓/pressure↓) or runaway (fast) from cooling loss (slow) — the rolling-window slope is
required (clarification answer). Ordered signatures keep the rules explicit and unit-testable.

**Alternatives**: ML/statistical classifier (needs training data, opaque to judges, offline-hostile);
absolute-only rules (cannot distinguish the dynamic faults above).

## R7 — ReAct agent shape (Module 4)

**Decision**: A lightweight, rule-based **Observe → Reason → Act** cycle invoked once per reading:
- **Observe**: ingest the new `Reading`, append to `ReadingWindow`, get zones from `alarm_manager`.
- **Reason**: if any breach, ask `fault_engine` for the most likely `FaultDiagnosis` (rule-based).
- **Act**: raise/clear alarms, append fault-history entries, drive mimic/chart state, and — only on
  explicit user request — dispatch the AI worker for an enriched explanation.

It is deterministic and offline; "AI" is an optional Act branch, not a required reasoning step.

**Rationale**: Gives the spec's diagnosis flow a clear, testable control loop and a natural seam for
the on-demand AI without coupling reasoning to the network (offline-first, SC-005/SC-006).

**Alternatives**: An LLM-driven agent loop (violates offline-first and is non-deterministic for an
exhibition); no agent abstraction (logic scattered across UI callbacks — harder to test).

## R8 — Pandas vs deque (rolling window & CSV)

**Decision**: Use a `collections.deque(maxlen=window)` for the live `ReadingWindow` (charts +
slope) — O(1) append, bounded memory. Use **pandas** in `data_logger` to buffer recorded rows and
write/append the session CSV (and for any post-hoc tabular export), satisfying the requested stack
without putting pandas on the hot per-frame path.

**Rationale**: A deque is the right structure for a fixed-length real-time buffer; pandas earns its
place at the I/O/export boundary where its CSV handling and column typing are convenient. Keeps the
1 Hz loop allocation-light.

**Alternatives**: Pandas DataFrame as the live buffer (heavier per-append, more GC churn at 1 Hz);
stdlib `csv` only (works, but the user specified pandas and it eases export/typing).

## R9 — Data-retention defaults (deferred from clarification)

**Decision** (to confirm at implementation): rolling window / trend view = **~5 minutes (≈300
samples @ 1 Hz)**; fault history = **session-only** (cleared on restart, persisted only if recording
is on); CSV recording is **manual** start/stop (not auto-started) writing to a user-chosen directory
with a `sentinelgui_YYYYMMDD_HHMMSS.csv` timestamped filename. These live in `gui_config.json`.

**Rationale**: 5 minutes is enough trend context for an exhibition without unbounded memory; manual
recording avoids surprise disk growth and gives presenters control; timestamped names prevent
overwrite.

**Alternatives**: Auto-record at launch (continuous capture, but risks large files unattended);
cross-session history DB (out of scope per spec).

## R10 — Exhibition/Kiosk mode & 15-inch display layout

**Decision**: A `--kiosk` launch flag (and in-app toggle) enables fullscreen, enlarged fonts/cards,
a simplified control set, confirmation dialogs on destructive actions (E-stop, resume, clear), and
auto-recovery into the simulator on serial loss. Layout targets ≥1920×1080 on a 15-inch panel: a
SCADA grid — top row of three large sensor cards, center mimic diagram, right alarm panel + AI
panel, bottom trend charts + status bar with a prominent red Emergency Shutdown button.

**Rationale**: Directly satisfies FR-028 and the "small SCADA system on a 15-inch laptop" goal;
fullscreen + large type suits judges/visitors at a distance.

**Alternatives**: Single layout for all (less robust unattended); web UI (adds a server/browser
dependency, against the single-laptop offline constraint).
