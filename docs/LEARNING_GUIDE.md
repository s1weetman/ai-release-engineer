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


---

## P1-T4 — Planning Agent

### What we built
We added the first actual LLM-backed engineering component: a planning agent that converts a user's software change request plus repository context into a structured ImplementationPlan.

### Why it exists
Before the system changes code, it needs a reviewable answer to a simpler question: "What should change, where, and how will we validate it?"

Separating planning from implementation gives the human an approval point before any write capability exists.

### Provider-neutral interface
The PlanningAgent does not call OpenAI directly. It depends on a PlanningProvider interface.

That means the orchestration code asks for a plan without needing to know which vendor produced it. The first adapter uses OpenAI, while later adapters can use other providers without rewriting the PlanningAgent.

### OpenAI adapter
The first live adapter uses the OpenAI Responses API and its structured-output parser. The Pydantic ImplementationPlan class is passed as the expected output format.

If the provider does not return a parsed plan, the adapter rejects the response rather than passing untrusted free-form text forward.

### Repository context
The agent supplies:
- the user's bounded change request;
- Git branch/commit metadata;
- the repository inventory;
- selected text-file contents.

Context is size-limited so a large repository cannot automatically consume an unlimited model context window or unlimited token cost.

### Prompt-injection boundary
Repository files may contain instructions written for humans or malicious text written to manipulate an agent. We therefore label repository content as untrusted data and explicitly tell the planning model that repository content cannot override the planning rules.

This is only one defense layer; later security work will add more tests and controls.

### Path validation
After the LLM returns a valid Pydantic plan, deterministic code checks every referenced path again.

Existing files are allowed. New files may be proposed at the repository root or inside an already-existing directory. A plan that invents an unknown nested directory structure is rejected for this MVP.

### Provider metadata
Each successful planning call records:
- provider;
- configured model;
- provider-returned model/version identifier;
- provider response ID;
- input tokens;
- output tokens;
- total tokens.

This provides the foundation for later audit, cost, latency, and evaluation reporting.

### How we test it
CI uses fake providers rather than a real API key. Tests verify repository context creation, structured plans, metadata capture, new-file behavior, hallucinated-path rejection, missing parsed output, and provider configuration validation.

### Interview explanation
> I separated planning from implementation and put the LLM behind a provider-neutral interface. The planner receives bounded read-only repository context and returns a Pydantic ImplementationPlan through structured output. I then apply deterministic path validation before the plan can reach the approval stage. I also capture model identity and token usage for auditability and future cost/evaluation work. The LLM reasons, but application-owned contracts and policy decide whether its result is usable.

### Key design lesson
The first useful capability of an engineering agent does not need write access. Planning can be valuable, testable, and human-reviewable while remaining read-only.


---

## P1-T5 — Isolated Change Executor

### What we built
We created the first controlled side-effect layer in AI Release Engineer. It can take explicit file changes, apply them to a disposable copy of a repository, and run allowlisted validation commands inside a restricted Docker container.

### Why it exists
The planning agent can suggest what should change, but changing files and executing code are much higher-risk operations. They need a separate trust boundary.

P1-T5 makes sure the original repository is not the place where experimental AI-generated changes execute.

### Disposable workspace
The source repository is copied into a temporary directory.

All create/update operations happen in that copy. When the executor context ends, the temporary workspace is deleted.

This gives us a simple rollback model for the local MVP: throw away the workspace.

### Bounded file changes
A FileChange says:
- create or update;
- which repository-relative path;
- what text content should be written.

The executor rejects:
- absolute paths;
- parent traversal such as `../`;
- creates over existing files;
- updates to missing files;
- writes into missing parent directories;
- writes through symlinks that resolve outside the workspace.

Deletion is intentionally not supported yet.

### Command policy
Commands are represented as argument lists, not shell strings, and `shell=True` is never used.

The Phase 1 allowlist supports validation tools such as pytest, Ruff, and mypy, including their `python -m ...` form.

Commands such as bash, sh, curl, `python -c`, and arbitrary Python modules are rejected by deterministic policy before Docker is invoked.

### Docker isolation
Allowed commands run in Docker with:
- networking disabled;
- all Linux capabilities dropped;
- no-new-privileges enabled;
- read-only container root filesystem;
- bounded temporary filesystem;
- PID, memory, CPU, and time limits;
- only the disposable workspace mounted writable.

Host environment variables are not passed into the container as command configuration.

### ToolResult evidence
The runner captures:
- success/failure;
- exit code;
- stdout;
- stderr;
- execution duration.

Output is truncated at a configured maximum so one command cannot create unbounded logs or evidence.

