"""TracePanel — visible reasoning trace for the ReAct agent.

Renders the agent's Observe→Reason→Act entries below the mimic diagram,
colour-coded by severity (critical/red, warning/amber, cleared/green).
"""

from __future__ import annotations

import customtkinter as ctk

from . import theme

_SEVERITY_ORDER = {"critical": 0, "warning": 1, "cleared": 2}

PLACEHOLDER = "No alerts yet — trace will appear when alarms fire."


class TracePanel(ctk.CTkFrame):
    def __init__(self, parent, kiosk: bool = False):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=8)
        self._kiosk = kiosk
        self._font = theme.font(11, kiosk=kiosk)

        header = ctk.CTkLabel(
            self, text="Reasoning Trace", text_color=theme.MUTED,
            font=theme.font(11, bold=True, kiosk=kiosk))
        header.pack(anchor="w", padx=10, pady=(8, 0))

        self._text = ctk.CTkTextbox(self, wrap="word", font=self._font,
                                     fg_color=theme.BG, text_color=theme.TEXT,
                                     border_width=0, corner_radius=0)
        self._text.pack(fill="both", expand=True, padx=6, pady=(4, 6))

        self._text.tag_config("critical", foreground=theme.ZONE_COLORS["critical"])
        self._text.tag_config("warning", foreground=theme.ZONE_COLORS["warning"])
        self._text.tag_config("cleared", foreground=theme.ZONE_COLORS["normal"])

        self._clear_btn = ctk.CTkButton(
            self, text="Clear", width=70, height=26,
            fg_color=theme.PANEL_LIGHT, hover_color="#374151",
            font=theme.font(11, kiosk=kiosk),
            command=self.clear)
        self._clear_btn.pack(side="bottom", anchor="e", padx=8, pady=(0, 6))

        self._show_placeholder()

    def update_trace(self, entries: list):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")

        if not entries:
            self._show_placeholder()
            self._text.configure(state="disabled")
            return

        for entry in entries:
            for sev in ("critical", "warning", "cleared"):
                if f"[{sev}]" in entry:
                    break
            else:
                sev = "cleared"

            # Colour the first line (timestamp + severity badge) only.
            start = self._text.index("end-1c")
            self._text.insert("end", entry + "\n\n")
            end = self._text.index("end-1c")
            first_len = len(entry.split("\n")[0])
            line_end = f"{int(str(start).split('.')[0])}.{first_len}"
            self._text.tag_add(sev, start, line_end)

        self._text.configure(state="disabled")
        self._text.see("end")

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")
        self._show_placeholder()

    def _show_placeholder(self):
        self._text.configure(state="normal")
        self._text.insert("1.0", PLACEHOLDER)
        self._text.configure(state="disabled")
