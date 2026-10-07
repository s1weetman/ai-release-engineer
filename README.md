# AI Release Engineer

A production-oriented agentic AI system and planned SaaS application that plans, implements, tests, validates, and prepares software changes for human-approved release.

## Why this project exists

AI Release Engineer demonstrates how modern AI-assisted software engineering can be made safe, observable, testable, and useful in real delivery workflows. The system accepts a software change request, inspects a repository, produces an implementation plan, generates or modifies code, runs validation checks, and prepares a pull request while keeping a human approval gate before release.

This is not a toy chatbot. The engineering focus is on agent orchestration, tool use, code quality, evaluation, security, CI/CD, observability, production reliability, and a usable SaaS control plane.

## What the system does

At a high level, AI Release Engineer acts like a governed AI software engineer:

1. A user signs in to a personal or organization workspace.
2. The user selects a connected GitHub repository.
3. The user submits a bounded software change request.
4. The system inspects the repository and gathers relevant context.
5. An LLM produces a structured implementation plan.
6. A human reviews and approves that plan.
7. The system performs the change inside an isolated workspace.
8. Automated tests, static analysis, type checks, and security checks validate the result.
9. The system creates an evidence bundle showing exactly what changed and what passed or failed.
10. A human approves the release candidate.
11. The system prepares a GitHub pull request.
12. It never automatically merges or deploys production code.

## SaaS product model

The finished product will provide a web front end and support two ways of working:

- **Personal workspace** — an individual user can connect repositories, configure an LLM provider, and run AI-assisted changes without belonging to an organization.
- **Organization workspace** — an organization can contain multiple users and shared repository/provider configuration.

For the initial SaaS role model, organization membership stays intentionally simple:

- **Admin** — manages organization settings, members, integrations, repository connections, and credentials; can also perform development workflows.
- **Developer** — creates and reviews AI-assisted change runs against repositories they are allowed to use.

A separate tester role is not planned initially because automated validation is part of the product workflow. Additional roles such as Reviewer or Approver can be introduced later if real requirements justify them.

A user may work in a personal workspace and may also belong to one or more organization workspaces.

## Bring Your Own Key (BYOK)

The SaaS product is designed to let a personal workspace or organization configure its own supported LLM provider credentials.

Examples include OpenAI- or Anthropic-compatible API credentials.

Security rules for provider credentials:

- credentials are entered through the authenticated web application;
- raw secret values are never returned to the browser after storage;
- secrets are encrypted at rest and accessed only by backend services that need them;
- secrets never appear in logs, traces, evidence bundles, or source control;
- organization credentials are managed by organization admins;
- credentials can be replaced or revoked without changing application code.

The provider layer remains vendor-neutral so users are not locked to one LLM vendor.

## GitHub connection model

GitHub is the first supported source-control platform.

The preferred connection model is a **GitHub App installation**, not a broad personal access token. A GitHub App can request narrowly scoped repository permissions, issue short-lived installation tokens, and be installed only on selected repositories.

Users will be able to:

- connect GitHub to a personal or organization workspace;
- choose which repositories the product may access;
- view connected repositories;
- submit change requests against an allowed repository;
- allow the system to create a branch and pull request only after the required approvals.

Other source-control systems can be added later behind the same repository integration boundary.

## Delivery boundary

AI Release Engineer goes beyond a traditional CI/CD pipeline. A conventional pipeline generally begins after source code already exists: it builds, tests, packages, and deploys that code. AI Release Engineer starts earlier in the software lifecycle by helping understand the requested change, planning it, creating the code change, and validating the result.

The initial product boundary intentionally stops at an approved **pull request**. It does not directly deploy production code. Once a human reviews and merges the PR, the target repository's existing CI/CD or hosting platform can take over and deploy normally.

This keeps the product focused on AI-assisted software change creation, validation, governance, and release preparation while allowing customers to keep their existing deployment systems.

A future commercial SaaS edition may extend the product with optional deployment integrations, but autonomous production deployment is not part of the current core scope.

## Target workflow

```text
Sign In
   |
   v
Personal / Organization Workspace
   |
   v
Connected GitHub Repository
   |
   v
Change Request
   |
   v
Repository Analysis
   |
   v
AI Implementation Plan
   |
   v
Human Plan Approval
   |
   v
Isolated Code Change
   |
   +--> Unit / Integration Tests
   +--> Lint / Type Checks
   +--> Security Scans
   |
   v
AI Review + Evidence Bundle
   |
   v
Human Release Approval
   |
   v
Pull Request
```

