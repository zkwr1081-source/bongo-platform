# NEXORA Connected Execution Agent — Architecture Blueprint

## Goal

Evolve the current NEXORA agent dashboard and `POST /api/agents/run` into a controlled execution agent that can discover connected integrations, prepare actions, execute only explicitly permitted actions, and report verifiable outcomes.

This document is a design blueprint, not a claim that connectors or transaction signing are already implemented.

## Current repository baseline

- `server.py` exposes a local dashboard, status endpoints, and an agent-run endpoint.
- `nexora_model_adapter.py` sends agent prompts to an OpenAI-compatible Chat Completions provider using environment-based credentials.
- `NEXORA_EXECUTION_TOKEN` is an optional bearer check. If unset, the execution endpoint has no token guard; the browser dashboard does not send the token. Keep the server bound to localhost until a complete auth/session and CSRF design is implemented.
- No universal connector registry, action authorization layer, approval workflow, durable execution queue, or wallet signer is established by this baseline.

## Proposed execution architecture

1. **Identity and session boundary**
   - Authenticate users at the API edge; associate every request with a stable principal.
   - Use secure, HttpOnly, SameSite cookies for browser sessions, CSRF protection for cookie-authenticated mutations, and HTTPS behind a trusted reverse proxy.
   - Never treat an agent label, request body field, or model output as an identity or authorization grant.

2. **Connector registry**
   - Each integration declares a stable connector ID, available capabilities, input/output schemas, required scopes, risk class, timeout, and idempotency behavior.
   - Initial connector candidates: GitHub (repository/read operations first), generic HTTPS/API connector with host allowlisting, and Web3 chain reads.
   - Connector credentials are stored server-side in environment variables or a dedicated secret manager; redact them from logs and tool outputs.

3. **Policy and action gate**
   - Use an explicit server-side allowlist of action IDs and JSON-schema-validated arguments.
   - Enforce principal, connector scopes, per-action permissions, rate limits, and resource constraints before execution.
   - Model output is untrusted: it may propose an action, but cannot directly call arbitrary code, shell commands, URLs, or contract methods.
   - Default to dry-run for mutations. Require a user confirmation for consequential actions; require a stronger approval flow for financial, destructive, or externally visible operations.

4. **Prepare → approve → execute**
   - `prepare_action`: validate and produce a human-readable preview, including destination, parameters, estimated costs, and side effects.
   - `approve_action`: record an approval bound to the exact normalized action hash, principal, expiry, and policy version.
   - `execute_action`: revalidate approval and policy, then execute with an idempotency key.
   - Never accept private keys or seed phrases through prompts, browser fields, chat, or repository files.

5. **Web3 boundary**
   - Begin with read-only chain data (chain ID, contract code, balances, transaction/receipt reads).
   - Transaction construction may be supported as a preview artifact.
   - Actual signing must be performed by a user-controlled wallet or a separately provisioned signer with explicit policies, limits, and auditable approval. The model service must not receive private key material.
   - Validate chain ID, destination contract, calldata, token, amount, gas bounds, nonce, deadline, and simulation result before presenting a transaction for signature.
   - Arbitrage execution is not enabled by this blueprint; profitable execution cannot be guaranteed and requires independent testing/auditing.

6. **Audit and observability**
   - Record action ID, principal, connector, normalized argument hash, approval reference, start/end timestamps, status, and external result identifier.
   - Redact API keys, authorization headers, cookies, private keys, and sensitive payload fields.
   - Keep audit records append-only where practical; distinguish “prepared”, “approved”, “submitted”, and “confirmed” states.

7. **Execution runtime**
   - Use a bounded worker queue for long-running tasks rather than blocking a request handler.
   - Add connector-specific timeouts, retry policy only for safe/idempotent operations, cancellation, and per-principal concurrency quotas.
   - Return a job ID and expose authenticated status/result endpoints.

## Suggested implementation milestones

- **M1 — foundation:** connector/action interfaces, schema validation, dry-run mode, policy checks, audit events, unit tests.
- **M2 — read-only integrations:** GitHub repository metadata/files and read-only Web3 RPC methods; secret redaction tests.
- **M3 — approval workflow:** action previews, expiring approvals bound to action hashes, authenticated browser session and CSRF protections.
- **M4 — controlled mutations:** selected GitHub changes behind explicit approval; durable job queue and idempotency.
- **M5 — wallet handoff:** unsigned transaction preview plus wallet-based signature handoff; no custody of user keys.
- **M6 — production readiness:** threat model, dependency/security scans, integration tests on testnet/fork, operational monitoring, and independent review.

## Acceptance criteria

- No connector can be invoked unless it is registered and the requested action is allowlisted.
- Invalid or extra arguments are rejected before connector invocation.
- Secrets do not appear in API responses, logs, exception strings, or model prompts.
- Mutating actions require a valid approval bound to the exact action and an authenticated principal.
- Web3 operations reject a mismatched chain ID and cannot access signing material from the model runtime.
- Tests cover authorization failures, expired/replayed approvals, idempotency, timeout behavior, and audit redaction.
- Documentation clearly distinguishes simulated/prepared actions from actions submitted to and confirmed by external systems.
