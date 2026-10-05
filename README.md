# AI Release Engineer

A production-oriented agentic AI system that plans, implements, tests, validates, and prepares software changes for human-approved release.

## Why this project exists

AI Release Engineer demonstrates how modern AI-assisted software engineering can be made safe, observable, testable, and useful in real delivery workflows. The system accepts a software change request, inspects a repository, produces an implementation plan, generates or modifies code, runs validation checks, and prepares a pull request while keeping a human approval gate before release.

This is not a toy chatbot. The engineering focus is on agent orchestration, tool use, code quality, evaluation, security, CI/CD, observability, and production reliability.

## What the system does

At a high level, AI Release Engineer acts like a governed AI software engineer:

1. A user gives it a bounded software change request.
2. It inspects the target repository and gathers relevant context.
3. An LLM produces a structured implementation plan.
4. A human reviews and approves that plan.
5. The system performs the change inside an isolated workspace.
6. Automated tests, static analysis, type checks, and security checks validate the result.
7. The system creates an evidence bundle showing exactly what changed and what passed or failed.
8. A human approves the release candidate.
9. The system prepares a GitHub pull request.
10. It never automatically merges or deploys production code.

## Target workflow

```text
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
| **API / CLI** | Receives the change request, repository target, and human approvals. | Gives people and other systems a controlled way to interact with the platform. |
| **Orchestrator** | Tracks the workflow state and decides what step happens next. | Prevents the LLM from controlling the entire system on its own. |
| **LLM Provider Layer** | Sends reasoning tasks to an AI model and returns validated structured responses. | Lets the system use AI for planning and code reasoning without locking the architecture to one vendor. |
| **Repository Service** | Safely lists files, reads code, searches text, and builds repository context. | Gives the agent the information it needs while restricting what it can access. |
| **Tool Layer** | Exposes explicit operations the agent may request. | Turns model intent into controlled, testable software actions. |
| **Execution Sandbox** | Runs generated changes and commands in an isolated environment. | Protects the host system from unsafe or broken generated code. |
| **Validation Pipeline** | Runs tests, linting, type checking, security scanning, and other quality gates. | Provides objective evidence instead of trusting the model when it says the code works. |
| **Policy / Approval Layer** | Enforces rules and human approval checkpoints. | Makes safety and release authority deterministic rather than model-controlled. |
| **Evidence Bundle** | Records the plan, changed files, diff, commands, validation results, model metadata, and approvals. | Makes every AI-assisted change explainable and auditable. |
| **Telemetry / Observability** | Measures traces, latency, token usage, failures, and estimated model cost. | Shows how the AI system behaves in production and helps improve reliability and cost. |
| **GitHub Integration** | Creates branches and pull requests after approval. | Connects the AI workflow to a real software delivery process without allowing autonomous merging. |

## Why AI is used here

AI is used where reasoning is ambiguous: understanding a change request, deciding which code is relevant, proposing an implementation plan, and helping generate or review code.

Deterministic software is used where correctness and control matter most: permissions, workflow state transitions, path validation, command execution, schema validation, test results, security gates, and approval rules.

That separation is a core architectural principle of this project.

## Core capabilities

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

## How to explain this project in one minute

> AI Release Engineer is an agentic software engineering system I architected to make AI-assisted code changes safer and more production-ready. The LLM handles reasoning tasks such as repository understanding and implementation planning, while deterministic services control file access, execution, validation, workflow state, and approvals. Generated changes run in an isolated environment, go through automated quality and security gates, and produce an auditable evidence bundle. A human must approve both the implementation plan and the release candidate before the system can create a pull request. The project demonstrates agent orchestration, structured tool use, secure execution, evaluation, observability, GitHub automation, and human-in-the-loop AI engineering.

## Status

**Current phase:** Phase 1  
**Current task:** P1-T1 — Engineering Foundation

See [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) for live status.
