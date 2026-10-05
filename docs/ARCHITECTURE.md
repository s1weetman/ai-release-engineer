# Architecture

## Architectural style

The model reasons and proposes actions; typed tools perform deterministic operations. Model output never receives unrestricted OS, tenant, credential, or GitHub authority.

The finished product separates the SaaS control plane from the AI execution engine.

```text
+------------------------+
| Web Frontend           |
| login / dashboard / UI |
+-----------+------------+
            |
            v
+------------------------+
| API + Identity         |
| users / workspaces     |
| roles / authorization  |
+-----------+------------+
            |
            v
+------------------------+       +---------------------+
| Orchestrator + Policy  |<----->| Audit / Telemetry   |
+------+-----------+-----+       +---------------------+
       |           |
       |           +----------------------+
       v                                  v
+---------------+                 +--------------------+
| LLM Provider  |                 | Secrets Service    |
| abstraction   |                 | BYOK / integrations|
+---------------+                 +--------------------+
       |
       v
+------------------------------------------------------+
| Typed Tool Layer                                     |
| repo read | patch | tests | security | git / GitHub  |
+--------------------------+---------------------------+
                           |
                           v
                  +-------------------+
                  | Isolated Runner   |
                  | Docker workspace  |
                  +-------------------+
```

## SaaS tenancy model

The application uses a workspace abstraction.

A workspace is either:

- **personal** — owned by one user; or
- **organization** — shared by users through membership records.

Workspace-owned resources include:

- repository connections;
- LLM provider configuration;
- AI change runs;
- approval records;
- evidence bundles;
- audit records;
- workspace settings.

Every data access must be scoped to the active workspace.

### Initial roles

**Admin**
- manage organization members;
- manage provider credentials;
- manage GitHub connections/repositories;
- manage organization settings;
- perform all developer workflow actions.

**Developer**
- view repositories available to the workspace;
- create change runs;
- review plans and evidence;
- perform authorized approval actions;
- request pull-request preparation.

A separate tester role is intentionally omitted in the initial design. Additional reviewer/approver roles may be added later if required.

## Credential model

### LLM BYOK

Provider credentials belong to a workspace.

- Personal workspace credentials are controlled by the user.
- Organization credentials are controlled by Admins.
- Secret values are encrypted at rest.
- APIs return only masked metadata after creation.
- Backend services retrieve secrets only when making authorized provider calls.
- Secrets are excluded from prompts, logs, traces, evidence bundles, and source control.

### GitHub

GitHub App installation is the preferred integration.

Reasons:

- selected-repository installation;
- narrowly scoped permissions;
- short-lived installation tokens;
- revocation through GitHub;
- no need to store broad personal access tokens as the normal path.

The repository integration boundary should allow GitLab or Bitbucket adapters later without changing the agent workflow.

## Workflow states

```text
RECEIVED -> ANALYZING -> PLAN_READY -> PLAN_APPROVED
-> IMPLEMENTING -> VALIDATING -> REVIEW_READY
-> RELEASE_APPROVED -> PR_PREPARED

Any state may transition to FAILED or CANCELLED.
```

Human approval is required for PLAN_READY -> PLAN_APPROVED and REVIEW_READY -> RELEASE_APPROVED.

Authorization to approve is checked by deterministic application policy in the active workspace.

## Major modules

- Web frontend
- Authentication / identity
- Workspace and membership service
- Authorization / policy
- API / CLI
- Orchestrator
- Model provider abstraction
- Secrets service
- Repository service
- GitHub integration
- Isolated execution runner
- Validation pipeline
- Evidence storage
- Audit / observability

## Initial engine repository structure

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

The web application structure is intentionally deferred until Phase 4 so the engine can be validated independently first.

## Design principle: deterministic outside the model

Use the LLM for ambiguous reasoning such as planning and code understanding.

Use deterministic code for:

- authentication;
- workspace isolation;
- authorization;
- secrets access;
- workflow state transitions;
- validation;
- path handling;
- subprocess execution;
- schemas;
- repository permissions;
- release policy.

## Deployment model

Initial target: cloud-hosted SaaS control plane plus isolated execution workers.

A later enterprise option may add a self-hosted/private-network runner so source code and build execution can stay inside a customer's environment while the SaaS control plane coordinates work. This is an extension point, not an initial requirement.

## Orchestration framework decision

Start with an explicit state machine so behavior remains understandable and testable. Evaluate LangGraph later if checkpointing, branching, or resumability provides concrete value.
