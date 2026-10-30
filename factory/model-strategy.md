# Model Strategy

## Operating principle

Prefer open-weight models with clear licenses and verifiable provenance, but do not equate open weights with open-source software or guaranteed safety. Review each model card, license, training/data statements, supported context length, tool-use behavior, and known limitations before adoption.

## Codespaces constraint

A stated 16 GB RAM allocation does not establish available memory, CPU architecture, GPU availability, or disk capacity. Codespaces memory is independent of phone/Termux memory. Do not download multi-gigabyte model weights until the active Codespace resources and storage have been measured.

## Staged approach

1. **Phase A — no model runtime:** use this repository's deterministic planning templates and existing GitHub review workflow.
2. **Phase B — small local inference:** only after measuring the Codespace; benchmark a quantized coding model with a short representative task. Treat CPU-only inference as potentially slow.
3. **Phase C — optional remote inference:** consider a separately managed GPU host only after privacy, provider terms, region, cost ceiling, authentication, and data-retention controls are approved.
4. **Phase D — evaluation:** compare candidate models on the same repository tasks using correctness, tests passed, patch quality, security findings, latency, token cost, and human review time.

## Candidate families

Evaluate Qwen coder/instruct releases, DeepSeek coder releases, and StarCoder releases by their exact current model card and license. Model names and tags change; do not pin a recommendation based on a family name alone.

## Mandatory controls

- No secrets in prompts or model context.
- No unrestricted shell or network access for a model.
- Tool calls pass through a policy-enforcing orchestrator.
- Human approval for external side effects.
- Log model identifier, prompt template version, tool actions, and evaluation outcome without logging sensitive content.
