"""Small, read-only registry of NEXORA external integrations.

This registry reports configuration only; it does not execute connector actions
or expose credential values.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectorSpec:
    connector_id: str
    label: str
    category: str
    required_env: tuple[str, ...]
    access_mode: str
    capabilities: tuple[str, ...]

    def status(self) -> dict[str, object]:
        missing = [key for key in self.required_env if not os.getenv(key, "").strip()]
        return {
            "id": self.connector_id,
            "label": self.label,
            "category": self.category,
            "configured": not missing,
            "status": "configured" if not missing else "needs_configuration",
            "access_mode": self.access_mode,
            "capabilities": list(self.capabilities),
            "missing_environment": missing,
        }


CONNECTORS: tuple[ConnectorSpec, ...] = (
    ConnectorSpec(
        connector_id="model-provider",
        label="OpenAI-compatible model provider",
        category="ai",
        required_env=("NEXORA_BASE_URL", "NEXORA_API_KEY", "NEXORA_MODEL"),
        access_mode="model-inference",
        capabilities=("chat-completions", "multi-agent-inference"),
    ),
    ConnectorSpec(
        connector_id="github-rest",
        label="GitHub REST API",
        category="developer-tools",
        required_env=(),
        access_mode="public-read-only",
        capabilities=("repository-metadata", "default-branch-commit", "workflow-status"),
    ),
)


def list_connectors() -> dict[str, object]:
    """Return connector configuration status without secret material."""
    items = [connector.status() for connector in CONNECTORS]
    return {"connectors": items, "count": len(items)}