## What each major piece does

| Component | What it does | Why it matters |
| --- | --- | --- |
| **Web Application** | Provides login, workspace switching, repository selection, change requests, approvals, results, and settings. | Makes the AI engineering engine usable as a real SaaS product. |
| **Identity / Workspace Layer** | Represents users, personal workspaces, organizations, memberships, and roles. | Provides tenant isolation and simple multi-user collaboration. |
| **API / CLI** | Receives change requests, repository targets, and approvals. | Gives the web app, developers, and automation a controlled interface to the engine. |
| **Orchestrator** | Tracks workflow state and decides what step happens next. | Prevents the LLM from controlling the entire system on its own. |
| **LLM Provider Layer** | Sends reasoning tasks to a configured AI model and returns validated structured responses. | Supports BYOK and avoids locking the architecture to one vendor. |
| **Repository Service** | Safely lists files, reads code, searches text, and builds repository context. | Gives the agent needed information while restricting access. |
| **Tool Layer** | Exposes explicit operations the agent may request. | Turns model intent into controlled, testable actions. |
| **Execution Sandbox** | Runs generated changes and commands in an isolated environment. | Protects the platform from unsafe or broken generated code. |
| **Validation Pipeline** | Runs tests, linting, type checking, security scanning, and other quality gates. | Provides objective evidence instead of trusting model confidence. |
| **Policy / Approval Layer** | Enforces rules and human approval checkpoints. | Makes safety and release authority deterministic rather than model-controlled. |
| **Evidence Bundle** | Records plan, changed files, diff, commands, validation results, model metadata, and approvals. | Makes every AI-assisted change explainable and auditable. |
| **Telemetry / Observability** | Measures traces, latency, token usage, failures, and estimated model cost. | Shows how the AI system behaves and helps improve reliability and cost. |
| **GitHub Integration** | Reads permitted repositories and creates branches/pull requests after approval. | Connects the AI workflow to real software delivery without autonomous merging. |
| **Secrets Service** | Protects LLM and integration credentials. | Keeps customer credentials out of source code, logs, and model context. |

## Why AI is used here

AI is used where reasoning is ambiguous: understanding a change request, deciding which code is relevant, proposing an implementation plan, and helping generate or review code.

Deterministic software is used where correctness and control matter most: authentication, permissions, tenant isolation, workflow state transitions, path validation, command execution, schema validation, test results, security gates, and approval rules.

That separation is a core architectural principle of this project.

## Core capabilities

- SaaS web control plane
- Personal and organization workspaces
- Simple Admin / Developer role model
- BYOK LLM provider configuration
- GitHub repository connections
- Repository-aware change planning
- LLM tool calling and structured outputs
- Safe, isolated code execution
- Automated test generation and execution
- Static analysis and security validation
- Human-in-the-loop approval gates
- GitHub branch and pull-request automation
- Audit trail for agent decisions and tool calls
- Evaluation harness for plan quality and change correctness
- Tracing, latency, token, and cost measurements
- Provider-neutral LLM abstraction

## Planned stack

- **Language:** Python 3.12+
- **API:** FastAPI
- **Agent orchestration:** explicit state machine, with LangGraph evaluated where it adds value
- **Models:** provider abstraction for OpenAI / Anthropic-compatible backends
- **Schemas:** Pydantic
- **Repository integration:** GitHub API / GitHub App
- **Execution isolation:** Docker
- **Tests:** pytest
- **Quality:** Ruff, mypy
- **Security:** Bandit, dependency scanning, secret scanning
- **Observability:** OpenTelemetry-compatible tracing and structured logs
- **CI/CD:** GitHub Actions
- **Web frontend:** framework to be selected when SaaS implementation begins
- **SaaS persistence/auth/secrets:** to be selected based on Phase 4 requirements

## Development approach: build it and understand it

This project is being developed as both a working system and a hands-on AI engineering portfolio.

For every meaningful task, the implementation process includes a concise explanation of:

- **What we built**
- **Why it exists**
- **How it works**
- **Where it fits in the architecture**
- **What could go wrong**
- **How we test or validate it**
- **How to explain it in an engineering interview**

The goal is not merely to have AI generate a codebase. The goal is to understand and own the architecture, tradeoffs, implementation decisions, and production behavior well enough to defend them technically.

See [docs/LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md) for the running engineering walkthrough.

## Delivery roadmap

