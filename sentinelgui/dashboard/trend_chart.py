"""Real-time trend chart per sensor (FR-015), Matplotlib embedded via FigureCanvasTkAgg."""

from __future__ import annotations

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from . import theme


class TrendChart(ctk.CTkFrame):
    def __init__(self, parent, sensor_key: str, label: str, kiosk: bool = False):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=10)
        self.sensor_key = sensor_key

        self._fig = Figure(figsize=(3.2, 1.6), dpi=100, facecolor=theme.PANEL)
        self._ax = self._fig.add_subplot(111)
        self._style_axes(label)
        self._line, = self._ax.plot([], [], color=theme.ACCENT, linewidth=1.6)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

    def _style_axes(self, label):
        self._ax.set_facecolor(theme.PANEL)
        self._ax.set_title(label, color=theme.MUTED, fontsize=9, loc="left")
        self._ax.tick_params(colors=theme.MUTED, labelsize=7)
        for spine in self._ax.spines.values():
            spine.set_color(theme.PANEL_LIGHT)

    def update_series(self, series: list[float]) -> None:
        if not series:
            return
        xs = list(range(len(series)))
        self._line.set_data(xs, series)
        self._ax.set_xlim(0, max(10, len(series)))
        low, high = min(series), max(series)
        pad = (high - low) * 0.1 or 1.0
        self._ax.set_ylim(low - pad, high + pad)
        self._canvas.draw_idle()
