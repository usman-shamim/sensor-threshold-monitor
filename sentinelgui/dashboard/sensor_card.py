"""Live sensor card widget — value, unit, and normal/warning/critical status (FR-005).

Thin view: it renders whatever the controller passes; no threshold logic here.
"""

from __future__ import annotations

import customtkinter as ctk

from . import theme


class SensorCard(ctk.CTkFrame):
    def __init__(self, parent, sensor_key: str, label: str, unit: str, kiosk: bool = False):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=10)
        self.sensor_key = sensor_key
        self.unit = unit
        self._kiosk = kiosk

        self._label = ctk.CTkLabel(self, text=label, text_color=theme.MUTED,
                                   font=theme.font(14, kiosk=kiosk))
        self._label.pack(anchor="w", padx=14, pady=(12, 0))

        self._value = ctk.CTkLabel(self, text="--", text_color=theme.TEXT,
                                   font=theme.font(40, bold=True, kiosk=kiosk))
        self._value.pack(anchor="w", padx=14)

        self._status = ctk.CTkLabel(self, text="NORMAL", text_color=theme.TEXT,
                                    fg_color=theme.ZONE_COLORS["normal"], corner_radius=6,
                                    font=theme.font(12, bold=True, kiosk=kiosk))
        self._status.pack(anchor="w", padx=14, pady=(4, 14))

    def update_value(self, value: float, zone: str) -> None:
        self._value.configure(text=f"{value:.1f} {self.unit}")
        self._status.configure(text=zone.upper(), fg_color=theme.ZONE_COLORS.get(zone, theme.MUTED))

    def update_label(self, label: str, unit: str) -> None:
        self._label.configure(text=label)
        self.unit = unit
