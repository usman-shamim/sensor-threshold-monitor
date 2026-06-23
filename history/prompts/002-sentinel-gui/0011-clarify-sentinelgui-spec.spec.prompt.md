---
id: 0011
title: Clarify SentinelGUI Spec
stage: spec
date: 2026-06-18
surface: agent
model: claude-opus-4-8[1m]
feature: 002-sentinel-gui
branch: 002-sentinel-gui
user: usman-shamim
command: /sp.clarify
labels: [clarify, spec, sentinel-gui, thresholds, fault-diagnosis, exhibition]
links:
  spec: specs/002-sentinel-gui/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-sentinel-gui/spec.md
tests:
 - none (specification clarification stage; no code)
---

## Prompt

/sp.clarify

Focus on:
- Alarm thresholds
- Sensor update frequency
- Fault classification logic
- Data retention policy
- Offline mode behavior
- AI fallback behavior
- Exhibition mode requirements

## Response snapshot

Ran the structured ambiguity scan against the seven focus areas and asked 5 clarification questions
(the maximum), all of which the user accepted at the recommended option:

1. **Alarm thresholds** → Two explicit nested bands per sensor: `warning {min,max}` inside
   `critical {min,max}`. Critical seeded from SentinelCLI `config.json`; warning ~10% inside each
   bound; both operator-configurable.
2. **Sensor update frequency** → ~1 Hz (one combined reading/second); cards, charts, and simulator
   all at this cadence.
3. **Fault classification logic** → Hybrid: current values vs thresholds + short-term
   rate-of-change/trend over a rolling window (small rolling buffer retained).
4. **Exhibition mode** → Dedicated kiosk mode: fullscreen, enlarged fonts, simplified controls,
   confirmation guards on destructive actions, auto-recover into simulator on serial drop.
5. **AI fallback behavior** → On-demand: rule-based shows instantly on every alarm; AI runs only on
   "Explain with AI", async, ~10s timeout, graceful fallback, never blocks.

Integrated into `spec.md`: added a `## Clarifications` → `### Session 2026-06-18` block (5 bullets);
updated FR-006 (two bands), FR-011 (hybrid classification), FR-014 (on-demand AI + ~10s timeout);
added FR-026 (~1 Hz cadence), FR-027 (rolling buffer), FR-028 (Exhibition/Kiosk mode); revised User
Story 7 and its scenarios; updated SC-006; added "Reading Window (rolling buffer)" entity and
refined the Threshold entity; and updated Assumptions (threshold derivation + data-retention
defaults).

Coverage outcome:
- **Resolved**: Alarm thresholds, Sensor update frequency, Fault classification logic, AI fallback
  behavior, Exhibition mode requirements.
- **Clear (already sufficient)**: Offline mode behavior — FR-023/SC-005 and the serial-disconnect
  edge case already cover offline-first behavior.
- **Deferred (default recorded, to confirm in planning)**: Data retention policy — trend window
  ~5 min, session-only fault history, manual CSV start/stop with timestamped filename.

## Outcome

- ✅ Impact: Five high-impact ambiguities resolved and encoded; spec is now plan-ready with a
  concrete threshold model, sample rate, classification approach, AI invocation model, and kiosk mode.
- 🧪 Tests: N/A — clarification stage, no code.
- 📁 Files: specs/002-sentinel-gui/spec.md (updated in place after each accepted answer).
- 🔁 Next prompts: `/sp.plan` — design architecture (UI framework, serial protocol + e-stop command,
  1 Hz reader loop, rolling buffer, hybrid fault rules, kiosk mode, SentinelCLI AI integration).
- 🧠 Reflection: Used the existing config.json to ground the thresholds question; deferred the
  lower-impact data-retention specifics with a recorded default rather than spending a 6th question.

## Evaluation notes (flywheel)

- Failure modes observed: none this session; prerequisites script ran cleanly in -PathsOnly mode.
- Graders run and results (PASS/FAIL): Clarification integrity — PASS (5 bullets, one per accepted
  answer; no duplicates; no lingering contradictions; only allowed new headings added).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): in `/sp.plan`, confirm the deferred data-retention
  defaults and the Arduino frame + emergency-stop command contract.
