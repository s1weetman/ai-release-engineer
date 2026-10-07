# Roadmap

Task IDs are stable. A task is complete only when all acceptance criteria are satisfied.

# Phase 1 — Working Local MVP

## P1-T1 — Engineering Foundation
- Python 3.12+ project metadata.
- src package layout.
- pytest, Ruff, mypy configured.
- GitHub Actions runs tests/static checks.
- .env.example with no secrets.
- baseline unit test passes.

## P1-T2 — Domain Models and Configuration
- change request schema;
- workflow state schema;
- implementation plan schema;
- tool/validation result schemas;
- approval model;
- safe environment configuration.

## P1-T3 — Repository Analysis Tools
- tree listing;
- safe file read;
- text/code search;
- repository metadata;
- path traversal prevention;
- normal/malicious path tests;
- fixture repository.

## P1-T4 — Planning Agent
- provider interface;
- one provider adapter;
- structured plan output;
- malformed output rejected;
- actual repository paths where applicable;
- provider/model/token metadata captured;
- mockable tests.

## P1-T5 — Isolated Change Executor
- disposable workspace;
- bounded file changes;
- timeout/output limits;
- exit code/stdout/stderr/duration capture;
- unsafe command/path rejection;
- fixture tests.

## P1-T6 — Validation and Evidence Bundle
- test/lint/type/security result schemas;
- diff/change summary;
- serializable evidence bundle;
- failed validation blocks success.

## P1-T7 — MVP Demo Scenario
- fixture app + bounded feature request;
- analysis -> plan -> approval -> implementation -> validation;
- reproducible demo command;
- success and failure examples;
- README demo instructions.

# Phase 2 — GitHub + Human Approval

## P2-T1 — GitHub App Integration
Least-privilege integration, safe credential handling, mockable client.

## P2-T2 — Change Request Intake
CLI/API intake, optional GitHub issue ingestion, sanitization, auditable run ID.

## P2-T3 — Branch and Patch Workflow
Approved-plan-to-patch generation, isolated branch, bounded writes, commit/diff metadata, and never write directly to the default branch.

## P2-T4 — Automated Test and Security Gate
Tests, lint, type, security, secret checks; deterministic pass/fail policy.

## P2-T5 — Human Approval Gate
Explicit plan and release approvals with actor/time/run audit records; no bypass.

## P2-T6 — Pull Request Automation
Create PR only after release approval; include summary/evidence/run ID; no auto-merge.

## P2-T7 — End-to-End GitHub Demo
Public issue/change-request-to-PR scenario plus failure scenario.

# Phase 3 — Production AI Engineering

## P3-T1 — Multi-Model Provider Layer
At least two providers, normalized usage/errors, tested fallback policy.

## P3-T2 — Agent Evaluation Harness
Versioned eval dataset, quality rubric, correctness checks, unsafe-action tests, measurable baseline.

## P3-T3 — Tracing, Metrics, Cost and Latency
Per-run traces, spans for LLM/tools/validation, tokens, estimated cost, latency, secret filtering.

## P3-T4 — Reliability, Retry and Recovery
Error categories, bounded retries, useful checkpoints, idempotent GitHub actions, recovery tests.

## P3-T5 — Policy and Security Hardening
Prompt-injection suite, command/path allowlists, permission review, dependency/secret scanning.

## P3-T6 — Deployment and CI/CD
Container image, deployment docs, CI gates, reproducible environment, health/readiness, rollback.

## P3-T7 — Public Portfolio Release
Polished README, architecture diagram, public engine demo, walkthrough plan, evaluation table, cost/latency results, tradeoffs, resume-ready summary.

# Phase 4 — SaaS Productization

## P4-T1 — Web Application and Authentication
- web application shell;
- sign-up/sign-in/sign-out;
- authenticated session handling;
- protected routes;
- initial dashboard;
- API integration boundary established.

## P4-T2 — Personal and Organization Workspaces
- personal workspace automatically available to a user;
- create organization;
- organization membership model;
- workspace switcher;
- workspace-owned repositories/runs/configuration;
- tenant-isolation tests.

## P4-T3 — Admin / Developer Authorization
- Admin and Developer roles;
- server-side authorization policy;
- Admin member management;
- Admin integration/credential management;
- Developer engineering workflow access;
- unauthorized-action tests.

## P4-T4 — BYOK LLM Provider Configuration
- supported provider configuration UI;
- encrypted secret storage;
- masked secret display;
- rotation/revocation flow;
- organization credentials Admin-only;
- provider connectivity validation;
- no secret leakage in logs/traces/responses.

## P4-T5 — GitHub Connection and Repository Management
- GitHub App installation flow;
- personal or organization workspace binding;
- selected repository discovery;
- connected repository list;
- permission validation;
- revoke/disconnect flow.

## P4-T6 — Run, Review, and Approval User Experience
- new change request screen;
- repository selection;
- run status/progress;
- implementation plan review;
- plan approve/reject;
- validation and evidence view;
- diff review;
- release approve/reject;
- run history.

## P4-T7 — Multi-Tenant Security and Secrets Hardening
- cross-tenant access test suite;
- role escalation tests;
- secure audit log;
- rate/resource controls;
- secrets threat model verification;
- security review of browser/API boundaries;
- backup/restore plan for SaaS data.

## P4-T8 — SaaS Deployment and Portfolio Demonstration
- deploy frontend and API;
- deploy isolated worker path;
- health/readiness monitoring;
- production configuration documentation;
- end-to-end personal workspace demo;
- end-to-end organization demo;
- public screenshots/walkthrough;
- README and architecture finalized.

## Deferred product options

The following are intentionally deferred until product validation:

- billing/subscriptions;
- Reviewer/Approver/Tester roles;
- GitLab/Bitbucket;
- enterprise SSO;
- self-hosted/private-network execution runner;
- customer-managed encryption keys.
