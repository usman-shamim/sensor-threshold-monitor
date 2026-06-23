# Contract: Serial Protocol (Arduino ⇄ SentinelGUI)

Single USB serial link. 115200 baud, 8N1 (configurable in `gui_config.json`). UTF-8/ASCII, line
oriented (`\n` terminated).

## 1. Arduino → GUI : data frames (~1 Hz)

```
<temperature>,<flow_rate>,<pressure>\n
```
- Three numeric fields, fixed order, comma-separated. Example: `72.4,31.8,3.21`
- Decimal point `.`; optional surrounding spaces tolerated.
- Lines beginning with `#` are comments and ignored.
- Optional status line (ignored for plotting, may be shown in status bar): `#STATUS:<text>`

### Parser rules (GUI side — `acquisition.parse_frame`)
- Strip; ignore empty and `#`-prefixed lines.
- Split on `,` → must be exactly 3 tokens, each parseable as `float` and finite.
- On success → `{"temperature": t, "flow_rate": f, "pressure": p}` (raw units).
- On failure → return `None`; caller increments the malformed-frame counter (FR-004). Never raises,
  never alarms.

## 2. GUI → Arduino : commands

```
CMD:STOP\n        # Emergency Shutdown — cut pump relay
CMD:PING\n        # optional liveness probe
```
- Firmware MAY reply: `ACK:STOP\n` / `ACK:PING\n`.
- The GUI writes the command and waits up to ~1 s for an `ACK:` line.

### Emergency-stop outcome mapping (`shutdown_controller`)
| Situation | `hardware_outcome` |
|-----------|--------------------|
| Bytes written **and** `ACK:STOP` received ≤1 s | `acked` |
| Bytes written, no ACK (write-only / no firmware support) | `sent` |
| Serial write raises / port closed | `failed` |
| Running on simulator (no serial) | `no_channel` |

In all cases the UI safe state is latched first (FR-020), then the command is attempted (FR-021).

## 3. Timing & errors
- Read timeout ~1 s. Two consecutive missed frames → `DataSource.status = disconnected`; kiosk mode
  auto-switches to simulator (FR-002, FR-028).
- Reconnect: reopening the port resumes `connected:serial`.
- All serial exceptions are caught and surfaced as plain status text (Principle V); the UI thread is
  never blocked (reads happen on the background thread).

## 4. Simulator equivalence
`simulator.py` emits the **same** `{"temperature","flow_rate","pressure"}` dicts at 1 Hz through the
identical queue path, so every downstream module is source-agnostic (FR-003, SC-003). Fault
injection nudges the relevant fields toward the signatures in data-model.md.
