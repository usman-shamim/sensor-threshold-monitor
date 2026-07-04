# ADR-0001: Optional AI Diagnosis Dependency

> **Scope**: Documents the decision cluster around introducing an optional, third-party AI layer
> (`anthropic`/Claude API) into an otherwise standard-library-only CS50P project, and the
> structural pattern that keeps it isolated.

- **Status:** Accepted
- **Date:** 2026-06-14
- **Feature:** 001-sensor-monitor (Sensor Threshold Monitor)
- **Context:** The feature requires an AI diagnosis layer that explains the likely cause of an
  out-of-range sensor alert in plain language. The only practical way to achieve this quality is a
  hosted LLM (Claude via the `anthropic` SDK). However, Constitution v2.0.0 **Principle II
  (Standard Library Only)** prohibits third-party packages and the Quality Gates require the tool
  to "run end-to-end... with no `pip install` step required." The project also targets the **CS50P
  final-project** structure, whose autograder runs on a clean environment where a missing package
  would break the program. These constraints are in direct tension with the requested feature, so
  a deliberate, recorded decision is needed on whether and how to admit the dependency.

## Decision

Admit `anthropic` as an **optional, opt-in, isolated** dependency rather than a core one. The
decision cluster:

- **Dependency policy:** `anthropic` is the single permitted third-party package, used solely by
  the AI diagnosis feature. The core tool depends only on the standard library
  (`argparse`, `csv`, `json`, `datetime`, `sys`).
- **Activation model:** AI is **OFF by default**. `--ai` enables it; `--no-ai` (and the default)
  fully disable it. The default/`--no-ai` path — and therefore the CS50P-graded path — imports no
  third-party package.
- **Isolation pattern:** `import anthropic` happens **lazily inside `diagnose_alert(...)`**, never
  at module top level. `diagnose_alert(alert, client=None)` accepts an **injectable client** so
  unit tests pass a fake and need no network or API key (preserves Constitution Principle III).
- **Graceful degradation:** if `--ai` is set but the package or `ANTHROPIC_API_KEY` env var is
  missing, or an API call fails, the tool emits a human-readable warning to `stderr` and continues
  without diagnoses (exit 0).
- **Secrets:** the API key is read from `ANTHROPIC_API_KEY`; never hardcoded.
- **Governance record:** logged as a justified deviation in the plan's Constitution Check →
  Complexity Tracking; the deviation is contained entirely to the optional AI seam.

## Consequences

### Positive

- Delivers the requested AI diagnosis capability with high-quality, plain-language explanations.
- Keeps the default and CS50P-graded execution path 100% standard library — gradeability and
  reproducibility are preserved.
- Lazy import + dependency injection make every function (including `diagnose_alert`) unit-testable
  with no network access or secret, satisfying the test-first principle.
- The deviation from Principle II is minimal, explicit, and reversible (removing the feature
  removes the dependency).

### Negative

- Introduces a documented deviation from Constitution Principle II; the constitution and build are
  intentionally out of step until amended or formally accepted via this ADR.
- Two execution paths (with/without AI) increase surface area to test and reason about.
- The AI path adds external runtime concerns absent from the rest of the tool: network latency,
  API cost, key management, and Claude API/model-version drift.
- Risk that a future contributor "promotes" the dependency to the core path (e.g., a top-level
  import), silently breaking the stdlib-only guarantee — must be guarded in review.

## Alternatives Considered

- **Drop the AI feature entirely (pure stdlib).** Fully constitution- and CS50P-compliant with
  zero dependency risk. Rejected because it removes a feature the user explicitly requested.
- **Standard-library heuristic "diagnosis"** (rule-based messages keyed to sensor + breach
  direction). Keeps stdlib-only purity. Rejected because canned heuristics cannot match the
  explanation quality of an LLM, which is the point of the feature.
- **Make `anthropic` a hard/core dependency (AI on by default).** Simplest code (no flag gating,
  no lazy import). Rejected because it forces a `pip install` + API key on every run, breaking the
  no-install Quality Gate and CS50P gradeability.
- **Vendor/inline an HTTP client to call the API with only stdlib (`urllib`).** Avoids the
  `anthropic` package and technically preserves "standard library only." Rejected as more code to
  maintain, brittle against API changes, and offering no practical benefit over the official SDK
  for this project's scope. (Could be revisited if zero third-party packages becomes mandatory.)

## References

- Feature Spec: [specs/001-sensor-monitor/spec.md](../../specs/001-sensor-monitor/spec.md)
- Implementation Plan: [specs/001-sensor-monitor/plan.md](../../specs/001-sensor-monitor/plan.md)
  (Constitution Check + Complexity Tracking)
- AI Layer Contract: [specs/001-sensor-monitor/contracts/ai-diagnosis.md](../../specs/001-sensor-monitor/contracts/ai-diagnosis.md)
- Research: [specs/001-sensor-monitor/research.md](../../specs/001-sensor-monitor/research.md) (R1, R2)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) (Principle II)
- Related ADRs: none
- Evaluator Evidence: [history/prompts/001-sensor-monitor/0004-sensor-monitor-implementation-plan.plan.prompt.md](../prompts/001-sensor-monitor/0004-sensor-monitor-implementation-plan.plan.prompt.md)
