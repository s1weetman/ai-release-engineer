# Architecture

## Architectural style
The model reasons and proposes actions; typed tools perform deterministic operations. Model output never receives unrestricted OS or GitHub authority.

```text
CLI / API / UI
      |
      v
Orchestrator + Policy
   |             |
   v             v
LLM Provider   Audit/Telemetry
   |
   v
Typed Tool Layer
(repo | patch | tests | security | git/github)
   |
   v
Isolated Runner
```

## Workflow states
```text
RECEIVED -> ANALYZING -> PLAN_READY -> PLAN_APPROVED
-> IMPLEMENTING -> VALIDATING -> REVIEW_READY
-> RELEASE_APPROVED -> PR_PREPARED

Any state may transition to FAILED or CANCELLED.
```

Human approval is required for PLAN_READY -> PLAN_APPROVED and REVIEW_READY -> RELEASE_APPROVED.

## Major modules
- API/CLI
- Orchestrator
- Model provider abstraction
- Repository service
- Isolated execution runner
- Validation pipeline
- Approval/policy layer
- Audit/observability

## Initial repository structure
```text
src/ai_release_engineer/
  api/
  orchestration/
  models/
  providers/
  repository/
  tools/
  runner/
  validation/
  policy/
  telemetry/
tests/
  unit/
  integration/
  fixtures/
docs/
.github/workflows/
```

## Design principle
Use the LLM for ambiguous reasoning such as planning and code understanding. Use deterministic code for permissions, state transitions, validation, paths, subprocess execution, schemas, and release policy.

## Orchestration framework decision
Start with an explicit state machine so behavior remains understandable and testable. Evaluate LangGraph later if checkpointing, branching, or resumability provides concrete value.
