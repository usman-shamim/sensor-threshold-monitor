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
            explanation=(
                "Flow has collapsed toward zero while pressure has also dropped, "
                "which points to a pump that has stopped delivering."
            ),
            confidence=_confidence(f_slope <= 0 and p_slope <= 0),
            related_sensors=["flow_rate", "pressure"],
        )

    # 2. Blockage — flow low AND pressure high (rising flow-down/pressure-up corroborates).
    if flow is not None and press is not None and flow < FLOW_LOW and press > PRESS_HIGH:
        return FaultDiagnosis(
            fault="blockage",
            explanation=(
                "Flow is restricted while pressure builds upstream — the classic signature "
                "of a restriction or blockage downstream of the pump."
            ),
            confidence=_confidence(f_slope < 0 and p_slope > 0),
            related_sensors=["flow_rate", "pressure"],
        )

    # 3. Cavitation — low, oscillating pressure (variance persists with the oscillation).
    if press is not None and press < PRESS_LOW and p_var > PRESS_OSCILLATION_VAR:
        return FaultDiagnosis(
            fault="cavitation",
            explanation=(
                "Pressure is low and oscillating, consistent with cavitation (vapour "
                "bubbles forming and collapsing in the pump)."
            ),
            confidence="medium",
            related_sensors=["pressure"],
        )

    # 4. Thermal runaway — temperature at/above its critical limit (steep rise corroborates).
    if temp is not None and temp >= TEMP_CRITICAL:
        return FaultDiagnosis(
            fault="thermal_runaway",
            explanation=(
                "Temperature is above its critical limit — a thermal runaway in the "
                "reactor; consider emergency shutdown."
            ),
            confidence=_confidence(t_slope >= TEMP_STEEP_SLOPE),
            related_sensors=["temperature"],
        )

    # 5. Cooling failure — temperature elevated while coolant flow is still adequate.
    if temp is not None and temp > TEMP_WARN and (flow is None or flow >= FLOW_ADEQUATE):
        return FaultDiagnosis(
            fault="cooling_failure",
            explanation=(
                "Temperature is high even though coolant flow is adequate, which indicates "
                "the cooling system is not removing heat effectively."
            ),
            confidence=_confidence(t_slope > 0),
            related_sensors=["temperature", "flow_rate"],
        )

    # 6. Fouling — temperature elevated AND a mild flow reduction (deposits restricting flow).
    if temp is not None and flow is not None and temp > TEMP_WARN and flow < FLOW_ADEQUATE:
        return FaultDiagnosis(
            fault="fouling",
            explanation=(
                "Temperature is creeping up while flow is mildly reduced — deposits/fouling "
                "are lowering heat transfer and restricting the loop."
            ),
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
