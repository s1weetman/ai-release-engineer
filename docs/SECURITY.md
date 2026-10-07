# Security

## Primary threats

- prompt injection in code, issues, comments, or docs;
- destructive model-generated commands;
- path traversal;
- cross-tenant data access;
- broken role authorization;
- LLM API key exposure;
- GitHub credential exposure;
- secret leakage through prompts, logs, traces, evidence, or browser responses;
- excessive GitHub permissions;
- dependency/supply-chain attacks;
- generated code exfiltration;
- resource exhaustion;
- false model claims of success;
- approval bypass.

## Security invariants

1. No autonomous merge or production deployment.
2. Human approval is enforced in deterministic policy code.
3. Model output cannot directly execute arbitrary host commands.
4. File operations remain inside an approved execution workspace.
5. Every SaaS data request is scoped to an authenticated workspace.
6. Role authorization is enforced on the server, never only in the UI.
7. Raw customer secrets are never returned after secure storage.
8. Secrets are not exposed to the model by default.
9. GitHub permissions follow least privilege.
10. Generated code is validated before release preparation.
11. Raw validation evidence is retained.
12. Repository instructions are untrusted unless policy says otherwise.
13. Tool inputs are schema-validated.
14. Tenant identifiers come from authenticated server-side context, not trusted client input alone.

## SaaS tenant rules

- Every user has an authenticated identity.
- Organization resources require an active membership.
- Workspace queries always include tenant/workspace scoping.
- Admin-only mutations are checked server-side.
- Audit records capture security-sensitive administrative actions.
- Tests must include attempts to access another workspace's data.

## LLM BYOK rules

- Provider secrets are encrypted at rest using a managed secrets mechanism or envelope encryption.
- The application stores a provider identifier, credential metadata, and encrypted secret material—not plaintext API keys.
- Secret values are masked after creation.
- Secret values are not written to logs, telemetry, errors, evidence bundles, analytics, or model prompts unless an explicitly reviewed provider request requires the credential at transport time.
- Rotation and revocation are supported.
- Organization provider credentials are writable only by Admins.

## GitHub rules

- Prefer GitHub App installations over broad personal access tokens.
- Install only on selected repositories where practical.
- Start read-only; add contents/pull-request write permissions only when required.
- Use short-lived installation tokens.
- Never request admin or secret-management permissions.
- Bind operations to the authenticated workspace and configured installation.
- Never auto-merge.

## Phase 1 runner rules

- source repositories are copied to disposable workspaces before mutation;
- fixture repositories are used first in automated tests;
- create/update paths are validated against workspace boundaries;
- symlinks cannot be used to write outside the workspace;
- deletion is not supported in the Phase 1 executor;
- commands are argument arrays, not unrestricted shell strings;
- supported validation commands are explicitly allowlisted;
- Docker command execution uses no network;
- Docker drops Linux capabilities and enables no-new-privileges;
- Docker root filesystem is read-only, with only bounded temporary storage plus the workspace writable;
- host secrets are not intentionally injected into the command container;
- CPU, memory, PID, command timeout, and output limits are applied;
- exit code/stdout/stderr/duration are captured;
- timed-out named containers receive best-effort forced cleanup.

## Future private-environment runner

If a self-hosted runner is added later:

- outbound connectivity must be configurable;
- runner identity must be authenticated;
- jobs must be tenant-bound and signed/authorized;
- secret delivery must be scoped and short-lived;
- source code should not be copied to the SaaS control plane unless explicitly configured.
