# Project Definition

## Product statement

AI Release Engineer is an agentic software engineering SaaS platform that can analyze a codebase, plan a requested change, implement the change in an isolated workspace, validate it with automated checks, and prepare the result for human-approved release.

## Product users

The product supports:

- individual developers using a personal workspace;
- engineering teams using an organization workspace;
- organization admins who manage members, repository connections, provider credentials, and workspace settings.

## Workspace model

Every user can have a personal workspace. A user may also belong to one or more organization workspaces.

Repositories, AI provider configuration, runs, approvals, evidence, and audit records belong to a workspace so personal and organization data remain clearly separated.

Initial organization roles:

- **Admin** — manages membership, integrations, credentials, workspace settings, and all developer functions.
- **Developer** — performs AI-assisted change workflows on repositories available to that workspace.

Additional roles are deferred until a real requirement exists.

## Integration model

### AI providers
Personal or organization workspaces may configure their own supported LLM API credentials (BYOK). Credentials are encrypted at rest, backend-only, masked after entry, and never included in logs, traces, prompts unless explicitly required, or evidence bundles.

### GitHub
GitHub is the first source-control integration. The preferred architecture uses a GitHub App with selected-repository installation and least-privilege permissions rather than broad long-lived personal access tokens.

## Portfolio objective

Demonstrate senior-level applied AI engineering through a real system combining:

- LLM and agent orchestration;
- structured tool calling;
- code generation and review;
- secure code execution;
- testing and policy gates;
- GitHub automation;
- SaaS identity and multi-tenancy;
- secure credential management;
- observability and evaluation;
- production deployment and delivery engineering.

## MVP engine user story

Given a repository and a bounded change request, the engine can:

1. inspect relevant repository content;
2. generate a structured implementation plan;
3. obtain approval for the plan;
4. implement the change in an isolated workspace;
5. run tests and quality/security checks;
6. produce a structured evidence bundle;
7. stop for human approval;
8. prepare a GitHub pull request.

## SaaS user story

Given an authenticated user:

1. the user enters a personal or organization workspace;
2. selects an authorized connected repository;
3. chooses/configures an available LLM provider;
4. submits a change request;
5. reviews the generated plan and approves or rejects it;
6. monitors implementation and validation;
7. reviews the resulting diff and evidence;
8. approves or rejects pull-request preparation;
9. reviews prior runs from the workspace history.

## Non-goals

Initial releases do not include:

- unrestricted autonomous production deployment;
- automatic merging without approval;
- training a foundation model;
- every source-control platform;
- every programming language in the first implementation;
- complex enterprise RBAC before it is needed;
- a dedicated tester role;
- customer billing/subscription logic unless product validation later requires it.

## Success criteria

- reproducible end-to-end engine demo;
- automated tests for the same scenario;
- validated schemas for model-driven actions;
- unsafe/invalid actions rejected;
- traces and usage metrics captured;
- evaluation results published;
- secure GitHub integration;
- personal and organization workspaces correctly isolated;
- Admin/Developer authorization enforced deterministically;
- provider credentials protected as secrets;
- web UI supports the primary run/review/approval workflow;
- public architecture and tradeoff documentation;
- reproducible deployment instructions.
