"""Alarm panel (FR-007): active Warning/Critical alarms, visually distinguished."""

from __future__ import annotations

import customtkinter as ctk

from . import theme


class AlarmPanel(ctk.CTkFrame):
    def __init__(self, parent, kiosk: bool = False):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=10)
        self._kiosk = kiosk
        ctk.CTkLabel(self, text="Alarms", text_color=theme.MUTED,
                     font=theme.font(14, kiosk=kiosk)).pack(anchor="w", padx=12, pady=(10, 4))
        self._list = ctk.CTkScrollableFrame(self, fg_color=theme.PANEL)
        self._list.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._rows: list = []

    def update_alarms(self, alarms: list) -> None:
        for row in self._rows:
            row.destroy()
        self._rows.clear()
        if not alarms:
            empty = ctk.CTkLabel(self._list, text="No active alarms", text_color=theme.MUTED,
                                 font=theme.font(12, kiosk=self._kiosk))
            empty.pack(anchor="w", padx=6, pady=4)
            self._rows.append(empty)
            return
        for alarm in alarms:
            color = theme.SEVERITY_COLORS.get(alarm.severity, theme.MUTED)
            text = (f"{alarm.severity.upper()}  {alarm.sensor}={alarm.value:.1f} "
                    f"({alarm.limit} {alarm.bound})")
            row = ctk.CTkLabel(self._list, text=text, text_color="#ffffff", fg_color=color,
                               corner_radius=6, anchor="w",
                               font=theme.font(12, bold=True, kiosk=self._kiosk))
            row.pack(fill="x", padx=6, pady=3)
            self._rows.append(row)
