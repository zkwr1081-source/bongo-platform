# BONGO AI Software Factory (MVP)

BONGO AI Software Factory is a human-supervised engineering workspace. The first milestone is deliberately a **planning and review foundation**, not an autonomous production agent.

## MVP goals

1. Turn a product request into a structured, reviewable implementation plan.
2. Keep engineering tasks separated by role: product, architecture, implementation, QA, and security.
3. Require evidence for completion: changed files, test output, known limitations, and reviewer notes.
4. Keep all model access optional and provider-neutral until resource, licensing, privacy, and cost checks are complete.
5. Never grant an LLM unrestricted shell, repository administration, production, wallet, or financial permissions.

## Initial workflow

`REQUEST → TRIAGE → PLAN → HUMAN APPROVAL → FEATURE BRANCH → IMPLEMENT → TEST → SECURITY REVIEW → PULL REQUEST → HUMAN MERGE`

The MVP does not merge, deploy, purchase services, or execute financial actions.

## Suggested first commercial experiment

Validate one narrowly scoped B2B automation problem before building a broad platform. Interview potential buyers, identify a repetitive workflow with measurable time/cost savings, produce a small demo, and seek a paid pilot. Do not treat market hypotheses as revenue forecasts.

## Components

- `agents.yaml`: role definitions and allowed responsibilities.
- `policy.md`: mandatory permission and safety boundaries.
- `opportunity-scorecard.md`: evidence-based commercial opportunity evaluation.
- `model-strategy.md`: model selection and deployment criteria.

## Current limitations

This repository does not yet contain a running multi-agent orchestrator, model runtime, task queue, customer billing, or production UI. These are future milestones and must be implemented and tested separately.

## Development

Start with documentation review. Before introducing runtime dependencies, define API contracts, data retention, authentication, audit events, rate limits, and a test strategy. Keep all implementation on a feature branch and submit a pull request for review.
