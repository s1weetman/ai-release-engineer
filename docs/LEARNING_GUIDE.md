# Engineering Learning Guide

This document is the running technical walkthrough for AI Release Engineer. It exists so the project owner can understand, explain, and defend the system as it is built.

## How to use this guide

For each roadmap task, record:

1. **What we built**
2. **Why it exists**
3. **How it works**
4. **Where it fits**
5. **How we validate it**
6. **Key terms to know**
7. **Interview explanation**
8. **Questions or tradeoffs to review**

The objective is understanding, not memorization.

---

# Phase 1

## P1-T1 — Engineering Foundation

### What we are building
The base Python project and engineering quality system that every later AI component will depend on.

### Why it exists
Before adding agents, models, or GitHub automation, the repository needs a predictable structure and automatic checks. This prevents the project from turning into a collection of scripts that are difficult to test or explain.

### Pieces in this task

**pyproject.toml**  
Defines the Python package, supported Python version, dependencies, development tools, and configuration for linting, typing, and testing. Think of it as the engineering manifest for the Python application.

**src/ai_release_engineer/**  
Holds the actual application code. A src-layout prevents accidental imports from the repository root and encourages the code to behave like an installable production package.

**pytest**  
Runs automated tests. As the AI system becomes more autonomous, tests are critical because we do not trust model confidence as proof that behavior is correct.

**Ruff**  
Performs fast Python linting and formatting checks. It catches common defects and keeps the codebase consistent.

**mypy**  
Performs static type checking. It helps catch invalid assumptions about data before runtime, which becomes especially important when many components exchange structured agent/tool results.

**.env.example**  
Documents environment variables the application expects while containing no real credentials. Real secrets remain outside source control.

**.gitignore**  
Prevents local environments, caches, secrets, generated files, and other machine-specific artifacts from being committed.

**GitHub Actions**  
Runs quality checks automatically when code changes. This turns testing and static analysis into repeatable engineering gates rather than something a developer has to remember manually.

### Where P1-T1 fits
This is the foundation layer. The planning agent, repository tools, execution sandbox, GitHub integration, and observability system will all sit on top of it.

### What has now been implemented
The P1-T1 branch contains the project manifest, installable package layout, baseline application metadata, unit tests, environment-variable template, ignore rules, and the GitHub Actions quality pipeline.

The small health/version module is intentionally simple. It gives us deterministic code to prove that packaging, importing, typing, linting, and testing all work before we add an LLM. We are testing the engineering foundation itself before placing AI behavior on top of it.

### How the automated gate works
When a pull request is opened, GitHub Actions creates a clean Linux environment, installs Python 3.12 and the project, then runs four independent checks:

1. Ruff lint — finds code-quality problems.
2. Ruff format check — verifies consistent formatting.
3. mypy — checks Python type contracts without running the application.
4. pytest — executes the behavioral tests.

A failure in any step makes the quality job fail. That is the beginning of our deterministic guardrail philosophy: the AI cannot simply claim that its code is good; independent tools must verify it.

### How we validate it
P1-T1 is complete only when the baseline test suite, Ruff, formatting, and mypy run successfully in GitHub Actions on the pull request.

### Interview explanation
> I started by establishing a conventional Python src-layout and automated quality gates before introducing the LLM. I wanted the AI functionality to sit inside a testable software system rather than letting the model become the architecture. pytest validates behavior, Ruff enforces code quality, mypy checks type contracts, and GitHub Actions makes those checks repeatable on every change.

### Key design lesson
The LLM is a component of the application. It is not the application architecture.


---

## P1-T2 — Domain Models and Configuration

### What we built
We added the typed data contracts that define what information is allowed to move through the system.

### Why it exists
AI systems often fail when free-form text is treated as if it were trustworthy application data. P1-T2 creates a strict boundary: the LLM can propose information, but the application validates it before using it.

### Main contracts

**ChangeRequest**  
Represents what the user wants changed and which repository the request applies to.

**WorkflowState / WorkflowRun**  
Defines the legal lifecycle vocabulary for a run: received, analyzing, plan ready, approved, implementing, validating, review ready, release approved, PR prepared, failed, or cancelled.

**ImplementationPlan / PlanStep**  
Represents the AI's proposed implementation as structured data instead of a paragraph. Plan steps have deterministic ordering and bounded repository-relative paths.

**ToolResult**  
Represents what happened when a controlled tool runs: success/failure, exit code, output, errors, and duration.

**ValidationResult**  
Normalizes test, lint, type, and security gate results into passed, failed, or skipped outcomes.

**ApprovalRecord**  
Records a human plan or release decision, who made it, when it happened, and an optional comment.

**Settings**  
Loads environment-based runtime configuration through validation. Invalid timeouts, unsupported environment names, or other malformed configuration fail early instead of creating unpredictable runtime behavior.

### Why Pydantic
Pydantic turns Python type definitions into runtime validation. If an LLM returns malformed structured output, or an API caller sends data that violates our contract, validation fails before the rest of the system acts on it.

### Security example
A PlanStep rejects repository paths such as `../secrets.txt`. That does not replace the later filesystem sandbox, but it creates an early defense-in-depth boundary.

### How we validate it
Unit tests cover valid models and intentional failures. GitHub Actions must then run Ruff, formatting, mypy, and pytest successfully.

### Interview explanation
> Before connecting an LLM, I defined strict Pydantic domain contracts for requests, workflow state, implementation plans, tool results, validation evidence, approvals, and runtime configuration. The model is not allowed to drive the application with arbitrary free-form data. Its outputs must cross validated schemas before deterministic code can act on them. That gives us a clean boundary between probabilistic AI reasoning and controlled application behavior.

### Key design lesson
Structured output is not trustworthy merely because it is JSON. It becomes usable only after the application validates it against rules it owns.


---

## P1-T3 — Repository Analysis Tools

### What we built
We added a read-only RepositoryService that can inspect a local source repository without allowing arbitrary filesystem access.

### Why it exists
Before the AI can create a useful implementation plan, it needs evidence about the codebase: what files exist, what those files contain, where relevant text appears, and which Git revision is being inspected.

The important part is that the AI does not receive unrestricted file-system access. It gets a controlled service with specific read-only capabilities.

### Main capabilities

**Repository tree listing**  
Returns a deterministic inventory of files and directories while excluding the internal `.git` directory.

**Safe file reading**  
Reads UTF-8 text files only after resolving the requested path against the configured repository root.

**Text search**  
Searches repository text files for a literal string and returns the file path, line number, and matching line.

**Repository metadata**  
Reads basic Git information such as current branch and commit SHA without modifying the repository.

**Boundary enforcement**  
Paths such as `../outside.txt` or `/etc/passwd` are rejected before reading.

**Fixture repository**  
Tests run against a tiny repository stored under `tests/fixtures`, so results are repeatable and do not depend on a developer machine.

### How path protection works
The service resolves both the repository root and the requested file to canonical filesystem paths. It then verifies that the requested path is still underneath the repository root. If not, it raises `UnsafeRepositoryPathError`.

This is a practical example of least privilege: the future planning agent gets only the repository visibility it needs, not general access to the machine.

### Why read-only first
P1-T3 intentionally contains no write, delete, commit, or shell-execution capability. Reading and changing code are separated into different trust boundaries. Write/execution capabilities arrive later inside isolated workflows.

### Quality issue we found
After P1-T2 was merged, the main quality workflow found one Ruff modernization rule involving `timezone.utc`. The code was functionally fine, but our automated quality gate correctly rejected it. P1-T3 carries the correction forward so the entire suite can be green again.

### How we validate it
Tests cover normal tree listing, file reading, search results, non-Git metadata behavior, missing roots, and malicious path escape attempts.

### Interview explanation
> I separated repository understanding from code modification. The planning side gets a read-only RepositoryService that exposes explicit operations for tree listing, bounded file reads, text search, and Git metadata. Every requested path is canonicalized and checked to ensure it remains under the repository root. That gives the LLM enough context to reason about code without giving it general filesystem authority.

### Key design lesson
Giving an AI "access to the repo" should not mean giving it unrestricted access to the host filesystem.
