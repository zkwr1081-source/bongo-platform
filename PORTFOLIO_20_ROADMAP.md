# NEXORA / BONGO — 20-Project Portfolio Roadmap

**Reviewed:** 2026-11-02  
**Operating strategy:** profit-first, sequential launches, one production candidate at a time.

This is a portfolio inventory, not a claim that 20 products are already built. It separates code that exists from draft pull requests and concept cards so that commercial progress is measurable.

## Portfolio inventory

| # | Project | Evidence today | Status | Primary monetization path | Critical acceptance gate |
|---:|---|---|---|---|---|
| 1 | BONGO Platform / NEXORA Core | Main repository contains the Python service, agent registry, model adapter, and gateway health monitoring. | Active platform code; no verified public deployment. | Shared platform enabling later products. | Stable authenticated APIs, tenant boundaries, observability, backups, and verified deployment. |
| 2 | NEXORA Command Center | Draft PR #23 adds the Arabic RTL dashboard and 12 business-unit cards. | Implemented on a review branch; integrations remain explicitly pending. | Internal control plane first; later multi-tenant operations subscription if validated. | Live API contracts, authorization, real metrics, responsive browser test, and production integration. |
| 3 | Digital Store | Dashboard concept card only. | Concept; no production commerce flow verified. | Transaction margin and seller subscriptions. | Product catalog, order state machine, digital fulfillment, refunds, tax, and lawful hosted checkout. |
| 4 | Customer Service AI | Dashboard concept card; BONGO has a model adapter but no production channel integration verified. | Concept / integration candidate. | Monthly subscription by seats or conversation volume. | Real model-provider connection, official messaging channel, knowledge base, tenant isolation, and usage metering. |
| 5 | SaaS Factory | Dashboard concept card only. | Concept. | Monthly or annual SaaS subscriptions. | Tenant provisioning, plans, entitlements, billing, quotas, and lifecycle controls. |
| 6 | Document AI | Dashboard concept card only. | Concept. | Per-document usage or processing bundles. | Secure upload, OCR/extraction pipeline, human review, retention controls, and export validation. |
| 7 | Risk Intelligence | Dashboard concept card only in the accessible GitHub portfolio. | Concept; no production risk data source verified. | Enterprise subscription or metered API. | Lawful data sources, explainable rules, calibrated scores, audit trail, and false-positive evaluation. |
| 8 | Market Intelligence | Dashboard concept card only. | Concept. | Paid reports and data subscriptions. | Licensed sources, provenance, scheduled collection, normalization, and freshness monitoring. |
| 9 | Freelance Hub | Dashboard concept card only. | Concept. | Transaction commission and promoted listings. | Identity, contracts, dispute workflow, verified payment provider, and seller protections. |
| 10 | Cloud Vault | Dashboard concept card only. | Concept. | Storage and collaboration subscriptions. | Encrypted object storage, access control, quotas, backups, deletion, and recovery tests. |
| 11 | Marketing Engine | Dashboard concept card only. | Concept. | Subscription or managed-campaign fees. | Official platform integrations, consent, approval workflow, attribution, and reporting. |
| 12 | API Marketplace | Dashboard concept card only. | Concept. | Usage fees and provider commission. | API gateway, secret-safe keys, rate limits, metering, settlement, and abuse controls. |
| 13 | Inventory | Dashboard concept card only. | Concept. | Subscription per store or branch. | Stock ledger, idempotent movements, point of sale, invoices, and reconciliation. |
| 14 | Automation Cloud | Dashboard concept card only. | Concept. | Subscription by workflows and executions. | Durable workflow engine, retries, idempotency, connector permissions, secret storage, and audit logs. |
| 15 | Secure Rewards Portal | Draft PR #12 adds an Arabic FastAPI portal and hosted-checkout boundary. | Draft implementation; checkout intentionally disabled. | Rewards / membership plans after payment-provider approval. | Server-created provider sessions, signed idempotent webhooks, refund handling, and legal payment eligibility. |
| 16 | NEXUS Master Core | Draft PR #13 adds orchestration, SQLite persistence, and a simulation-only ledger. | Draft implementation; no broker, wallet, or live financial integration. | Internal orchestration capability; standalone revenue not established. | Real approved data integrations, explicit authorization boundaries, auditability, and no simulated financial claims. |
| 17 | NEXORA Finance Observer | Draft PR #19 adds a local read-only dashboard and observer controls. | Draft implementation; not deployed on the device. | B2B monitoring subscription if customer demand is validated. | Read-only guarantees, tenant authorization, retention, backup/restore, and operational deployment. |
| 18 | GitHub Portfolio Newsletter Bot | Merged PR #17 adds the private Telegram newsletter bot source under `ops-telegram-bot/`. | Source code merged; no running bot or host verified. | Private team reporting subscription or managed reporting service. | Owner-supplied Telegram token in a secret manager, allowlisted user IDs, always-on host, delivery monitoring, and privacy review. |
| 19 | AURA-BOT | Separate public Python repository contains a Telegram menu bot; README states payments are disabled. | Basic bot code; no hosted AI or payment integration verified. | Telegram support/service subscription after real functionality is added. | BotFather token rotation if exposed, command tests, real service integration, rate limiting, and hosted deployment. |
| 20 | Hyper-Agent Android Control Center | Private Kotlin/Compose app includes Telegram API calls and a local keyword-rule chat engine. | App code exists; security and polling fixes are in draft PR #3; no LLM connection verified. | Mobile companion subscription only after genuine AI and account features exist. | Remove historical credential exposure, verify Android CI, persist settings securely, and integrate a real model provider. |

