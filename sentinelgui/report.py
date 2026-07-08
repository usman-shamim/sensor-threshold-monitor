"""Batch run summary — generates a one-page PDF report when monitoring ends.

Triggered on emergency stop or window close. Uses fpdf2 for zero-dependency PDF output.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from fpdf import FPDF


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _s(text: str) -> str:
    """Strip Unicode to safe ASCII for the built-in Helvetica font."""
    text = str(text)
    text = text.replace("\u2014", "-")   # em-dash
    text = text.replace("\u2013", "-")   # en-dash
    text = text.replace("\u00b0", " deg ")   # degree
    text = text.replace("\u0394", "dP")     # Greek Delta (Delta-P)
    text = text.replace("\u00d7", "x")      # multiplication sign
    for i in range(10):
        text = text.replace(chr(0x2080 + i), str(i))  # subscript 0-9
    return text.encode("ascii", errors="replace").decode("ascii")


def generate(scenario_name: str, started_at: str | None, seq: int,
             fault_history: list, output_dir: str = ".") -> str | None:
    """
    Build a one-page PDF report from the session data.
    Returns the output file path, or None if nothing to report.
    """
    if not fault_history:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "SENTINELGUI - Batch Run Summary", ln=True, align="C")
    pdf.ln(4)

    # Meta
    duration = "—"
    if started_at:
        try:
            dt = datetime.datetime.fromisoformat(started_at)
            elapsed = datetime.datetime.now() - dt
            m, s = divmod(int(elapsed.total_seconds()), 60)
            duration = f"{m}m {s}s" if m else f"{s}s"
        except Exception:
            pass

    # ASCII-normalize for built-in Helvetica (no Unicode special chars).
    sn = scenario_name.replace("\u2014", "-")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Scenario: {sn}", ln=True)
    pdf.cell(0, 6, f"Duration: {duration}", ln=True)
    pdf.cell(0, 6, f"Readings processed: {seq}", ln=True)
    pdf.cell(0, 6, f"Generated: {_now()}", ln=True)
    pdf.ln(6)

    # Stats
    criticals = [e for e in fault_history if e.severity == "critical"]
    warnings = [e for e in fault_history if e.severity == "warning"]
    shutdowns = [e for e in fault_history if e.fault == "emergency_shutdown"]

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Alarm Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Total alarms: {len(fault_history)}", ln=True)
    pdf.cell(0, 6, f"  Critical: {len(criticals)}", ln=True)
    pdf.cell(0, 6, f"  Warning:  {len(warnings)}", ln=True)
    if shutdowns:
        pdf.cell(0, 6, f"  Emergency shutdowns: {len(shutdowns)}", ln=True)
    pdf.ln(6)

    # Fault count
    fault_counts: dict[str, int] = {}
    for e in fault_history:
        if e.fault and e.fault != "emergency_shutdown":
            fault_counts[e.fault] = fault_counts.get(e.fault, 0) + 1
    if fault_counts:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Faults Detected", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for fname, count in sorted(fault_counts.items(), key=lambda x: -x[1]):
            label = fname.replace("_", " ").title()
            pdf.cell(0, 6, f"  {label}  x{count}", ln=True)
        pdf.ln(6)

    # Timeline
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Event Timeline", ln=True)
    pdf.set_font("Helvetica", "", 9)

    col_time = 42
    col_sev = 22
    col_sensor = 30
    col_detail = pdf.w - col_time - col_sev - col_sensor - pdf.l_margin - pdf.r_margin

    # Header
    pdf.set_fill_color(30, 30, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col_time, 6, "Time", border=0, fill=True)
    pdf.cell(col_sev, 6, "Sev", border=0, fill=True)
    pdf.cell(col_sensor, 6, "Sensor", border=0, fill=True)
    pdf.cell(col_detail, 6, "Detail", border=0, fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)

    for entry in fault_history:
        ts = _s(entry.timestamp[:19]) if entry.timestamp else "-"
        sev = entry.severity.upper() if entry.severity != "critical" else "CRIT"
        sensor = _s(entry.sensor[:20]) if entry.sensor else "-"
        detail = _s(entry.explanation[:70]) if entry.explanation else entry.fault
        pdf.cell(col_time, 5, _s(ts))
        pdf.cell(col_sev, 5, sev)
        pdf.cell(col_sensor, 5, _s(sensor))
        pdf.cell(col_detail, 5, _s(detail), ln=True)

    # Footer
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"SentinelGUI - Generated {_now()}", ln=True, align="C")

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sentinelgui_report_{ts}.pdf"
    filepath = str(Path(output_dir) / filename)
    pdf.output(filepath)
    return filepath
