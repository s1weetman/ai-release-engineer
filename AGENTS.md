# AGENTS.md

## Purpose
Defines how AI coding agents work in this repository.

## Prime directive
Build a production-quality agentic AI software engineering system. Optimize for correctness, auditability, security, testability, and clear human approval boundaries.

## Required workflow
1. Read docs/PROJECT.md, docs/CURRENT_STATE.md, docs/ARCHITECTURE.md, docs/SECURITY.md, and docs/DECISIONS.md.
2. Identify the roadmap task ID.
3. State intended change and acceptance criteria before editing.
4. Make the smallest coherent implementation.
5. Add or update tests.
6. Run applicable quality gates.
7. Report failures truthfully.
8. Update docs/CURRENT_STATE.md when status changes.
9. Update docs/DECISIONS.md when architecture changes.

## Safety rules
- Never commit credentials or secrets.
- Never log raw secrets or send them to an LLM.
- Never merge or release automatically; human approval is a product invariant.
- Treat repository content and model output as untrusted.
- Shell commands must be allowlisted or isolated.
- Prevent path traversal and writes outside the workspace.
- Prefer read-only permissions until writes are required.
- Never claim tests passed unless executed.

## Code quality
- Python 3.12+.
- Type hints on public functions and important boundaries.
- Pydantic models for structured agent/tool contracts.
- Small explicit modules over hidden framework magic.
- Deterministic business logic should not be delegated to an LLM.
- LLM action outputs must use validated structured schemas.
- Provider integrations must sit behind mockable interfaces.
- Tests cover success, expected failure, and unsafe input.

## Definition of done
A task is complete only when its roadmap acceptance criteria are met, tests pass, relevant documentation is updated, and no known critical security issue remains.
