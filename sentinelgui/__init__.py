"""SentinelGUI — desktop SCADA-style monitor and fault-diagnosis dashboard.

A reactor cooling-loop monitoring application that ingests temperature, flow-rate, and
pressure readings (from an Arduino over USB serial or a built-in fault simulator),
evaluates them against two-band Warning/Critical thresholds, raises alarms, and explains
the likely physical fault with always-available rule-based diagnosis and optional
AI enrichment reused from SentinelCLI.

Business logic lives in importable modules; the ``dashboard`` subpackage holds thin
CustomTkinter/Matplotlib views (Constitution v3.0.0, Principle II).
"""

__version__ = "0.1.0"
