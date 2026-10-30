"""NEXORA 1000-agent registry and bounded async execution runtime.

The registry defines 1,000 logical specialists. It does not spawn 1,000 OS
processes or pretend to provide model intelligence without a configured
handler. Plug an LLM/tool handler into run_batch to execute real work.
"""
from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from typing import Any, Awaitable, Callable, Iterable

DEPARTMENTS: tuple[tuple[str, str], ...] = (
    ("orchestration", "تنسيق المهام وتوزيعها"),
    ("software_architecture", "هندسة البرمجيات والمعمارية"),
    ("backend", "تطوير الخوادم وواجهات API"),
    ("frontend", "واجهات المستخدم وتجربة الاستخدام"),
    ("mobile", "تطبيقات Android وiOS"),
    ("database", "قواعد البيانات وإدارة البيانات"),
    ("quality", "الاختبارات وضمان الجودة"),
    ("security", "الأمن والتحليل الدفاعي"),
    ("devops", "النشر والبنية التحتية"),
    ("ai_research", "النماذج وتكامل الذكاء الاصطناعي"),
    ("data_science", "تحليل البيانات"),
    ("automation", "الأتمتة وسير العمل"),
    ("product", "تحليل المنتج واحتياجات المستخدم"),
    ("design", "التصميم وإمكانية الوصول"),
    ("documentation", "التوثيق والمعرفة"),
    ("business", "تحليل الأعمال ونماذج الإيرادات"),
    ("integration", "التكاملات والخدمات الخارجية"),
    ("performance", "الأداء والاعتمادية"),
    ("support", "الدعم وتحليل الأعطال"),
    ("research", "البحث والتحقق من المصادر"),
)

@dataclass(frozen=True, slots=True)
class AgentSpec:
    agent_id: str
    department: str
    specialty: str
    index: int

def build_registry() -> tuple[AgentSpec, ...]:
    """Create exactly 1,000 stable, uniquely named logical agents."""
    agents = tuple(
        AgentSpec(
            agent_id=f"NX-{dept.upper()}-{n:03d}",
            department=dept,
            specialty=f"{description} — اختصاص فرعي {n:02d}",
            index=n,
        )
        for dept, description in DEPARTMENTS
        for n in range(1, 51)
    )
    if len(agents) != 1000 or len({a.agent_id for a in agents}) != 1000:
        raise RuntimeError("Agent registry invariant failed")
    return agents

REGISTRY = build_registry()
AgentHandler = Callable[[AgentSpec, str], Awaitable[Any]]

async def run_batch(
    goal: str,
    handler: AgentHandler,
    *,
    agent_ids: Iterable[str] | None = None,
    concurrency: int = 10,
    timeout_seconds: float = 90.0,
) -> list[dict[str, Any]]:
    """Run selected agents through a real async handler with bounded concurrency."""
    if not goal or not goal.strip():
        raise ValueError("goal must not be empty")
    if concurrency < 1 or concurrency > 100:
        raise ValueError("concurrency must be between 1 and 100")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    selected_ids = set(agent_ids) if agent_ids is not None else None
    selected = [a for a in REGISTRY if selected_ids is None or a.agent_id in selected_ids]
    if selected_ids is not None:
        unknown = selected_ids - {a.agent_id for a in selected}
        if unknown:
            raise ValueError(f"Unknown agent IDs: {', '.join(sorted(unknown))}")

    semaphore = asyncio.Semaphore(concurrency)

    async def invoke(agent: AgentSpec) -> dict[str, Any]:
        async with semaphore:
            try:
                result = await asyncio.wait_for(
                    handler(agent, goal), timeout=timeout_seconds
                )
                return {"agent_id": agent.agent_id, "status": "ok", "result": result}
            except asyncio.TimeoutError:
                return {"agent_id": agent.agent_id, "status": "timeout"}
            except Exception as exc:  # isolate failures so other agents can finish
                return {
                    "agent_id": agent.agent_id,
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                }

    return await asyncio.gather(*(invoke(agent) for agent in selected))

def registry_summary() -> dict[str, Any]:
    return {
        "name": "NEXORA",
        "logical_agents": len(REGISTRY),
        "departments": len(DEPARTMENTS),
        "agents_per_department": 50,
        "execution_mode": "bounded_async",
        "default_concurrency": 10,
        "model_connected": False,
        "note": "Connect a trusted model/tool handler before claiming AI task execution.",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(registry_summary(), ensure_ascii=False, indent=2))
