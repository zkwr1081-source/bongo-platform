"""OpenAI-compatible model adapter for NEXORA's logical agent runtime.

Configuration (environment only; never commit credentials):
  NEXORA_BASE_URL  e.g. https://api.openai.com/v1
  NEXORA_API_KEY   provider API key
  NEXORA_MODEL     provider model identifier

The adapter uses only the Python standard library and sends one request per
selected agent. Start with a small batch and respect provider rate limits.
"""
from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from typing import Any

from nexora_agents import AgentSpec, run_batch


class ModelConfigurationError(RuntimeError):
    """Raised when model connection settings are incomplete."""


class ModelRequestError(RuntimeError):
    """Raised when the provider rejects or cannot complete a request."""


def _settings() -> tuple[str, str, str]:
    base_url = os.getenv("NEXORA_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv("NEXORA_API_KEY", "").strip()
    model = os.getenv("NEXORA_MODEL", "").strip()
    missing = [name for name, value in (
        ("NEXORA_BASE_URL", base_url),
        ("NEXORA_API_KEY", api_key),
        ("NEXORA_MODEL", model),
    ) if not value]
    if missing:
        raise ModelConfigurationError("Missing environment variables: " + ", ".join(missing))
    if not base_url.startswith(("https://", "http://")):
        raise ModelConfigurationError("NEXORA_BASE_URL must start with http:// or https://")
    return base_url, api_key, model


def _request_completion(agent: AgentSpec, goal: str) -> str:
    base_url, api_key, model = _settings()
    url = base_url + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a specialist worker in the NEXORA multi-agent system. "
                    f"Your department is {agent.department}; specialty: {agent.specialty}. "
                    "Work only on the assigned goal. Be concrete, state assumptions, "
                    "and do not claim actions you did not perform."
                ),
            },
            {"role": "user", "content": goal},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Do not include request headers or credentials in error messages.
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise ModelRequestError(f"Provider HTTP {exc.code}: {detail}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ModelRequestError(f"Provider request failed: {type(exc).__name__}") from None

    try:
        result = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ModelRequestError("Provider response did not contain choices[0].message.content") from None
    if not isinstance(result, str) or not result.strip():
        raise ModelRequestError("Provider returned an empty assistant message")
    return result.strip()


async def model_handler(agent: AgentSpec, goal: str) -> str:
    """Async handler compatible with nexora_agents.run_batch."""
    return await asyncio.to_thread(_request_completion, agent, goal)


async def main() -> None:
    # Safe smoke-test default: only 2 agents, concurrency 2.
    results = await run_batch(
        goal="اقترح فحصاً عملياً قصيراً لجاهزية منصة NEXORA للنشر.",
        handler=model_handler,
        agent_ids=("NX-ORCHESTRATION-001", "NX-QUALITY-001"),
        concurrency=2,
        timeout_seconds=75,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
