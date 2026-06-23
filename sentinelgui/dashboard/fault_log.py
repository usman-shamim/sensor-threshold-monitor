"""Fault history log (FR-018): per-alarm timestamp, sensor, value, severity, diagnosis."""

from __future__ import annotations

import customtkinter as ctk

from . import theme


class FaultLog(ctk.CTkFrame):
    def __init__(self, parent, kiosk: bool = False):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=10)
        self._kiosk = kiosk
        ctk.CTkLabel(self, text="Fault History", text_color=theme.MUTED,
                     font=theme.font(14, kiosk=kiosk)).pack(anchor="w", padx=12, pady=(10, 4))
        self._list = ctk.CTkScrollableFrame(self, fg_color=theme.PANEL)
        self._list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._rows: list = []
        self._count = 0

    def update_history(self, entries: list) -> None:
        # Append-only: only render newly added entries to keep it cheap.
        if len(entries) == self._count:
            return
        for entry in entries[self._count:]:
            color = theme.SEVERITY_COLORS.get(entry.severity, theme.MUTED)
            text = (f"{entry.timestamp}  [{entry.severity}] {entry.sensor}={entry.value:.1f} "
                    f"→ {entry.fault}")
            row = ctk.CTkLabel(self._list, text=text, text_color=color, anchor="w",
                               justify="left", wraplength=520,
                               font=theme.font(11, kiosk=self._kiosk))
            row.pack(fill="x", padx=6, pady=2)
            self._rows.append(row)
        self._count = len(entries)
