# Architecture Decision Log

## ADR-001 — Human approval is a hard release boundary
**Status:** Accepted  
The system may plan, modify, test, and prepare changes, but does not merge or deploy without explicit human approval.

## ADR-002 — Python is the primary implementation language
**Status:** Accepted  
Python 3.12+ is used for orchestration/API because of its strong AI, automation, testing, and API ecosystem.

## ADR-003 — Provider-neutral model boundary
**Status:** Accepted  
LLM access is behind an internal provider interface to enable model comparison, fallback, and testability.

## ADR-004 — Explicit workflow state machine first
**Status:** Accepted  
Start explicit; add orchestration frameworks only when they solve a demonstrated need.

## ADR-005 — Isolated execution for generated changes
**Status:** Accepted  
Generated changes and validation commands execute in an isolated workspace, with Docker as the target implementation.

## ADR-006 — Evidence bundle is a first-class output
**Status:** Accepted  
Each run should retain plan, changed files, diff summary, commands, tests, security results, model metadata, timing, and approvals.
