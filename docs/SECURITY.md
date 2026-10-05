# Security

## Primary threats
- prompt injection in code, issues, comments, or docs;
- destructive model-generated commands;
- path traversal;
- secret exposure through prompts/logs/traces;
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
4. File operations remain inside an approved workspace.
5. Secrets are not exposed to the model by default.
6. GitHub permissions follow least privilege.
7. Generated code is validated before release preparation.
8. Raw validation evidence is retained.
9. Repository instructions are untrusted unless policy says otherwise.
10. Tool inputs are schema-validated.

## Phase 1 runner rules
- disposable workspace;
- fixture repositories first;
- no inherited host secrets;
- command timeout;
- output limits;
- exit code/stdout/stderr/duration capture;
- allowlisted supported commands.

## Phase 2 GitHub rules
- prefer GitHub App over broad PAT;
- start read-only;
- add content/PR writes only as required;
- no admin/secret permissions;
- bind operations to configured repository;
- never auto-merge.