## Evidence-based launch sequence

The order below optimizes for a narrow first release and short feedback loops. It is a priority order, not a revenue forecast.

1. **GitHub Portfolio Newsletter Bot** — already merged source code; smallest remaining path is owner-controlled secret configuration, allowlist, host, and delivery verification.
2. **AURA-BOT** — existing Telegram menu foundation; finish command behavior and operational hardening before adding payment or AI claims.
3. **Digital Store** — strongest direct transaction model among the 12 business-unit concepts, but requires an actual order/fulfillment backend and an approved payment route.
4. **Customer Service AI** — reuse the BONGO model adapter only after provider connectivity, official channel integration, and per-tenant usage accounting are verified.
5. **Secure Rewards Portal** — complete provider-hosted checkout and signed webhook handling only after legal and provider eligibility checks.
6. **Finance Observer** — validate with read-only pilot users before considering any broader financial functionality.
7. **Document AI** — build one narrow document workflow and measure extraction accuracy before expanding.
8. **Risk Intelligence** — require lawful data provenance and measured precision/recall before offering risk decisions.
9. **Market Intelligence** — start with one licensed data source and a freshness SLA.
10. **Inventory** — start with a single-store stock ledger and reconciliation.
11. **Marketing Engine** — add only official, consent-based platform integrations.
12. **SaaS Factory** — use the first paid product to prove tenant, entitlement, and billing primitives.
13. **API Marketplace** — launch only after API metering, abuse controls, and provider settlement are reliable.
14. **Freelance Hub** — defer until identity, dispute, and payment operations are supportable.
15. **Cloud Vault** — defer until storage security, backup, deletion, and recovery are tested.
16. **Automation Cloud** — defer until durable workflows and secret-safe connectors are proven.
17. **NEXUS Master Core** — keep as internal orchestration until real integrations and measurable customer value justify productization.
18. **NEXORA Command Center** — keep as the internal control plane; only productize multi-tenant access after authorization and isolation are complete.
19. **Hyper-Agent Android** — treat as a companion app after the Telegram security PR and a real model integration are verified.
20. **Voice Agent integration** — evaluate the upstream Qwen Audio fork as an integration dependency, not as an independently owned product, and verify license obligations and differentiation before commercial use.

## Portfolio hygiene: repositories not counted as independent products

The accessible profile currently contains nine repositories. Three are upstream forks (Qwen Audio Agent, Etherscan Skills, and Expo) and should not be counted as original products without substantial differentiated work and license review. The private `app-mall` repository currently contains only repository metadata files; public `BONGO` is empty; private `NEXORA-Terminal` contains a README/license shell rather than a terminal implementation. These are backlog assets, not launch-ready projects.

## Non-negotiable release gates

Every product must pass all applicable gates before a public release:

- A working end-to-end customer flow verified against real services; no mock data presented as live.
- Tests for critical business logic, API contracts, authentication, authorization, and failure handling.
- Secret-manager configuration and least-privilege credentials; no credentials in source, logs, screenshots, or chat.
- Observability for errors, latency, usage, and service health without collecting unnecessary personal data.
- Backup/restore and data-retention/deletion behavior appropriate to the product.
- Clear terms, privacy, support, refunds, tax, and consumer-protection handling.
- Payment eligibility and lawful processor authorization verified for the operating jurisdiction before checkout is enabled.
- Revenue is reported only from independently reconciled provider receipts; code, subscriptions configured, or successful API responses are not revenue.

## Current portfolio truth

- The 12 cards in the command center are proposed business units and currently display **waiting for production integration**.
- Draft pull requests are not merged products.
- Source code is not a deployment.
- No verified production URL, payment processor, customer receipt, or profit distribution was found during this review.
- The portfolio should launch sequentially; do not activate several payment or customer-data products at once.
