"""Module 6 — Industrial Dashboard main window.

Composes the SCADA layout (sensor cards, trend charts, process mimic, alarm panel, fault
log, diagnosis panel) and the control bar (recording, fault injection, emergency shutdown).
It is the View: its ``update(state)`` is a pure render of the model snapshot the
``AppController`` passes each tick; all logic lives in the headless modules.
"""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ..models import SENSOR_KEYS, SENSOR_LABELS, SENSOR_UNITS
from ..simulator import FAULT_TARGETS
from . import theme
from .ai_panel import AIPanel
from .alarm_panel import AlarmPanel
from .fault_log import FaultLog
from .mimic_diagram import MimicDiagram
from .sensor_card import SensorCard
from .trend_chart import TrendChart


class MainWindow:
    """The dashboard view, driven by an ``AppController``."""

    def __init__(self, controller, kiosk: bool = False):
        self.controller = controller
        self.kiosk = kiosk
        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.title("SentinelGUI — Reactor Cooling Loop Monitor")
        self.root.configure(fg_color=theme.BG)
        self._active_alarm = None
        self._build()
        controller.attach_view(self, self.root)
        if kiosk:
            self.root.attributes("-fullscreen", True)
        else:
            self.root.geometry("1280x800")

    # -- layout ---------------------------------------------------------------
    def _build(self):
        self._build_topbar()
        body = ctk.CTkFrame(self.root, fg_color=theme.BG)
        body.pack(fill="both", expand=True, padx=12, pady=6)

        # Left column: cards + charts. Right column: mimic + alarms + diagnosis + log.
        left = ctk.CTkFrame(body, fg_color=theme.BG)
        left.pack(side="left", fill="both", expand=True)
        right = ctk.CTkFrame(body, fg_color=theme.BG, width=560)
        right.pack(side="right", fill="both", padx=(12, 0))

        cards = ctk.CTkFrame(left, fg_color=theme.BG)
        cards.pack(fill="x")
        self._cards = {}
        self._charts = {}
        for i, key in enumerate(SENSOR_KEYS):
            card = SensorCard(cards, key, SENSOR_LABELS[key], SENSOR_UNITS[key], self.kiosk)
            card.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)
            self._cards[key] = card

        charts = ctk.CTkFrame(left, fg_color=theme.BG)
        charts.pack(fill="both", expand=True, pady=(6, 0))
        for i, key in enumerate(SENSOR_KEYS):
            chart = TrendChart(charts, key, SENSOR_LABELS[key], self.kiosk)
            chart.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            charts.grid_columnconfigure(i, weight=1)
            charts.grid_rowconfigure(0, weight=1)
            self._charts[key] = chart

        self._mimic = MimicDiagram(left, self.kiosk)
        self._mimic.pack(fill="x", pady=(6, 0))

        self._alarms = AlarmPanel(right, self.kiosk)
        self._alarms.pack(fill="both", expand=True)
        self._ai = AIPanel(right, self._on_explain_ai, self.kiosk)
        self._ai.pack(fill="x", pady=(8, 0))
        self._log = FaultLog(right, self.kiosk)
        self._log.pack(fill="both", expand=True, pady=(8, 0))

        self._shutdown_banner = ctk.CTkLabel(
            self.root, text="", fg_color=theme.SHUTDOWN_BG, text_color="#ffffff",
            font=theme.font(20, bold=True, kiosk=self.kiosk))

    def _build_topbar(self):
        bar = ctk.CTkFrame(self.root, fg_color=theme.PANEL, corner_radius=0)
        bar.pack(fill="x")

        self._status = ctk.CTkLabel(bar, text="Starting…", text_color=theme.MUTED,
                                    font=theme.font(12, kiosk=self.kiosk))
        self._status.pack(side="left", padx=12, pady=8)

        estop = ctk.CTkButton(bar, text="EMERGENCY SHUTDOWN", fg_color=theme.ZONE_COLORS["critical"],
                              hover_color="#8b1a1a", command=self._on_estop,
                              font=theme.font(13, bold=True, kiosk=self.kiosk))
        estop.pack(side="right", padx=8, pady=6)

        self._record_btn = ctk.CTkButton(bar, text="Start Recording", command=self._on_record,
                                         fg_color=theme.ACCENT,
                                         font=theme.font(12, bold=True, kiosk=self.kiosk))
        self._record_btn.pack(side="right", padx=8, pady=6)

        # Fault injection (simulator only).
        self._fault_choice = ctk.CTkOptionMenu(bar, values=["(clear)"] + list(FAULT_TARGETS),
                                               command=self._on_inject,
                                               font=theme.font(12, kiosk=self.kiosk))
        self._fault_choice.set("Inject Fault")
        self._fault_choice.pack(side="right", padx=8, pady=6)

    # -- control callbacks ----------------------------------------------------
    def _on_record(self):
        session = self.controller.logger.session
        if session.state == "recording":
            self.controller.logger.stop()
            self._record_btn.configure(text="Start Recording")
            self.set_status("Recording stopped.")
        else:
            new = self.controller.logger.start()
            if new.state == "error":
                messagebox.showwarning("Recording", new.error)
                self.set_status(new.error)
            else:
                self._record_btn.configure(text="Stop Recording")
                self.set_status(f"Recording to {new.path}")

    def _on_inject(self, choice: str):
        producer = self.controller._producer
        inject = getattr(producer, "inject", None)
        clear = getattr(producer, "clear_fault", None)
        if choice == "(clear)" and callable(clear):
            clear()
            self.set_status("Fault cleared.")
        elif callable(inject):
            try:
                inject(choice)
                self.set_status(f"Injected fault: {choice}")
            except ValueError as exc:
                self.set_status(str(exc))
        else:
            self.set_status("Fault injection is available in simulator mode only.")
        self._fault_choice.set("Inject Fault")

    def _on_estop(self):
        event = self.controller.shutdown.trigger()
        from ..models import FaultHistoryEntry
        self.controller.fault_history.append(FaultHistoryEntry(
            timestamp=event.timestamp, sensor="—", value=0.0, severity="critical",
            fault="emergency_shutdown", explanation=f"hardware: {event.hardware_outcome}",
            source="operator"))
        if self.controller.logger.session.state == "recording":
            self.controller.logger.stop()
            self._record_btn.configure(text="Start Recording")
        self._show_shutdown(event)

    def _show_shutdown(self, event):
        msg = (f"SHUTDOWN — hardware {event.hardware_outcome}. "
               f"Click to confirm and resume monitoring.")
        self._shutdown_banner.configure(text=msg)
        self._shutdown_banner.pack(fill="x", side="bottom")
        self._shutdown_banner.bind("<Button-1>", lambda e: self._confirm_resume())

    def _confirm_resume(self):
        if messagebox.askyesno("Resume", "Resume monitoring from SHUTDOWN safe state?"):
            self.controller.shutdown.resume()
            self._shutdown_banner.pack_forget()
            self.set_status("Resumed monitoring.")

    def _on_explain_ai(self):
        if self._active_alarm is None:
            self._ai.show_ai_result(None)
            return
        self.controller.agent.request_ai(self._active_alarm, self._ai_done)

    def _ai_done(self, text):
        # Marshal back onto the UI thread.
        self.root.after(0, lambda: self._ai.show_ai_result(text))

    # -- view API (called by the controller) ----------------------------------
    def set_status(self, text: str):
        self._status.configure(text=text)

    def update(self, state: dict):
        reading = state["reading"]
        zones = state["zones"]
        for key, card in self._cards.items():
            if key in reading.values:
                card.update_value(reading.values[key], zones.get(key, "normal"))
            self._charts[key].update_series(state["window"].series(key))
        self._mimic.update_health(state["stage_health"])
        self._alarms.update_alarms(state["active_alarms"])
        self._ai.update_diagnosis(state["diagnosis"])
        self._log.update_history(state["fault_history"])
        self._active_alarm = state["active_alarms"][0] if state["active_alarms"] else None

        src = state["source"]
        rec = state["recording"]
        rec_text = f" · REC {rec.rows_written} rows" if rec.state == "recording" else ""
        self.set_status(
            f"{src.kind}:{src.status} · {src.detail} · malformed {state['malformed']}{rec_text}")

    def run(self):
        self.root.mainloop()
