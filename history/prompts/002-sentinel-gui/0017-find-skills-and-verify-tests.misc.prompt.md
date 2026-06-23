---
id: 0017
title: Find Skills and Verify Tests
stage: misc
date: 2026-06-23
surface: agent
model: claude-opus-4-8
feature: 002-sentinel-gui
branch: 002-sentinel-gui
user: usman-shamim
command: null
labels: [find-skills, subagents, pytest, verification, skills-sh, fault-engine]
links:
  spec: specs/002-sentinel-gui/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - history/prompts/002-sentinel-gui/0017-find-skills-and-verify-tests.misc.prompt.md
tests:
 - "python -m pytest sentinelgui/tests/ test_project.py -q -> 58 passed (51 GUI + 7 CLI)"
---

## Prompt

https://github.com/vercel-labs/skills/tree/main/skills/find-skills use this skill to find the best skills that I can use and create subagents as well to speed up the process also continue

(Follow-up after a tooling outage: "what was the last thing you were doing")

## Response

Picked up the three pending tasks once the transient classifier outage cleared.

1. **Verified tests (the "continue" task):** Ran `python -m pytest sentinelgui/tests/ test_project.py -q` -> **58 passed in 0.91s** (51 SentinelGUI + 7 SentinelCLI). Confirms the value-signature-primary `fault_engine.py` refactor fixed the steady-state classification bug without regressions; `project.py` / `test_project.py` remain isolated.

2. **Applied the find-skills skill:** Fetched the SKILL.md from vercel-labs/skills. Methodology = check the https://skills.sh/ leaderboard first, then `npx skills find <query>`, verify quality (install count >=1K, reputable source, GitHub stars), present options, offer `npx skills add <owner/repo@skill> -g -y`.

3. **Spawned 2 parallel subagents** to speed discovery (testing stack / GUI+serial+SDD).

### Recommended skills (vetted)

Tier 1 (clears quality bar):
- `mattpocock/skills@tdd` (291.6K) — red-green-refactor for headless logic modules (Constitution Principle III).
- `github/awesome-copilot@pytest-coverage` (11.1K) — pytest + coverage gating.
- `anthropics/knowledge-work-plugins@documentation` (5.8K) — first-party docs for SDD artifacts.
- `addyosmani/agent-skills@documentation-and-adrs` (6.7K) — ADR authoring for the /sp.adr workflow.

Tier 2 (vet first, sub-1K / non-marquee):
- `jeffallan/claude-skills@embedded-systems` (4.3K) — closest to pyserial/SCADA rig.
- `davila7/claude-code-templates@matplotlib` (858) — trend charts.

Gap: no reputable Tkinter/customtkinter or pyserial/Modbus/SCADA skill exists in the registry — the hand-built `dashboard/` and `acquisition.py` remain the right approach.

## Outcome

- Tests green (58 passed); fault-engine fix confirmed.
- Skill recommendations delivered with install commands; nothing installed (awaiting user consent).
- No production code changed this turn.

## Follow-ups

- Optional: `npx skills add` any Tier 1 skill globally if the user wants it.
- Optional: `pip install -r sentinelgui/requirements.txt` then `python -m sentinelgui --simulate` UI smoke test.
- Optional: `/sp.git.commit_pr` to land the SentinelGUI feature branch.
