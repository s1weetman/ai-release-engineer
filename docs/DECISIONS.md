# Architecture Decision Log

## ADR-001 — Human approval is a hard release boundary
**Status:** Accepted  
The system may plan, modify, test, and prepare changes, but does not merge or deploy without explicit human approval.

## ADR-002 — Python is the primary implementation language
**Status:** Accepted  
Python 3.12+ is used for orchestration/API because of its strong AI, automation, testing, and API ecosystem.

## ADR-003 — Provider-neutral model boundary
**Status:** Accepted  
LLM access is behind an internal provider interface to enable model comparison, fallback, BYOK, and testability.

## ADR-004 — Explicit workflow state machine first
**Status:** Accepted  
Start explicit; add orchestration frameworks only when they solve a demonstrated need.

## ADR-005 — Isolated execution for generated changes
**Status:** Accepted  
Generated changes and validation commands execute in an isolated workspace, with Docker as the target implementation.

## ADR-006 — Evidence bundle is a first-class output
**Status:** Accepted  
Each run should retain plan, changed files, diff summary, commands, tests, security results, model metadata, timing, and approvals.

## ADR-007 — SaaS uses a workspace abstraction
**Status:** Accepted  
Every user has a personal workspace and may also belong to organization workspaces. Repositories, provider configuration, runs, approvals, evidence, and audit records are owned by a workspace.

**Reason:** One tenant model can support both individual developers and organizations without duplicating the application architecture.

## ADR-008 — Initial organization roles are Admin and Developer
**Status:** Accepted  
Admin manages membership, integrations, credentials, and settings and can perform developer actions. Developer performs AI-assisted engineering workflows on authorized repositories.

**Reason:** Two roles cover the initial product without premature enterprise RBAC complexity. More roles can be added when requirements justify them.

## ADR-009 — Support Bring Your Own Key for LLM providers
**Status:** Accepted  
Personal and organization workspaces may configure supported LLM provider credentials.

**Reason:** BYOK lets customers control provider accounts, quotas, billing, and model access while the product remains provider-neutral.

**Security:** Raw keys are backend-only, encrypted at rest, masked after storage, rotatable/revocable, and excluded from logs and telemetry.

## ADR-010 — Prefer GitHub App installations over personal access tokens
**Status:** Accepted  
GitHub App installation is the primary repository connection model.

**Reason:** GitHub Apps provide selected-repository installation, narrowly scoped permissions, short-lived tokens, and cleaner revocation than broad long-lived PATs.

## ADR-011 — Build the execution engine before the SaaS UI
**Status:** Accepted  
Phases 1-3 validate the engine and production controls. Phase 4 adds the multi-tenant web product.

**Reason:** The web application should sit on top of a working, testable engine rather than hiding an immature backend behind a polished UI.