### Phase 1 — Working Local MVP
- **P1-T1 — Engineering Foundation**
- **P1-T2 — Domain Models and Configuration**
- **P1-T3 — Repository Analysis Tools**
- **P1-T4 — Planning Agent**
- **P1-T5 — Isolated Change Executor**
- **P1-T6 — Validation and Evidence Bundle**
- **P1-T7 — MVP Demo Scenario**

### Phase 2 — GitHub + Human Approval
- **P2-T1 — GitHub App Integration**
- **P2-T2 — Change Request Intake**
- **P2-T3 — Branch and Patch Workflow**
- **P2-T4 — Automated Test and Security Gate**
- **P2-T5 — Human Approval Gate**
- **P2-T6 — Pull Request Automation**
- **P2-T7 — End-to-End GitHub Demo**

### Phase 3 — Production AI Engineering
- **P3-T1 — Multi-Model Provider Layer**
- **P3-T2 — Agent Evaluation Harness**
- **P3-T3 — Tracing, Metrics, Cost and Latency**
- **P3-T4 — Reliability, Retry and Recovery**
- **P3-T5 — Policy and Security Hardening**
- **P3-T6 — Deployment and CI/CD**
- **P3-T7 — Public Portfolio Release**

### Phase 4 — SaaS Productization
- **P4-T1 — Web Application and Authentication**
- **P4-T2 — Personal and Organization Workspaces**
- **P4-T3 — Admin / Developer Authorization**
- **P4-T4 — BYOK LLM Provider Configuration**
- **P4-T5 — GitHub Connection and Repository Management**
- **P4-T6 — Run, Review, and Approval User Experience**
- **P4-T7 — Multi-Tenant Security and Secrets Hardening**
- **P4-T8 — SaaS Deployment and Portfolio Demonstration**

See [docs/ROADMAP.md](docs/ROADMAP.md) for acceptance criteria.

## Engineering principles

1. AI may implement code, but the system must produce evidence that the change is safe and correct.
2. Generated code is never trusted merely because it compiles.
3. High-risk actions require explicit human approval.
4. Secrets never enter prompts, logs, traces, or source control.
5. Every agent action and tool result should be explainable and auditable.
6. Evaluation is a product feature, not an afterthought.
7. Prefer simple, testable components before adding orchestration complexity.
8. Documentation must evolve with the implementation so the repository always explains the system that actually exists.
9. SaaS tenant boundaries and permissions are deterministic application concerns, not decisions delegated to the LLM.

## How to explain this project in one minute

> AI Release Engineer is a SaaS-based agentic software engineering system I architected to make AI-assisted code changes safer and more production-ready. Users work in personal or organization workspaces, connect approved GitHub repositories, and can bring their own LLM provider credentials. The LLM handles reasoning tasks such as repository understanding and implementation planning, while deterministic services control authentication, permissions, file access, execution, validation, workflow state, and approvals. Generated changes run in an isolated environment, go through automated quality and security gates, and produce an auditable evidence bundle. A human must approve both the implementation plan and the release candidate before the system can create a pull request.

## P1-T1 foundation now being implemented

The engineering foundation introduces:

- `pyproject.toml` as the Python project manifest;
- a production-style `src/ai_release_engineer/` package;
- pytest for automated behavior tests;
- Ruff for linting and formatting checks;
- mypy for static type checking;
- `.env.example` for safe configuration documentation;
- `.gitignore` to prevent local secrets and generated files from entering source control;
- a GitHub Actions quality workflow so the same checks run automatically on pull requests.

These pieces deliberately come before the AI agent itself. They create a controlled software-engineering foundation so later model-generated behavior can be tested and governed.

## P1-T2 domain contracts now being implemented

P1-T2 defines the data contracts that every later AI workflow step will use. Instead of passing around loose dictionaries or free-form model output, the application now has typed schemas for:

- change requests;
- workflow runs and states;
- implementation plans and ordered steps;
- tool execution results;
- validation results;
- human approval records;
- validated runtime configuration.

These contracts are implemented with Pydantic so malformed or unsafe data is rejected before it reaches later parts of the system. This is especially important for AI-generated output: the model may propose data, but the application decides whether that data is valid enough to use.

## P1-T3 repository analysis now being implemented

P1-T3 gives the engine safe, read-only visibility into a local repository. The new RepositoryService can:

- list a repository tree deterministically;
- read UTF-8 text files inside the repository boundary;
- search text and return file/line matches;
- report basic Git metadata such as current branch and commit SHA;
- reject absolute paths and parent-directory escapes;
- skip binary/non-UTF-8 files during text search.

A dedicated fixture repository is included so repository analysis can be tested repeatedly without depending on a developer's real project.

