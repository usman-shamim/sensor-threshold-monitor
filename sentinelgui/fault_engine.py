"""Module 3 — Fault Detection Engine.

Hybrid rule-based classifier: combines current values against thresholds with short-term
rate-of-change/variance over the rolling window so dynamic faults can be distinguished
(FR-011). Resolution order (first match wins): pump_failure, blockage, cavitation,
thermal_runaway, cooling_failure, fouling, undetermined (data-model.md). Pure standard
library — fully unit-testable.
"""

from __future__ import annotations

from typing import Optional

from .models import FaultDiagnosis
from .reading_window import ReadingWindow

# Tuning reference points (engineering units). Chosen to match the simulator signatures and
# the default gui_config bands; adjustable without code changes elsewhere.
SLOPE_N = 10
FLOW_LOW = 20.0
FLOW_ADEQUATE = 26.0
FLOW_NEAR_ZERO = 6.0
PRESS_HIGH = 4.2
PRESS_LOW = 2.0
PRESS_OSCILLATION_VAR = 0.15
TEMP_WARN = 88.0
TEMP_CRITICAL = 100.0
TEMP_STEEP_SLOPE = 2.0

_EXPLANATIONS: dict[str, str] = {}  # overridden per scenario
_TUNE: dict[str, float] = {}  # overridden per scenario


def set_explanations(explanations: dict):
    _EXPLANATIONS.clear()
    _EXPLANATIONS.update(explanations)


def reset_tuning():
    _TUNE.clear()
    global FLOW_LOW; FLOW_LOW = 20.0
    global FLOW_ADEQUATE; FLOW_ADEQUATE = 26.0
    global FLOW_NEAR_ZERO; FLOW_NEAR_ZERO = 6.0
    global PRESS_HIGH; PRESS_HIGH = 4.2
    global PRESS_LOW; PRESS_LOW = 2.0
    global PRESS_OSCILLATION_VAR; PRESS_OSCILLATION_VAR = 0.15
    global TEMP_WARN; TEMP_WARN = 88.0
    global TEMP_CRITICAL; TEMP_CRITICAL = 100.0
    global TEMP_STEEP_SLOPE; TEMP_STEEP_SLOPE = 2.0


def set_tuning(params: dict):
    _TUNE.clear()
    _TUNE.update(params)
    if "flow_low" in _TUNE:
        global FLOW_LOW; FLOW_LOW = _TUNE["flow_low"]
    if "flow_adequate" in _TUNE:
        global FLOW_ADEQUATE; FLOW_ADEQUATE = _TUNE["flow_adequate"]
    if "flow_near_zero" in _TUNE:
        global FLOW_NEAR_ZERO; FLOW_NEAR_ZERO = _TUNE["flow_near_zero"]
    if "press_high" in _TUNE:
        global PRESS_HIGH; PRESS_HIGH = _TUNE["press_high"]
    if "press_low" in _TUNE:
        global PRESS_LOW; PRESS_LOW = _TUNE["press_low"]
    if "press_oscillation_var" in _TUNE:
        global PRESS_OSCILLATION_VAR; PRESS_OSCILLATION_VAR = _TUNE["press_oscillation_var"]
    if "temp_warn" in _TUNE:
        global TEMP_WARN; TEMP_WARN = _TUNE["temp_warn"]
    if "temp_critical" in _TUNE:
        global TEMP_CRITICAL; TEMP_CRITICAL = _TUNE["temp_critical"]
    if "temp_steep_slope" in _TUNE:
        global TEMP_STEEP_SLOPE; TEMP_STEEP_SLOPE = _TUNE["temp_steep_slope"]


def _explain(fault: str, fallback: str) -> str:
    return _EXPLANATIONS.get(fault, fallback)


def slope(window: ReadingWindow, sensor: str, n: int = SLOPE_N) -> float:
    """Per-sample rate of change for *sensor* over the last *n* samples (pure helper)."""
    return window.slope(sensor, n)


def _confidence(strong: bool) -> str:
    """Trend corroborates the value signature -> high; value-only -> medium."""
    return "high" if strong else "medium"


