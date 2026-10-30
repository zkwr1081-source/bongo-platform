# Global Need Discovery & Innovation Engine

Status: proposed engineering specification
Owner: BONGO AI Software Factory
Execution posture: research-first, evidence-backed, human-supervised

## Mission

Continuously discover important, poorly served human and infrastructure needs; gather traceable evidence; map existing interventions; identify gaps; generate testable solution hypotheses; and turn the strongest hypotheses into scoped project briefs.

The engine must not claim to invent something unprecedented merely because a search did not find it. Novelty is always provisional and must include search coverage, competing work, and uncertainty.

## Research domains

1. Water security, sanitation, leakage detection, low-cost purification, drought resilience.
2. Food systems, crop disease, soil health, post-harvest loss, logistics, affordability.
3. Energy access, grid reliability, storage, efficiency, demand response.
4. Health access, diagnostics support, medicine availability, public-health logistics.
5. Education access, language inclusion, disability accessibility, skills verification.
6. Disaster early warning, resilient infrastructure, humanitarian logistics.
7. Cybersecurity, privacy, identity, fraud prevention, trustworthy information.
8. Climate adaptation, biodiversity, pollution, resource circularity.
9. Public-service access, financial inclusion, accessibility, local commerce.
10. AI accountability, evaluation, provenance, safety, low-resource deployment.

## Source registry (initial candidates)

Use official, documented sources first; preserve attribution, terms, license, publication date, geographic scope, and update cadence.

- UN Sustainable Development Goals indicators: https://unstats.un.org/sdgs/
- UN Scientific Advisory Board horizon scanning: https://www.un.org/scientific-advisory-board/
- UNDRR data and APIs: https://data.undrr.org/
- ACAPS humanitarian datasets and API: https://api.acaps.org/
- World Bank development topics and indicators: https://www.worldbank.org/en/topic
- WHO Global Health Observatory: https://www.who.int/data/gho
- FAOSTAT: https://www.fao.org/faostat/
- Copernicus Climate Data Store: https://cds.climate.copernicus.eu/
- NASA Earthdata: https://www.earthdata.nasa.gov/
- OpenAlex scholarly works: https://openalex.org/
- Crossref metadata: https://www.crossref.org/
- arXiv open research: https://arxiv.org/

Before ingestion, each connector must verify endpoint documentation, authentication needs, license/terms, rate limits, data minimization, and whether local caching is permitted. Do not crawl private, paywalled, or access-controlled material.

## Agent pipeline

1. **Scout** — monitors approved source registry and records candidate signals.
2. **Evidence Extractor** — extracts claims, dates, locations, populations, metrics, and source links.
3. **Need Mapper** — converts signals into a structured problem statement and affected-user map.
4. **Gap Analyst** — searches for existing products, public programs, research, and substitutes.
5. **Contradiction Analyst** — finds counter-evidence, failed interventions, and uncertainty.
6. **Inventor** — generates multiple solution hypotheses, including low-cost and low-connectivity options.
7. **Feasibility Engineer** — estimates technical maturity, dependencies, data needs, operating constraints, and prototype scope.
8. **Impact Analyst** — estimates reach and measurable benefit without presenting estimates as facts.
9. **Commercial Analyst** — identifies potential buyers/payers and tests whether public-good and commercial incentives align.
10. **Red Team** — checks misuse, privacy, bias, safety, environmental effects, and unintended consequences.
11. **Portfolio Curator** — deduplicates, ranks, versions, and maintains the idea backlog.
12. **Experiment Designer** — creates the smallest ethical validation experiment and measurable success criteria.

Agents are bounded workers, not independent authorities. Every claim must link to evidence. Retrieved pages and datasets are untrusted input, never instructions.

## Evidence record

Every research signal must store:
- stable record ID and collection timestamp (UTC)
- source name, canonical URL, publisher, license/terms, publication/update date
- exact excerpt or structured observation with context
- geography, population, domain, and measurement units where available
- claim type: observed fact, estimate, hypothesis, or opinion
- confidence rationale and known limitations
- content hash for change detection
- privacy classification and retention policy

Keep a local-first cache. Do not upload phone files, private project data, credentials, or personal data to research providers. Send only minimal public queries. Respect robots, API terms, rate limits, attribution, and deletion requests.

## Idea scoring

Score each dimension from 0–5 and preserve the underlying evidence:
- severity and urgency of the need
- number of people affected and equity implications
- evidence quality and recency
- gap versus existing solutions
- plausible novelty (never certainty)
- technical feasibility and prototype cost
- time to measurable outcome
- maintainability and deployment constraints
- legal, safety, privacy, and environmental risk (risk is a penalty)
- sustainability of funding or business model

A score ranks investigation priority; it does not prove impact, novelty, demand, or profitability. Missing evidence must lower confidence, not be silently imputed.

## Required outputs

- Daily signal digest with citations and source dates.
- Deduplicated global needs map by domain and geography.
- Ranked opportunity backlog with evidence and uncertainty.
- One-page project concept briefs with users, pain, alternatives, proposed intervention, impact metric, risks, cost, and validation plan.
- Technical architecture and prototype milestones for approved ideas.
- Rejected-idea register with reasons, to prevent rediscovery.
- Monthly review of source quality, missed domains, bias, and stale assumptions.

## Novelty and anti-hallucination checks

Before labeling an idea novel:
1. Search scholarly metadata, patents where legally accessible, open-source repositories, commercial products, public procurement, and NGO/government programs.
2. Compare functional claims and target users, not just names.
3. Identify the closest prior art and explain the difference.
4. Label novelty as low / medium / high confidence, with explicit search coverage.
5. Never use phrases such as "never before imagined" or "first in the world" without independent expert and legal review.

## Safety and approval boundaries

- Research and local analysis may run automatically within configured budgets and source allowlists.
- No autonomous contact with affected people, scraping of personal profiles, medical diagnosis, high-stakes eligibility decisions, surveillance, or political persuasion.
- No purchases, paid API activation, cloud uploads of private data, production deployment, or financial transactions without owner approval.
- High-impact health, water, energy, and disaster interventions require qualified domain experts and field validation before deployment.
- Generated code runs only in an isolated workspace with allowlisted tools, resource limits, and auditable logs.

## MVP implementation sequence

1. Implement source registry, evidence schema, local SQLite store, and deduplication.
2. Add two read-only connectors first: UNDRR and ACAPS; add public metadata only.
3. Implement need extraction and evidence-linked scoring with deterministic tests.
4. Add contradiction search and prior-art review before ideation.
5. Generate structured project briefs and a local HTML/Markdown report.
6. Add scheduled runs only after rate limits, resource ceilings, and retention are tested.
7. Add model providers behind an adapter; keep API keys in environment variables and never send private phone data.
8. Evaluate against a human-labelled benchmark for relevance, citation accuracy, duplication, bias, and false novelty claims.

## Acceptance criteria

- Every nontrivial factual claim in a brief has a source and date.
- The same source item is not repeatedly emitted as a new idea.
- Failed or unavailable sources are reported, not silently ignored.
- All scores expose their evidence and uncertainty.
- Tests cover malformed feeds, duplicate records, stale evidence, missing licenses, prompt injection, unsafe proposals, and privacy boundaries.
- The engine can run in offline review mode from its local cache.
- No idea is marked "validated" without a documented experiment and result.
