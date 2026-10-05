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
