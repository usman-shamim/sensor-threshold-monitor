---
id: 0009
title: Protect API Key For GitHub
stage: misc
date: 2026-06-14
surface: agent
model: claude-opus-4-8[1m]
feature: 001-sensor-monitor
branch: 001-sensor-monitor
user: usman-shamim
command: null
labels: [security, secrets, api-key, gitignore, github]
links:
  spec: specs/001-sensor-monitor/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - .gitignore
 - .env.example
tests:
 - git check-ignore .env (ignored) / .env.example (not ignored)
 - grep scan for AIza... key literals (none found)
---

## Prompt

I will be putting this project in git hub how can I protect my api key

## Response snapshot

Audited the repo for secret-safety before the user pushes to GitHub:
- Confirmed no API key literal anywhere (grep for `AIza[0-9A-Za-z_-]{10,}` → none); the key is only
  ever read via os.environ.get("GEMINI_API_KEY") in project.py — never hardcoded.
- Confirmed .gitignore already ignores `.env` and `.env.*`.

Hardening added:
- Created `.env.example` (committable template; documents GEMINI_API_KEY without a value).
- Updated .gitignore with `!.env.example` so real `.env` stays ignored but the template is tracked.
- Verified via `git check-ignore`: `.env` → ignored, `.env.example` → not ignored.

Guidance given: how to set the env var on Windows (Git Bash export / PowerShell $env: / persistent
setx); flagged honestly that the tool reads the OS env and does NOT auto-load `.env` (python-dotenv
would violate the stdlib-only constitution) and offered an optional ~6-line stdlib .env loader;
pre-push checks (git status / git ls-files | grep env); enabling GitHub secret scanning + push
protection; and rotate-then-restrict if a key ever leaks (delete in Google AI Studio, restrict to
the Generative Language API).

## Outcome

- ✅ Impact: Repo confirmed secret-safe for GitHub; .env.example + gitignore negation added.
- 🧪 Tests: git check-ignore behavior verified; key-literal grep clean.
- 📁 Files: .gitignore (negation), .env.example (new).
- 🔁 Next prompts: optional stdlib .env loader in project.py; enable GitHub push protection; commit + push.
- 🧠 Reflection: Key handling was already correct (env var + gitignore); main value was an explicit audit + a committable template + the honest note that .env isn't auto-loaded.

## Evaluation notes (flywheel)

- Failure modes observed: `.env.*` would have ignored `.env.example` too — fixed with `!.env.example` negation.
- Graders run and results (PASS/FAIL): secret scan PASS (no literals); ignore-rule check PASS (.env ignored, template tracked).
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): add stdlib .env auto-loader so the .env.example→.env workflow actually functions without a third-party package.
