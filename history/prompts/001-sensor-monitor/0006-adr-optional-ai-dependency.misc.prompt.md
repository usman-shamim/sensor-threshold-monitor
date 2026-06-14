---
id: 0006
title: ADR Optional AI Dependency
stage: misc
date: 2026-06-14
surface: agent
model: claude-opus-4-8[1m]
feature: 001-sensor-monitor
branch: 001-sensor-monitor
user: usman-shamim
command: /sp.adr
labels: [adr, architecture, ai, constitution-deviation, cs50p]
links:
  spec: specs/001-sensor-monitor/spec.md
  ticket: null
  adr: history/adr/0001-optional-ai-diagnosis-dependency.md
  pr: null
files:
 - history/adr/0001-optional-ai-diagnosis-dependency.md
 - specs/001-sensor-monitor/plan.md
tests:
 - none
---

## Prompt

/sp.adr optional-ai-diagnosis-dependency

## Response snapshot

Created `history/adr/0001-optional-ai-diagnosis-dependency.md` (no prior ADRs; history/adr/
created). PowerShell prerequisites/create-adr scripts unavailable — authored agent-natively from
.specify/templates/adr-template.md.

Decision cluster (single ADR — passes all significance tests: impacts code structure, has notable
tradeoffs, will be revisited): admit `anthropic` as an OPTIONAL, opt-in, isolated dependency.
Components: dependency policy (anthropic only, for AI feature; core = stdlib), activation model
(AI off by default, --ai enables, --no-ai/default disables), isolation pattern (lazy import inside
diagnose_alert + injectable client seam), graceful degradation (warn+continue, exit 0), secrets via
ANTHROPIC_API_KEY env var, governance record in plan Complexity Tracking.
Status: Accepted. Consequences cover positive (feature delivered, stdlib-only graded path
preserved, fully unit-testable, reversible) and negative (documented Principle II deviation, two
execution paths, external runtime concerns, promotion risk). Alternatives: drop AI; stdlib
heuristic; hard/core dependency; stdlib urllib vendored client — each rejected with rationale.
Linked spec/plan/research(R1,R2)/ai-diagnosis contract/constitution. Added a back-reference to
ADR-0001 in plan.md Complexity Tracking.

## Outcome

- ✅ Impact: Optional-AI-dependency decision permanently recorded; constitution deviation now justified & traceable via ADR-0001.
- 🧪 Tests: none (decision record)
- 📁 Files: history/adr/0001-optional-ai-diagnosis-dependency.md; plan.md (ADR back-link)
- 🔁 Next prompts: /sp.implement (or start T001) to build the MVP (Phases 1–4).
- 🧠 Reflection: Single clustered ADR avoided over-granular records; explicit alternatives + pros/cons satisfy the significance grader.

## Evaluation notes (flywheel)

- Failure modes observed: none (avoided over-granular ADR and missing-alternatives failure modes); create-adr.ps1 unavailable → agent-native authoring.
- Graders run and results (PASS/FAIL): significance checklist PASS (clustered decision, ≥1 alternative with rationale, pros+cons, concise); placeholder scan PASS.
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): on /sp.implement, guard against promoting anthropic to a top-level import (review checklist item).
