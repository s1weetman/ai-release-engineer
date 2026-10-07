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


## ADR-012 — Core product stops at pull-request preparation
**Status:** Accepted  
The core AI Release Engineer workflow ends after an approved pull request is prepared. It does not directly deploy production code.

**Reason:** The product's differentiating responsibility is the pre-merge lifecycle: understanding a requested change, planning it, creating code, validating it, gathering evidence, enforcing approvals, and preparing the PR. Existing CI/CD and hosting systems can continue handling deployment after a human merge. This keeps deployment authority outside the AI agent while allowing future optional deployment integrations.


## ADR-013 — Pydantic schemas are the domain boundary
**Status:** Accepted  
Core workflow information is represented by validated Pydantic models rather than loosely structured dictionaries or unvalidated model output.

**Reason:** The LLM is probabilistic, while the application needs deterministic contracts. Runtime schema validation provides a clear boundary for rejecting malformed, incomplete, unexpected, or unsafe data before downstream actions occur.


## ADR-014 — Planning uses a provider-neutral interface
**Status:** Accepted  
The PlanningAgent depends on an internal PlanningProvider protocol rather than directly on a vendor SDK.

**Reason:** Model vendors, model versions, pricing, and capabilities change independently from the product workflow. Keeping vendor code behind an adapter makes the planning logic mockable, testable, and replaceable.

---

## ADR-015 — First planning adapter uses structured Responses API output
**Status:** Accepted  
The first live planning adapter uses OpenAI's Responses API structured-output parsing into the existing ImplementationPlan Pydantic model.

**Reason:** The model should return application-owned structured data rather than free-form prose that downstream code tries to interpret. A missing parsed plan is treated as a provider failure.

---

## ADR-016 — Planning remains read-only
**Status:** Accepted  
P1-T4 can inspect repository context and propose an implementation plan but has no file-write, command-execution, commit, or merge authority.

**Reason:** Separating reasoning from side effects creates a clear human-review boundary and keeps the first LLM capability low-risk.


---

## ADR-017 — File changes use disposable workspaces
**Status:** Accepted  
Phase 1 file changes are applied to a temporary copy of the source repository rather than directly to the source checkout.

**Reason:** A disposable copy creates a simple failure/rollback boundary and prevents experimental generated changes from corrupting the source repository.

---

## ADR-018 — Command execution is allowlisted and shell-free
**Status:** Accepted  
Commands are supplied as argument arrays, validated against a small tool allowlist, and never executed through an unrestricted shell string.

**Reason:** Model-generated shell text is too powerful a control surface. A deterministic allowlist reduces command-injection and destructive-command risk.

---

## ADR-019 — Docker is the Phase 1 command isolation boundary
**Status:** Accepted  
Supported commands execute in a Docker container with network disabled, Linux capabilities dropped, no-new-privileges enabled, a read-only root filesystem, resource/time limits, and the disposable repository mounted as the intended writable workspace.

**Reason:** Validation commands execute repository code and therefore require stronger isolation than a changed working directory alone.


---

## ADR-020 — Validation success is derived from evidence
**Status:** Accepted  
The application does not accept a caller-supplied success flag for the validation stage. A deterministic ValidationGate passes only when validation evidence exists and every required result is PASSED.

**Reason:** The LLM or orchestration layer must not be able to self-certify generated code. Failed, skipped, or absent validation evidence is not sufficient to advance as successful.

---

## ADR-021 — Evidence bundles are versioned structured data
**Status:** Accepted  
Change-run evidence is represented as a versioned Pydantic EvidenceBundle containing request, plan, model metadata, diff/change summary, raw tool results, normalized validations, and approvals.

**Reason:** Evidence will later cross API, persistence, audit, and UI boundaries. A versioned schema makes those records machine-readable, reviewable, and evolvable.


---

## ADR-022 — Phase 1 demo is deterministic by default
**Status:** Accepted  
The P1-T7 public local demo uses a deterministic PlanningProvider and predefined bounded FileChange objects.

**Reason:** The Phase 1 milestone is intended to prove workflow integration, isolation, validation, evidence, and failure handling reproducibly. Requiring a live API key would add nondeterminism, cost, rate limits, and provider availability as unrelated demo failure modes.

The live OpenAI planning adapter remains part of the engine. Later phases connect the workflow to model-driven patch generation and real GitHub delivery.

---

## ADR-023 — Phase 1 demo includes an intentional failure path
**Status:** Accepted  
The demo includes both a passing scenario and a scenario whose implementation deliberately fails a regression test.

**Reason:** A governed AI engineering system must prove that incorrect changes are blocked, not only that a curated successful example can pass.
