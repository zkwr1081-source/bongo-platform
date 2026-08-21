# NEXORA Infrastructure

NEXORA is organized as an extensible infrastructure layer.

## Layers

Core → Agents → Plugins → Memory → Security → Governance
→ Observability → Recovery → API → Runtime

The architecture intentionally separates responsibilities so new
capabilities can be added without rewriting the kernel.

## Current endpoints

- `/`
- `/health`
- `/metrics`
- `/agents`
- `/plugins`
- `/memory`
