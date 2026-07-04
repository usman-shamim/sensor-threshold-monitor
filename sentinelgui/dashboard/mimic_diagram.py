"""Process mimic diagram (FR-016): Reservoir → Pump → Flow → Pressure → Reactor → Reservoir.

Drawn on a plain Tk canvas; the stage tied to an active fault is highlighted by colour.
"""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from ..models import PROCESS_STAGES
from . import theme

class MimicDiagram(ctk.CTkFrame):
    def __init__(self, parent, kiosk: bool = False, stages=None):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=10)
        self._stages = tuple(stages) if stages else PROCESS_STAGES
        title = ctk.CTkLabel(self, text="Process Mimic", text_color=theme.MUTED,
                             font=theme.font(14, kiosk=kiosk))
        title.pack(anchor="w", padx=12, pady=(10, 0))
        self._canvas = tk.Canvas(self, bg=theme.PANEL, highlightthickness=0, height=100)
        self._canvas.pack(fill="both", expand=True, padx=10, pady=6)
        self._nodes: dict[str, int] = {}
        self._labels: dict[str, int] = {}
        self._canvas.bind("<Configure>", lambda e: self._draw())

    def _draw(self, **kwargs) -> None:
        if not hasattr(self, "_nodes"):
            return
        self._canvas.delete("all")
        self._nodes.clear()
        self._labels.clear()
        cw = self._canvas.winfo_width() or 600
        ch = self._canvas.winfo_height() or 100
        n = len(self._stages)
        margin = 10
        gap = max(8, cw // (n * 8))
        node_w = max(50, (cw - 2 * margin - gap * (n - 1)) // n)
        node_h = max(30, ch - 20)
        y = (ch - node_h) // 2
        x = margin
        prev = None
        for stage in self._stages:
            rect = self._canvas.create_rectangle(
                x, y, x + node_w, y + node_h, fill=theme.ZONE_COLORS["normal"],
                outline=theme.PANEL_LIGHT, width=2,
            )
            text = self._canvas.create_text(
                x + node_w / 2, y + node_h / 2, text=stage, fill="#ffffff",
                font=theme.font(9, bold=True), width=node_w - 6,
            )
            self._nodes[stage] = rect
            self._labels[stage] = text
            if prev is not None:
                self._canvas.create_line(prev, y + node_h / 2, x, y + node_h / 2,
                                         fill=theme.MUTED, width=2, arrow=tk.LAST)
            prev = x + node_w
            x += node_w + gap

    def update_health(self, stage_health: dict) -> None:
        if not self._nodes:
            self._draw()
        for stage, rect in self._nodes.items():
            health = stage_health.get(stage, "normal")
            self._canvas.itemconfigure(rect, fill=theme.ZONE_COLORS.get(health, theme.ZONE_COLORS["normal"]))
