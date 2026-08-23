from __future__ import annotations

from typing import Any, Dict, List


class Orchestrator:
    name = "ORCHESTRATOR"
    role = "تنسيق الوكلاء وتحديد مسار المهمة"

    def run(self, context: Any) -> Dict[str, Any]:
        request = context.request.strip()

        return {
            "agent": self.name,
            "role": self.role,
            "task_id": str(context.task_id),
            "route": self.route(request),
            "stages": [
                "ANALYST",
                "FUTURE_INTELLIGENCE",
                "ORCHESTRATOR",
                "EXECUTION",
                "VERIFY",
            ],
        }

    def route(self, request: str) -> List[str]:
        t = request.lower()

        if any(x in t for x in ("نفذ", "execute", "run", "شغل")):
            return [
                "ANALYST",
                "FUTURE_INTELLIGENCE",
                "ORCHESTRATOR",
                "ACTION_ENGINE",
                "VERIFY",
            ]

        if any(x in t for x in ("ابحث", "حلل", "search", "research")):
            return [
                "ANALYST",
                "FUTURE_INTELLIGENCE",
                "ORCHESTRATOR",
                "RESEARCH",
                "VERIFY",
            ]

        return [
            "ANALYST",
            "FUTURE_INTELLIGENCE",
            "ORCHESTRATOR",
            "VERIFY",
        ]
