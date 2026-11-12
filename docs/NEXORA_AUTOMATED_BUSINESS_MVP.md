# NEXORA Automated Business — MVP scope

## Objective

Create a verifiable command-center module for a sequential portfolio of digital ventures, tracking project stage and actual cash collection while preserving existing BONGO/NEXORA architecture.

## Data domains

- **Projects:** name, description, category, stage, creation timestamp.
- **Transactions:** linked project, income/expense type, integer minor-unit amount, ISO currency code, status, source, date, timestamp.
- **Dashboard:** active/total project count; collected income, expenses, and net cash grouped by currency; pending items separated.

## Operational sequence

1. Record and classify the project.
2. Validate customer pain and willingness-to-pay before advancing into build.
3. Track delivery stage.
4. Record income only when cash is actually collected; pending receivables remain separate.
5. Record project expenses and review net cash by currency.
6. Keep portfolio launch sequential; prioritize evidence of buyer demand, not speculative revenue projections.

## Security and non-goals

- API-key protection for business-data endpoints; localhost binding recommended.
- No credentials stored in database or source code.
- No auto-deployment, purchasing, wallet access, transfer, trade execution, or payment initiation.
- No change to default branch and no core-system replacement.

## Acceptance criteria

- Project creation/listing persists in SQLite.
- Ledger validates kind, currency, positive integer amount, date, and project foreign key.
- Dashboard separates currencies and excludes pending/void items from collected cash.
- Unit tests cover persistence, arithmetic, currency grouping, and invalid inputs.
- API routes use authentication dependency and expose a minimal unauthenticated health check.
