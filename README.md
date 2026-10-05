# AI Release Engineer

A production-oriented agentic AI system that plans, implements, tests, validates, and prepares software changes for human-approved release.

## Why this project exists

AI Release Engineer demonstrates how modern AI-assisted software engineering can be made safe, observable, testable, and useful in real delivery workflows. The system accepts a software change request, inspects a repository, produces an implementation plan, generates or modifies code, runs validation checks, and prepares a pull request while keeping a human approval gate before release.

This is not a toy chatbot. The engineering focus is on agent orchestration, tool use, code quality, evaluation, security, CI/CD, observability, and production reliability.

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

## Status

**Current phase:** Phase 1  
**Current task:** P1-T1 — Engineering Foundation

See [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) for live status.
