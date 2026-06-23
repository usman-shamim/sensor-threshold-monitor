# Contract: Module Interfaces (internal API)

SentinelGUI has no network API; its "contracts" are the public signatures of the nine modules.
Each headless module is independently unit-testable. Signatures are indicative, not final.

## Module 1 — `acquisition.py` (Serial Data Acquisition)
```python
def parse_frame(line: str) -> dict[str, float] | None: ...   # pure; tested without a port
class SerialDataAcquisition:
    def __init__(self, port: str, baud: int, out_queue: "queue.Queue", read_timeout_s: float = 1.0): ...
    def start(self) -> None: ...        # spawns background read thread
    def stop(self) -> None: ...
    def send_command(self, cmd: str) -> bool: ...   # returns True if bytes written
    @property
    def status(self) -> str: ...        # connected | disconnected | error
```

## Module 1b — `simulator.py` (Fault Simulator)
```python
class FaultSimulator:
    def __init__(self, out_queue: "queue.Queue", tick_s: float = 1.0): ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def inject(self, fault: str) -> None: ...   # one of the fault keys
    def clear_fault(self) -> None: ...
    def next_frame(self) -> dict[str, float]: ...   # pure-ish; tested directly
```

## Module 2 — `process_engine.py`
```python
def to_engineering(raw: dict[str, float]) -> dict[str, float]: ...   # raw -> °C, L/min, bar
def build_reading(raw: dict[str, float], seq: int, source: str, now: str) -> Reading: ...
```

## `thresholds.py`
```python
def load_thresholds(path: str | None = None) -> dict[str, ThresholdBand]: ...  # validates nesting
def zone_of(sensor: str, value: float, bands: dict) -> str: ...   # normal|warning|critical
# zone_of reuses SentinelCLI check_reading per band (see sentinelcli-bridge.md)
```

## Module 8 — `alarm_manager.py`
```python
class AlarmManager:
    def __init__(self, bands: dict, debounce_samples: int = 2): ...
    def evaluate(self, reading: Reading) -> list[Alarm]: ...   # state changes since last reading
    @property
    def active(self) -> list[Alarm]: ...
    @property
    def history(self) -> list[Alarm]: ...
```

## Module 3 — `fault_engine.py`
```python
def classify(reading: Reading, window: ReadingWindow, active: list[Alarm]) -> FaultDiagnosis: ...
def slope(window: ReadingWindow, sensor: str, n: int) -> float: ...   # pure helper
```

## Module 4 — `react_agent.py`
```python
class ReActAgent:
    def __init__(self, alarms: AlarmManager, faults, bridge, window: ReadingWindow): ...
    def step(self, reading: Reading) -> AgentResult: ...   # observe->reason->act (no AI)
    def request_ai(self, diagnosis: FaultDiagnosis, on_done) -> None: ...  # async worker
# AgentResult: {reading, new_alarms, cleared_alarms, diagnosis, stage_health}
```

## Module 5 — `sentinelcli_bridge.py`
```python
def alarm_to_cli_alert(alarm: Alarm) -> dict: ...      # -> SentinelCLI alert dict
def ai_diagnose(alarm: Alarm, timeout_s: float = 10.0, client=None) -> str | None: ...
```
(See sentinelcli-bridge.md for the mapping and threading.)

## Module 7 — `data_logger.py`
```python
class DataLogger:
    def __init__(self, directory: str): ...
    def start(self) -> RecordingSession: ...   # opens timestamped CSV; error state if unwritable
    def write(self, reading: Reading, alarms: list[Alarm]) -> None: ...
    def stop(self) -> RecordingSession: ...
```

## Module 9 — `shutdown_controller.py`
```python
class ShutdownController:
    def __init__(self, source): ...
    def trigger(self, by: str = "operator") -> ShutdownEvent: ...   # latch UI safe state + CMD:STOP
    def resume(self) -> None: ...                                   # requires explicit confirm upstream
```

## Module 6 — `dashboard/*` (views)
Thin CustomTkinter/Matplotlib widgets driven by `AppController`. Each `update(state)` is a pure
render of the latest model objects; no business logic lives in widgets (keeps logic testable).
`AppController` owns the `queue.Queue`, the `root.after(250, drain)` loop, and wiring.

## Test contract
Every module above (except `dashboard/*`) has a `test_<module>.py` under `sentinelgui/tests/`
covering a normal case and at least one edge/error case (Constitution Principle III, adapted).
