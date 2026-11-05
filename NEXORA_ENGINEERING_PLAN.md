# NEXORA Engineering Plan

This plan improves the existing BONGO/NEXORA repository incrementally. It does not replace BONGO's product purpose or rewrite its architecture.

## Verified implementation boundaries

- The current registry contains 1,000 **logical agent profiles** across 20 departments.
- The async runner executes only the selected profiles for which a handler is supplied. Its concurrency limit is bounded; it does not keep 1,000 independent models running.
- The current model adapter supports one OpenAI-compatible Chat Completions endpoint configured through environment variables.
- The lightweight `server.py` exposes a dashboard, health response, and registry/configuration status. A configured key is not proof of a successful provider connection.
- Firebase and Railway are not required by this plan. Local and cloud deployment targets remain replaceable.

## Delivery sequence

### P0 — Reproducible baseline
1. Compile the Python modules.
2. Run the existing NEXORA unit tests.
3. Add CI so every pull request repeats those checks.
4. Keep secrets out of source control; use deployment secret stores or local ignored `.env` files.

### P1 — Runtime correctness
1. Select one canonical production entrypoint only after comparing the existing `bongo.web.app` and `nexora.api.server` applications.
2. Add endpoint and startup tests for the selected entrypoint.
3. Make health/readiness semantics explicit: liveness must not imply model connectivity.
4. Add structured task IDs, bounded retries, cancellation, and safe error redaction.

### P2 — Real multi-agent orchestration
1. Add a task contract with input, owner, status, deadline, and result schema.
2. Route work to specialists by department and capability rather than broadcasting every task.
3. Persist task state and agent outputs behind a storage interface.
4. Add deduplication, budgets, rate limits, and per-provider concurrency controls.
5. Begin with 2–5 real model-backed workers; scale only after load tests.

### P3 — Hybrid providers and deployment
1. Introduce a provider interface and capability-based routing.
2. Keep provider credentials in environment/secret storage, never in Git.
3. Add local-provider support behind the same interface.
4. Keep the phone as a control/monitoring client; use a cloud runtime for sustained concurrent workloads.

### P4 — Product quality
1. Replace dashboard demo metrics with live API data.
2. Implement complete Arabic/English localization and accessible navigation.
3. Add integration, security, and performance tests.
4. Add deployment documentation and rollback procedures.

## Release gates

A change is not considered complete until:
- CI passes;
- the affected endpoint or workflow has a reproducible test;
- secrets and personal data are not exposed in logs;
- failure and timeout behavior is documented;
- the change preserves existing BONGO behavior unless a migration is explicitly approved.

## Configuration

Copy `.env.example` to `.env` locally and fill in the provider values. Do not commit `.env`. Start with two workers and verify provider quotas before increasing concurrency.
