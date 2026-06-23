---
id: 0015
title: Remove CS50 Project Constitution
stage: constitution
date: 2026-06-19
surface: agent
model: claude-opus-4-8
feature: none
branch: 002-sentinel-gui
user: usman-shamim
command: /sp.constitution
labels: [constitution, governance, sentinel-gui, sentinel-cli, exhibition, major-bump]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none (governance document; no code changed)
---

## Prompt

/sp.constitution

(no additional arguments in the command body)

User clarification during execution: "this is for other project exhibiton remove any relation with
CS50 rules" — the project is the Sensor Threshold Monitor exhibition system (SentinelCLI + SentinelGUI),
not a CS50P submission; all CS50P-specific rules must be removed.

## Response snapshot

Rewrote `.specify/memory/constitution.md`, bumping **2.0.0 → 3.0.0 (MAJOR)** — full replacement of the
CS50P principle set with principles appropriate to this exhibition project.

Removed (CS50P-specific): Standard-Library-Only mandate (Principle II) and CLI-via-argparse-only
mandate (Principle IV), plus all "gradable on a clean environment / submission layout" framing.

New principle set (6):
- I. Python-First & PEP 8 Style (retained, CS50P rationale stripped)
- II. Testable Core, Thin UI (logic in importable modules; UI delegates)
- III. Automated Test Coverage (pytest) — NON-NEGOTIABLE (generalized from "every project.py
  function" to all logic modules; thin UI validated manually)
- IV. Offline-First & Graceful Degradation (core works with no network; optional AI is timeout-bounded
  with clean fallback)
- V. Human-Readable Errors (retained, broadened to GUI status banners)
- VI. Secure Configuration & Reproducible Dependencies (no hardcoded secrets via env/.env;
  third-party deps now permitted but pinned)

Project Constraints, Workflow & Quality Gates, and Governance rewritten to match (two deliverables
CLI+GUI; PHR/ADR guarantees retained; offline + dependency-pinning gates added). Title changed to
"Sensor Threshold Monitor Constitution". Dates: Ratified 2026-06-13, Last Amended 2026-06-19.

Sync Impact Report prepended; plan/spec/tasks templates and CLAUDE.md verified aligned (Constitution
Check is generic; no hardcoded principle names).

## Outcome

- ✅ Impact: Constitution now governs the real project. Resolves the `/sp.analyze` CRITICAL findings
  C1 (§II stdlib-only) and C2 (§IV CLI-only) at the source — they are no longer constraints, so
  SentinelGUI's third-party GUI stack is fully compliant rather than a documented deviation.
- 🧪 Tests: none (governance doc).
- 📁 Files: .specify/memory/constitution.md (overwritten, v3.0.0).
- 🔁 Next prompts: optionally update specs/002-sentinel-gui/plan.md Constitution Check (the
  "PASS WITH DOCUMENTED DEVIATIONS" note and Complexity Tracking are now obsolete — it's a plain
  PASS); the previously-suggested `/sp.adr` for the stack deviation is no longer needed. Then
  `/sp.implement` from T001 (or re-run `/sp.analyze` to confirm C1/C2 cleared).
- 🧠 Reflection: The user corrected a wrong premise mid-task (the repo is not a CS50P submission).
  Rewrote rather than patched, since scoping exceptions onto CS50P rules would have been the wrong
  model; removing the rules entirely is simpler and correct for an exhibition product.

## Evaluation notes (flywheel)

- Failure modes observed: my first attempt (scoping §II/§IV via an "Adjunct Tooling Exception" while
  keeping CS50P framing) was rejected by the user — the correct action was to remove CS50P entirely.
  Corrected immediately.
- Graders run and results (PASS/FAIL): Placeholder check — PASS (no bracket tokens remain). Version
  coherence — PASS (report and footer both 3.0.0, MAJOR). Date format — PASS (ISO). Template
  alignment — PASS (generic Constitution Check, no principle names hardcoded).
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): re-run `/sp.analyze`; expect C1/C2 to clear and the only
  remaining items to be the MEDIUM coverage notes (SC-004, to_engineering, reading_window test).
