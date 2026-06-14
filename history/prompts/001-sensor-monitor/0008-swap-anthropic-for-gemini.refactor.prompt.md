---
id: 0008
title: Swap Anthropic For Gemini
stage: refactor
date: 2026-06-14
surface: agent
model: claude-opus-4-8[1m]
feature: 001-sensor-monitor
branch: 001-sensor-monitor
user: usman-shamim
command: null
labels: [refactor, ai, gemini, stdlib, urllib, constitution]
links:
  spec: specs/001-sensor-monitor/spec.md
  ticket: null
  adr: history/adr/0001-optional-ai-diagnosis-dependency.md
  pr: null
files:
 - project.py
 - requirements.txt
 - README.md
 - specs/001-sensor-monitor/contracts/ai-diagnosis.md
tests:
 - pytest test_project.py (7 passed)
 - pycodestyle --max-line-length=99 project.py test_project.py (clean)
 - GEMINI_API_KEY= python project.py sample_readings.csv --config config.json --ai (graceful warn, exit 0)
---

## Prompt

can you change the anthropic key with gemini api

## Response snapshot

Swapped the optional AI diagnosis layer from Anthropic/Claude (`anthropic` SDK +
ANTHROPIC_API_KEY) to Google Gemini. Chose to call the Gemini REST API over HTTPS using the
standard-library `urllib.request` instead of a `google-generativeai` SDK — this keeps the tool
third-party-free on EVERY path and therefore RESOLVES the Constitution Principle II deviation that
ADR-0001 was created to justify (no `pip install` anywhere; `--ai` now needs only GEMINI_API_KEY +
network).

project.py changes:
- Added `import urllib.request` and `GEMINI_MODEL = "gemini-2.0-flash"` constant.
- Rewrote `diagnose_alert` no-client branch: read GEMINI_API_KEY, POST
  {"contents":[{"parts":[{"text": prompt}]}]} to
  generativelanguage.googleapis.com/v1beta/models/<model>:generateContent?key=..., parse
  candidates[0].content.parts[0].text; returns None on any anticipated failure (never raises).
- Injectable `client` seam UNCHANGED → existing tests still valid (no network/key needed).
- Updated main() warning message and module docstring.

Docs updated for accuracy: requirements.txt (no package needed; GEMINI_API_KEY only),
README.md (--ai usage + function description), contracts/ai-diagnosis.md (interface, activation
rules, constraints now say "standard library only — no deviation").

Verification: pytest 7/7 pass; pycodestyle clean; `--ai` with empty GEMINI_API_KEY warns to stderr
and completes with exit 0 (graceful degradation intact).

NOT changed (flagged for consent): ADR-0001 still says "Accepted" for the anthropic third-party
deviation, and plan.md Constitution Check still marks Principle II as a justified deviation — both
are now stale because the urllib approach removes the dependency entirely. Recommend superseding
ADR-0001 with a new ADR (or amending it) and updating the plan's Constitution Check to full PASS.

## Outcome

- ✅ Impact: AI provider switched to Gemini via stdlib urllib; tool is now stdlib-only on all paths (Principle II deviation eliminated).
- 🧪 Tests: pytest 7/7 pass; style clean; graceful AI-degradation verified.
- 📁 Files: project.py, requirements.txt, README.md, contracts/ai-diagnosis.md.
- 🔁 Next prompts: /sp.adr to supersede ADR-0001 (deviation resolved); update plan.md Constitution Check to PASS; optional live --ai smoke test with a real GEMINI_API_KEY.
- 🧠 Reflection: Choosing urllib over the Gemini SDK turned a vendor swap into a constitution win — the optional AI path no longer breaks stdlib-only.

## Evaluation notes (flywheel)

- Failure modes observed: none; provider swap kept the injectable seam so tests needed no change.
- Graders run and results (PASS/FAIL): pytest PASS (7/7); pycodestyle PASS; graceful-degradation PASS; stdlib-only-all-paths check PASS.
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): supersede ADR-0001 and flip plan.md Constitution Check Principle II to PASS to remove stale deviation records.