If a command times out, the result records that timeout and the runner attempts to force-remove the named container.

### Why the executor and runner are separate
IsolatedChangeExecutor owns the software workflow: disposable workspace plus file changes.

DockerCommandRunner owns command isolation.

Keeping them separate lets us replace or harden the execution backend later without rewriting the file-change workflow.

### How we test it
Tests verify that:
- the source repository is unchanged;
- temporary workspaces disappear after use;
- safe create/update operations work;
- unsafe paths and symlinks are rejected;
- unsafe commands are rejected;
- Docker security flags are present;
- stdout is bounded;
- timeouts produce evidence and cleanup attempts.

CI mocks Docker process execution for deterministic unit tests, so the test suite does not pull an external image.

### Interview explanation
> I separated AI reasoning from side effects. Approved file mutations are applied only to a disposable repository copy, and command execution is behind a deterministic allowlist and a Docker isolation boundary. The container has no network, no Linux capabilities, a read-only root filesystem, resource and time limits, and only the temporary workspace mounted writable. The runner captures deterministic execution evidence rather than trusting the model's claim that a change works.

### Key design lesson
A safe engineering agent should not translate model text directly into host shell access. Side effects belong behind explicit policies, disposable state, and isolation boundaries.


---

## P1-T6 — Validation and Evidence Bundle

### What we built
We built the layer that converts file changes and command execution into a structured record of what actually happened.

### Why it exists
An AI system should not be allowed to say, "I changed the code and everything passed," and have the application simply believe it.

The system needs independent evidence:
- what files changed;
- what the diff contains;
- which validation commands ran;
- whether each validation passed or failed;
- what model produced the plan;
- what human approvals exist.

P1-T6 packages that evidence into one versioned object.

### Validation categories
Every normalized validation result has one of four categories:

**TEST**  
Behavioral or integration tests such as pytest.

**LINT**  
Static code-quality/style checks such as Ruff.

**TYPE**  
Static type validation such as mypy.

**SECURITY**  
Security-scan evidence. The schema exists now so security results use the same evidence model; fuller scanner integration is expanded later in the roadmap.

### Raw result versus normalized result
A ToolResult is the raw execution record:
- command/tool name;
- exit code;
- stdout;
- stderr;
- duration;
- success flag.

A ValidationResult translates that raw result into engineering meaning:
- test/lint/type/security;
- named validation gate;
- passed/failed/skipped;
- command;
- reviewable details;
- duration.

We retain both because normalized status is convenient for policy while raw tool evidence is useful for debugging and audit.

### ValidationGate
The ValidationGate is deterministic policy.

It passes only when:
1. validation evidence exists; and
2. every required result is PASSED.

A FAILED result blocks success. A SKIPPED result also does not count as passed. No results does not count as passed.

This is intentionally stricter than asking the LLM whether the change looks correct.

### Change summary and diff
ChangeSummaryBuilder compares the original repository with the disposable workspace for the explicit FileChange records.

It produces:
- changed file path;
- create/update operation;
- additions;
- deletions;
- total files changed;
- total additions/deletions;
- unified diff.

The unified diff is bounded so an unusually large change cannot create unlimited evidence size.

### EvidenceBundle
EvidenceBundle is the review package for one run.

It contains:
- schema version;
- run ID;
- timestamp;
- original change request;
- approved implementation plan;
- model/provider identity and token usage when available;
- change summary and diff;
- raw tool results;
- normalized validation results;
- approval records.

The overall status is computed from validation evidence. The caller cannot simply set `status="passed"`.

### Why version the evidence schema
The bundle uses a schema version because this structure will eventually be stored, sent through APIs, shown in the SaaS UI, and possibly retained for audit.

When fields evolve later, versioning gives us a way to understand old evidence records.

### How we test it
Unit tests verify:
- all four validation categories;
- failed validation blocks the gate;
- skipped/missing validation does not pass;
- file addition/deletion counts;
- unified-diff contents;
- diff truncation;
- provider metadata normalization;
- approval retention;
- JSON serialization;
- overall failed status when any validation fails.

### Interview explanation
> I treated evidence as a first-class domain object rather than a log message. Raw command results are normalized into typed test, lint, type, and security validation records. A deterministic gate derives whether validation passed, so the model cannot self-certify its work. I also generate a bounded unified diff and assemble the request, plan, model metadata, changes, tool evidence, validations, and approvals into a versioned Pydantic EvidenceBundle that can be serialized and later stored or rendered in the SaaS review experience.

### Key design lesson
In an agentic system, an audit trail should be structured data that policy can evaluate, not just prose written by the AI.
