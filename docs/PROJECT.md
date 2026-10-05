# Project Definition

## Product statement
AI Release Engineer is an agentic software engineering system that can analyze a codebase, plan a requested change, implement the change in an isolated workspace, validate it with automated checks, and prepare the result for human-approved release.

## Portfolio objective
Demonstrate senior-level applied AI engineering through a real system combining LLM/agent orchestration, structured tool calling, code generation/review, testing, secure execution, GitHub automation, observability, evaluation, and delivery engineering.

## MVP user story
Given a repository and a bounded change request, the system can:
1. inspect relevant repository content;
2. generate a structured implementation plan;
3. obtain approval for the plan;
4. implement the change in an isolated workspace;
5. run tests and quality/security checks;
6. produce a structured evidence bundle;
7. stop for human approval;
8. prepare a GitHub pull request.

## Non-goals
- unrestricted autonomous production deployment;
- automatic merging without approval;
- training a foundation model;
- supporting every language in v1;
- hiding AI-generated code behind unverifiable claims.

## Success criteria
- reproducible end-to-end demo;
- automated tests for the same scenario;
- validated schemas for model-driven actions;
- unsafe/invalid actions rejected;
- traces and usage metrics captured;
- evaluation results published;
- public architecture/tradeoff documentation;
- reproducible deployment instructions.
