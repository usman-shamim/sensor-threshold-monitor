# SentinelGUI Quickstart

A SCADA-style desktop dashboard for the reactor cooling-loop demo rig. Runs fully offline; an
Arduino is optional thanks to the built-in fault simulator.

## Prerequisites
- Python 3.12
- Dependencies (SentinelGUI only — SentinelCLI stays standard-library-only):
  ```
  pip install pyserial pandas customtkinter matplotlib
  ```
  (These will be pinned in a `sentinelgui/requirements.txt` during implementation.)

## Run with no hardware (simulator) — recommended for demos/testing
```
python -m sentinelgui --simulate
```
- The dashboard opens with a live 1 Hz stream.
- Use the **Inject Fault** control to trigger: blockage, pump failure, cavitation, fouling,
  thermal runaway, cooling failure — watch the matching card/zone, mimic stage highlight, alarm,
  and rule-based diagnosis appear.

## Run with the Arduino rig
```
python -m sentinelgui --port COM3        # Windows
python -m sentinelgui --port /dev/ttyUSB0 # Linux/macOS
```
- Firmware should emit `temperature,flow_rate,pressure` lines at ~1 Hz, 115200 baud
  (see `contracts/serial-protocol.md`).
- Open/close the physical valves to induce faults; the dashboard reacts within ~2 s.
- If the port can't be opened or drops, the app falls back to the simulator (kiosk mode auto-recovers).

## Exhibition / Kiosk mode
```
python -m sentinelgui --simulate --kiosk
```
Fullscreen, enlarged fonts/cards, simplified controls, confirmation guards on destructive actions.

## Optional AI diagnosis
- Rule-based diagnosis always works offline.
- For the richer **"Explain with AI"** button, set the SentinelCLI key (no key is ever hardcoded):
  ```
  export GEMINI_API_KEY=...        # PowerShell: $env:GEMINI_API_KEY="..."
  ```
- Without a key or network, the button gracefully falls back to the rule-based text.

## Recording a session
- Click **Start Recording** → readings stream to `sentinelgui_YYYYMMDD_HHMMSS.csv` in the configured
  directory. **Stop Recording** closes the file. If the location is unwritable, you're warned and
  monitoring continues.

## Emergency Shutdown
- The red **Emergency Shutdown** button latches a SHUTDOWN safe state immediately and attempts a
  `CMD:STOP` to the rig. It reports whether hardware was actuated (`acked`/`sent`) or not
  (`failed`/`no channel`). Resuming requires an explicit confirmation.

## Run the tests
```
pytest sentinelgui/tests/        # SentinelGUI logic modules
pytest test_project.py           # SentinelCLI — still green, unchanged
```

## Validation checklist (maps to spec Success Criteria)
- [ ] `--simulate` runs the full dashboard with no hardware, no errors (SC-003).
- [ ] Crossing a threshold updates card + alarm within 2 s (SC-001).
- [ ] Each of the six faults is correctly identified when injected (SC-002).
- [ ] Works with networking disabled; AI button falls back cleanly (SC-005, SC-006).
- [ ] Recorded CSV opens in a spreadsheet, one row per reading (SC-007).
- [ ] Emergency Shutdown latches the UI in <1 s and logs the event (SC-008).
