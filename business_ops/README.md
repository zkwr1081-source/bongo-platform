# NEXORA Business Operations MVP

A first verifiable module for managing a digital-project portfolio and tracking collected revenue and expenses. It is additive: it does not modify BONGO/NEXORA core modules.

## Features

- Project portfolio with stages: idea, validation, build, launch, operating, paused, archived.
- Cash ledger for income and expenses, with pending/collected/void statuses.
- Dashboard totals grouped by currency; no cross-currency addition.
- Money stored as positive signed 64-bit integer minor units (e.g. 1250 = $12.50 when currency is USD); values outside SQLite's integer range are rejected.
- API key authentication on all business-data routes, with a 32-UTF-8-byte minimum configured secret.
- Health endpoint intentionally exposes only service status.

## Run in Termux / Python

From the repository root:

```bash
python -m pip install -r requirements.txt
export NEXORA_BUSINESS_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export NEXORA_BUSINESS_DB="$PWD/nexora_business.db"
uvicorn business_ops.api:app --host 127.0.0.1 --port 8094
```

Keep the API bound to localhost unless a protected reverse proxy and network policy are configured. Never commit the API key or database.

## API

- `GET /health` — unauthenticated liveness only.
- `GET /api/projects` — list projects.
- `POST /api/projects` — create a project; body: `{"name":"AI Support SaaS","category":"saas","stage":"idea"}`
- `PATCH /api/projects/{project_id}/stage` — advance or pause a project; body: `{"stage":"validation"}`
- `POST /api/transactions` — record income or expense; body: `{"project_id":1,"kind":"income","amount_minor":12500,"currency":"USD","status":"collected","source":"pilot"}`
- `GET /api/dashboard` — cash metrics, grouped by currency.

For all `/api/*` routes send `X-API-Key: <NEXORA_BUSINESS_API_KEY>`.

## Financial semantics

Only transactions marked `collected` count in collected cash metrics. Pending records are shown separately; void entries are excluded. The dashboard reports gross collected income, collected expenses, and net collected cash per currency. These are bookkeeping summaries, not audited financial statements or profit forecasts.

## Verification

Run tests from repository root:

```bash
pytest -q tests/unit/test_business_ops.py
```

MVP limitations: no user accounts/roles, billing provider, invoice issuance, tax calculation, multi-user tenancy, project editing/deletion, or automated money movement. These should be separately scoped and security-reviewed before production.