def classify(reading, window: ReadingWindow, active: Optional[list] = None) -> FaultDiagnosis:
    """Return the most likely ``FaultDiagnosis`` for the current reading + trend.

    The current-value signature is primary so a *sustained* fault stays diagnosed even
    after its transient has settled (slopes flatten at steady state); the short-term trend
    only corroborates the value pattern and raises confidence.
    """
    v = reading.values
    temp = v.get("temperature")
    flow = v.get("flow_rate")
    press = v.get("pressure")
    t_slope = slope(window, "temperature")
    f_slope = slope(window, "flow_rate")
    p_slope = slope(window, "pressure")
    p_var = window.variance("pressure", SLOPE_N)

    # 1. Pump failure — flow collapsed toward zero AND pressure low.
    if flow is not None and press is not None and flow <= FLOW_NEAR_ZERO and press <= PRESS_LOW:
        return FaultDiagnosis(
            fault="pump_failure",
            explanation=_explain("pump_failure",
                "Pump failure — coolant circulation has stopped. Flow rate collapsed "
                "to near zero and discharge pressure dropped, consistent with a "
                "centrifugal pump that has lost prime, tripped, or suffered impeller "
                "damage. Without coolant flow the reactor cannot reject heat."),

            confidence=_confidence(f_slope <= 0 and p_slope <= 0),
            related_sensors=["flow_rate", "pressure"],
        )

    # 2. Blockage — flow low AND pressure high (rising flow-down/pressure-up corroborates).
    if flow is not None and press is not None and flow < FLOW_LOW and press > PRESS_HIGH:
        return FaultDiagnosis(
            fault="blockage",
            explanation=_explain("blockage",
                "Blockage detected — a physical obstruction in the cooling loop "
                "(e.g. precipitated solids, debris, or a partially closed valve) is "
                "restricting flow. Pressure builds upstream of the restriction while "
                "flow drops downstream — the classic ΔP signature of a blocked line."),
            confidence=_confidence(f_slope < 0 and p_slope > 0),
            related_sensors=["flow_rate", "pressure"],
        )

    # 3. Cavitation — low, oscillating pressure (variance persists with the oscillation).
    if press is not None and press < PRESS_LOW and p_var > PRESS_OSCILLATION_VAR:
        return FaultDiagnosis(
            fault="cavitation",
            explanation=_explain("cavitation",
                "Cavitation — vapour bubbles are forming in the pump. When the local "
                "pressure at the impeller drops below the fluid's vapour pressure, "
                "bubbles nucleate and then collapse violently against the impeller "
                "surface. This causes the characteristic pressure oscillation, noise, "
                "vibration, and progressive impeller erosion."),
            confidence="medium",
            related_sensors=["pressure"],
        )

    # 4. Thermal runaway — temperature at/above its critical limit (steep rise corroborates).
    if temp is not None and temp >= TEMP_CRITICAL:
        return FaultDiagnosis(
            fault="thermal_runaway",
            explanation=_explain("thermal_runaway",
                "Thermal runaway — the reactor temperature has exceeded its critical "
                "limit. An exothermic reaction is accelerating: reaction rate increases "
                "exponentially with temperature (Arrhenius kinetics), generating heat "
                "faster than the cooling system can remove it. Immediate intervention "
                "required — consider emergency shutdown."),
            confidence=_confidence(t_slope >= TEMP_STEEP_SLOPE),
            related_sensors=["temperature"],
        )

    # 5. Cooling failure — temperature elevated while coolant flow is still adequate.
    if temp is not None and temp > TEMP_WARN and (flow is None or flow >= FLOW_ADEQUATE):
        return FaultDiagnosis(
            fault="cooling_failure",
            explanation=_explain("cooling_failure",
                "Cooling failure — the heat exchanger is not removing heat effectively "
                "despite adequate coolant flow. Possible causes: fouled heat exchanger "
                "surfaces reducing the overall heat transfer coefficient (U), low "
                "coolant level, or secondary cooling circuit failure. Reactor "
                "temperature is rising."),
            confidence=_confidence(t_slope > 0),
            related_sensors=["temperature", "flow_rate"],
        )

    # 6. Fouling — temperature elevated AND a mild flow reduction (deposits restricting flow).
    if temp is not None and flow is not None and temp > TEMP_WARN and flow < FLOW_ADEQUATE:
        return FaultDiagnosis(
            fault="fouling",
            explanation=_explain("fouling",
                "Fouling — scale or deposits are accumulating on heat exchanger "
                "surfaces, reducing the overall heat transfer coefficient (U). The "
                "insulating layer forces temperature upward while flow is mildly "
                "restricted. Common in hard water or when dissolved solids precipitate "
                "out of solution at elevated temperatures."),
            confidence=_confidence(t_slope > 0 and f_slope < 0),
            related_sensors=["temperature", "flow_rate"],
        )

    # 7. No known signature.
    related = [s for s in ("temperature", "flow_rate", "pressure") if s in v]
    return FaultDiagnosis(
        fault="undetermined",
        explanation=(
            "Readings are out of their normal range but do not match a known fault "
            "signature; monitor closely."
        ),
        confidence="low",
        related_sensors=related,
    )
