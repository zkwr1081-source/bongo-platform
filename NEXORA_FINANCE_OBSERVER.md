# NEXORA Finance Observer

A safe first integration of the supplied finance/agent concept into BONGO.
This is a **read-only market telemetry prototype**, not an autonomous trading
or payment system.

## What it does

- Polls CoinGecko's public global market aggregate at a conservative interval.
- Stores observed market-cap change, total market cap, volume, timestamp and source in SQLite.
- Labels the observed 24-hour movement descriptively; it does not predict future prices.
- Provides a bounded worker setting for future analysis tasks.
- Can record a 5% / 95% split for **externally verified revenue** as bookkeeping only.

## Explicit non-features

- No exchange connection, order placement, wallet access, crypto transfer or payout.
- No fabricated profit, guaranteed return, prediction confidence, or claim of 100 live agents.
- No automatic GitHub repository creation or recursive repo spawning.
- No automatic Telegram messages. Add notification delivery only after explicit configuration
  and opt-in, with secrets held outside Git.

## Run

Python 3.10+; standard library only.

```bash
python nexora_finance_observer.py
```

Optional environment variables:

| Variable | Default | Constraint |
|---|---:|---|
| `NEXORA_FINANCE_DB` | `nexora_finance_observer.db` | Local SQLite path |
| `NEXORA_WORKERS` | `4` | 1–16 |
| `NEXORA_POLL_SECONDS` | `300` | At least 60 seconds |
| `LOG_LEVEL` | `INFO` | Standard Python logging level |

Stop with Ctrl+C. Market data availability and provider rate limits apply.

## Accounting helper

`split_verified_revenue(amount_usd)` returns an illustrative accounting split.
`FinanceStore.record_verified_revenue(amount_usd)` stores that split with status
`RECORDED_NOT_PAID`. It never initiates a transfer. Reconcile against invoices,
payment processor records, refunds, taxes and contractual obligations before
any real distribution.

## Security and operations

- Keep API tokens and credentials in local environment variables or a secret manager.
- Never commit `.env`, wallet secrets, bot tokens or private keys.
- Use a separate staging environment before adding integrations.
- Require human approval for trades, transfers, repository creation, deployments,
  public messages and other irreversible or externally visible actions.
