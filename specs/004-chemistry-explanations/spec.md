# Feature Specification: Chemistry-Aware Fault Explanations

**Feature Branch**: `004-chemistry-explanations`
**Created**: 2026-07-04
**Status**: Implemented
**Scope**: Rewrite the six rule-based fault explanations in `sentinelgui/fault_engine.py` to include chemical process context suitable for a chemical technology exhibition audience.

## Overview

The existing fault explanations are generic engineering descriptions. For a chemical
technology exhibition, each explanation is rewritten to reference the underlying chemical
and physical principles: Arrhenius kinetics, heat transfer coefficients, vapour pressure,
precipitation, and centrifugal pump mechanics.

## Changes (all in `sentinelgui/fault_engine.py`)

| Fault | Before | After |
|-------|--------|-------|
| **pump_failure** | "Flow has collapsed toward zero while pressure has also dropped, which points to a pump that has stopped delivering." | "Pump failure — coolant circulation has stopped. Flow rate collapsed to near zero and discharge pressure dropped, consistent with a centrifugal pump that has lost prime, tripped, or suffered impeller damage. Without coolant flow the reactor cannot reject heat." |
| **blockage** | "Flow is restricted while pressure builds upstream — the classic signature of a restriction or blockage downstream of the pump." | "Blockage detected — a physical obstruction in the cooling loop (e.g. precipitated solids, debris, or a partially closed valve) is restricting flow. Pressure builds upstream of the restriction while flow drops downstream — the classic ΔP signature of a blocked line." |
| **cavitation** | "Pressure is low and oscillating, consistent with cavitation (vapour bubbles forming and collapsing in the pump)." | "Cavitation — vapour bubbles are forming in the pump. When the local pressure at the impeller drops below the fluid's vapour pressure, bubbles nucleate and then collapse violently against the impeller surface. This causes the characteristic pressure oscillation, noise, vibration, and progressive impeller erosion." |
| **thermal_runaway** | "Temperature is above its critical limit — a thermal runaway in the reactor; consider emergency shutdown." | "Thermal runaway — the reactor temperature has exceeded its critical limit. An exothermic reaction is accelerating: reaction rate increases exponentially with temperature (Arrhenius kinetics), generating heat faster than the cooling system can remove it. Immediate intervention required — consider emergency shutdown." |
| **cooling_failure** | "Temperature is high even though coolant flow is adequate, which indicates the cooling system is not removing heat effectively." | "Cooling failure — the heat exchanger is not removing heat effectively despite adequate coolant flow. Possible causes: fouled heat exchanger surfaces reducing the overall heat transfer coefficient (U), low coolant level, or secondary cooling circuit failure. Reactor temperature is rising." |
| **fouling** | "Temperature is creeping up while flow is mildly reduced — deposits/fouling are lowering heat transfer and restricting the loop." | "Fouling — scale or deposits are accumulating on heat exchanger surfaces, reducing the overall heat transfer coefficient (U). The insulating layer forces temperature upward while flow is mildly restricted. Common in hard water or when dissolved solids precipitate out of solution at elevated temperatures." |

## Chemistry concepts referenced

| Concept | Fault(s) |
|---------|----------|
| Arrhenius kinetics (reaction rate ∝ eᵀ) | thermal_runaway |
| Heat transfer coefficient U (Q = UAΔT) | cooling_failure, fouling |
| Vapour pressure / cavitation nucleation | cavitation |
| Centrifugal pump mechanics (prime, impeller) | pump_failure |
| ΔP signature across a restriction | blockage |
| Precipitation / scale formation | blockage, fouling |

## Success criteria

- **SC-001**: All six faults display their chemistry-aware explanation when triggered via
  simulator or serial data.
- **SC-002**: Existing test suite (58 tests) passes without modification — only literal
  strings in explanations changed.

## Out of scope

- New fault types
- Changes to the classification logic or tuning thresholds
- AI-enriched explanations (these remain in the AIPanel)
