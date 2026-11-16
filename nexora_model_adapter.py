"""OpenAI-compatible adapter for local Qwen and remote model providers.

Local HTTP is allowed only for loopback hosts and does not require an API key.
Remote providers must use HTTPS and an API key. Credentials are environment-only.
"""
from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from nexora_agents import AgentSpec, run_batch


class ModelConfigurationError(RuntimeError):
    """Raised when model connection settings are incomplete or unsafe."""


class ModelRequestError(RuntimeError):
    """Raised when the provider rejects or cannot complete a request."""


def _settings() -> tuple[str, str, str]:
    base_url = os.getenv("NEXORA_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv("NEXORA_API_KEY", "").strip()
    model = os.getenv("NEXORA_MODEL", "").strip()
    missing = [name for name, value in (
        ("NEXORA_BASE_URL", base_url), ("NEXORA_MODEL", model)
    ) if not value]
    if missing:
        raise ModelConfigurationError("Missing environment variables: " + ", ".join(missing))

    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ModelConfigurationError("NEXORA_BASE_URL must be a valid HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ModelConfigurationError("NEXORA_BASE_URL must not contain credentials, query, or fragment")

    host = parsed.hostname.lower().rstrip(".")
    is_loopback = host in ("localhost", "127.0.0.1", "::1")
    if parsed.scheme == "http" and not is_loopback:
        raise ModelConfigurationError("Remote model endpoints must use HTTPS")
    if not is_loopback and not api_key:
        raise ModelConfigurationError("NEXORA_API_KEY is required for remote HTTPS providers")
    return base_url, api_key, model


def _request_completion(agent: AgentSpec, goal: str) -> str:
    base_url, api_key, model = _settings()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": (
                "أنت وكيل متخصص ضمن NEXORA. "
                f"القسم: {agent.department}. الاختصاص: {agent.specialty}. "
                "نفّذ المطلوب ضمن النطاق، وميّز الأدلة عن الاستنتاجات، "
                "ولا تدّع تنفيذ إجراء لم يحدث."
            )},
            {"role": "user", "content": goal},
        ],
        "temperature": 0.2,
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        timeout = float(os.getenv("NEXORA_MODEL_TIMEOUT", "300"))
        if not 1 <= timeout <= 600:
            raise ModelConfigurationError("NEXORA_MODEL_TIMEOUT must be between 1 and 600")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(1000).decode("utf-8", errors="replace")
        raise ModelRequestError(f"Provider HTTP {exc.code}: {detail}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ModelRequestError(f"Provider request failed: {type(exc).__name__}") from None

    try:
        result = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise ModelRequestError("Provider response missing choices[0].message.content") from None
    if not isinstance(result, str) or not result.strip():
        raise ModelRequestError("Provider returned an empty assistant message")
    return result.strip()


async def model_handler(agent: AgentSpec, goal: str) -> str:
    return await asyncio.to_thread(_request_completion, agent, goal)


async def main() -> None:
    results = await run_batch(
        goal="افحص جاهزية NEXORA واقترح خطوة تحقق عملية واحدة.",
        handler=model_handler,
        agent_ids=("NX-ORCHESTRATION-001", "NX-QUALITY-001"),
        concurrency=2,
        timeout_seconds=330,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