## P1-T4 planning agent

P1-T4 connects the repository-analysis layer to an LLM through a provider-neutral planning interface.

The planning agent now:

- builds a bounded repository context from the tree, Git metadata, and selected text files;
- labels repository contents as untrusted data to reduce prompt-injection risk;
- sends planning work through a provider interface rather than coupling orchestration directly to one vendor;
- includes an OpenAI Responses API adapter using Pydantic structured output;
- captures provider, requested model, resolved model/version, response ID, and token usage;
- rejects plans that reference implausible repository structure;
- remains read-only: it creates a plan but does not modify code.

The local MVP uses an environment-provided OpenAI API key when a live provider call is made. Unit tests use mock providers and never require a real secret.

## P1-T5 isolated change executor

P1-T5 introduces the first controlled write-and-execute boundary.

The executor now:

- copies the source repository into a disposable temporary workspace;
- supports validated create/update file changes only inside that workspace;
- rejects absolute paths, parent traversal, conflicting create/update operations, and symlink escapes;
- keeps the original repository unchanged;
- validates commands against a small allowlist instead of invoking an unrestricted shell;
- runs allowed commands through Docker with networking disabled, Linux capabilities dropped, no-new-privileges enabled, a read-only container filesystem, resource limits, and only the disposable workspace mounted writable;
- enforces command timeouts and bounded stdout/stderr;
- captures exit code, stdout, stderr, duration, and success as ToolResult evidence;
- force-removes timed-out containers on a best-effort basis.

The Docker runner is intentionally separate from the high-level executor so the execution backend can be tested and evolved independently. The default base image is only a runner mechanism; project-specific dependency images will be addressed as the validation/demo workflow matures.

## P1-T6 validation and evidence bundle

P1-T6 turns raw command output and file changes into an auditable review package.

The validation/evidence layer now:

- classifies validation results as test, lint, type, or security;
- preserves the raw ToolResult alongside normalized ValidationResult records;
- runs multiple validation specifications and records all outcomes;
- uses a deterministic ValidationGate that passes only when every required result passed;
- treats failed, skipped, or missing validation evidence as not ready to continue;
- creates per-file change summaries with create/update operation, additions, and deletions;
- creates a bounded unified diff for human review;
- captures request, implementation plan, model-call metadata, tool results, validation results, approvals, and change summary in one versioned EvidenceBundle;
- derives overall evidence status from validation results instead of accepting a caller-supplied success flag;
- serializes the bundle to JSON for future storage, APIs, audit history, and the SaaS review screen.

The Phase 1 security result is a typed evidence category. Full production security scanning policy and scanner integration are expanded later in the roadmap.

## Phase 1 MVP demo

P1-T7 connects the Phase 1 components into one reproducible local workflow against a tiny greeting-service repository.

The demo proves this sequence:

```text
bounded change request
      |
      v
safe repository analysis
      |
      v
structured implementation plan
      |
      v
recorded plan approval
      |
      v
disposable repository copy
      |
      v
bounded file implementation
      |
      +--> pytest
      +--> Ruff
      +--> mypy
      |
      v
deterministic validation gate
      |
      v
versioned EvidenceBundle JSON
```

### Important Phase 1 scope note

The demo intentionally uses a **deterministic planning provider and scenario-specific FileChange objects** so the workflow is reproducible without an API key, token cost, or nondeterministic model output.

The real OpenAI planning adapter built in P1-T4 remains part of the engine. Phase 1 demonstrates the governed workflow around planning and code changes; later phases connect that workflow to live GitHub branches, model-driven patch creation, stronger security gates, and pull-request automation.

### Run the demo

Prerequisites:

- Python 3.12+
- Docker
- `make`

Install the local project once:

```bash
python -m pip install -e ".[dev]"
```

Run the successful scenario:

```bash
make demo-success
```

This builds the local validation image, applies the requested feature only inside a disposable repository copy, runs pytest/Ruff/mypy with Docker networking disabled, and writes the evidence bundle to:

```text
.demo-output/mvp-success.json
```

Run the intentionally failing scenario:

```bash
make demo-failure
```

The failing scenario deliberately introduces incorrect excited-greeting behavior. Pytest fails, the ValidationGate blocks success, and the evidence bundle is written to:

```text
.demo-output/mvp-validation-failure.json
```

The failure command exits with status code `2` intentionally because the validation gate correctly blocked the change.

## Status

**Current phase:** Phase 1  
**Current task:** P1-T7 — MVP Demo Scenario (implementation branch active; validation pending)

See [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) for live status.
