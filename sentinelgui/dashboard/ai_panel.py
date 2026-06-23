"""Diagnosis panel (FR-012, FR-014): rule-based explanation + optional 'Explain with AI'.

The rule-based text shows immediately on every diagnosis. 'Explain with AI' is an on-demand
enrichment; while it runs the panel stays responsive and falls back cleanly if AI is
unavailable or times out.
"""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from . import theme


class AIPanel(ctk.CTkFrame):
    def __init__(self, parent, on_explain: Callable[[], None], kiosk: bool = False):
        super().__init__(parent, fg_color=theme.PANEL, corner_radius=10)
        self._on_explain = on_explain
        self._kiosk = kiosk

        ctk.CTkLabel(self, text="Diagnosis", text_color=theme.MUTED,
                     font=theme.font(14, kiosk=kiosk)).pack(anchor="w", padx=12, pady=(10, 0))

        self._fault = ctk.CTkLabel(self, text="—", text_color=theme.TEXT, anchor="w",
                                   font=theme.font(20, bold=True, kiosk=kiosk))
        self._fault.pack(anchor="w", padx=12, pady=(2, 0))

        self._explanation = ctk.CTkLabel(self, text="No active fault.", text_color=theme.MUTED,
                                         anchor="w", justify="left", wraplength=460,
                                         font=theme.font(12, kiosk=kiosk))
        self._explanation.pack(anchor="w", padx=12, pady=(2, 6), fill="x")

        self._ai_text = ctk.CTkLabel(self, text="", text_color=theme.ACCENT, anchor="w",
                                     justify="left", wraplength=460,
                                     font=theme.font(12, kiosk=kiosk))
        self._ai_text.pack(anchor="w", padx=12, pady=(0, 6), fill="x")

        self._button = ctk.CTkButton(self, text="Explain with AI", command=self._clicked,
                                     fg_color=theme.ACCENT, font=theme.font(12, bold=True, kiosk=kiosk))
        self._button.pack(anchor="w", padx=12, pady=(0, 12))
        self._button.configure(state="disabled")

    def _clicked(self):
        self._ai_text.configure(text="Asking AI…", text_color=theme.MUTED)
        self._button.configure(state="disabled")
        self._on_explain()

    def update_diagnosis(self, diagnosis) -> None:
        if diagnosis is None:
            self._fault.configure(text="—")
            self._explanation.configure(text="No active fault.")
            self._ai_text.configure(text="")
            self._button.configure(state="disabled")
            return
        self._fault.configure(text=diagnosis.fault.replace("_", " ").title())
        tag = "(rule-based)" if diagnosis.source == "rule" else "(AI)"
        self._explanation.configure(text=f"{diagnosis.explanation}  {tag}")
        self._button.configure(state="normal")

    def show_ai_result(self, text: Optional[str]) -> None:
        if text:
            self._ai_text.configure(text=f"AI: {text}", text_color=theme.ACCENT)
        else:
            self._ai_text.configure(text="AI unavailable — showing rule-based diagnosis.",
                                    text_color=theme.MUTED)
        self._button.configure(state="normal")
