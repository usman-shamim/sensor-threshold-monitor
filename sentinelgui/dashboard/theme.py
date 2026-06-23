"""Shared colour palette and fonts for the SCADA dark theme."""

BG = "#10141a"
PANEL = "#1b212b"
PANEL_LIGHT = "#252d3a"
TEXT = "#e6edf3"
MUTED = "#8b97a7"

ZONE_COLORS = {
    "normal": "#2e7d32",
    "warning": "#f9a825",
    "critical": "#c62828",
}

SEVERITY_COLORS = {
    "warning": "#f9a825",
    "critical": "#c62828",
}

ACCENT = "#1f6feb"
SHUTDOWN_BG = "#7f1d1d"


def font(size=14, bold=False, kiosk=False):
    scale = 1.4 if kiosk else 1.0
    weight = "bold" if bold else "normal"
    return ("Segoe UI", int(size * scale), weight)
