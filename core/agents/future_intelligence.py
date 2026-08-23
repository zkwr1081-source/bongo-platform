from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
import hashlib
import json
import re


class FutureIntelligence:
    name = "FUTURE_INTELLIGENCE"
    role = "طبقة التفكير الاستراتيجي والتخطيط والتنبؤ والتحقق"

    def run(self, context: Any) -> Dict[str, Any]:
        request = context.request.strip()

        return {
            "agent": self.name,
            "role": self.role,
            "task_id": str(context.task_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intent": self.intent(request),
            "domains": self.domains(request),
            "complexity": self.complexity(request),
            "priority": self.priority(request),
            "tools": self.tools(request),
            "plan": self.plan(request),
            "verification": self.verification(request),
            "fingerprint": hashlib.sha256(
                request.encode("utf-8")
            ).hexdigest()[:16],
        }

    def intent(self, text: str) -> str:
        t = text.lower()

        if any(x in t for x in ("ابحث", "search", "research", "حلل", "analyze")):
            return "research"

        if any(x in t for x in ("نفذ", "execute", "run", "شغل")):
            return "execution"

        if any(x in t for x in ("خطة", "plan", "roadmap")):
            return "planning"

        if any(x in t for x in ("أنشئ", "ابن", "build", "create", "برمج")):
            return "construction"

        return "general"

    def domains(self, text: str) -> List[str]:
        t = text.lower()
        mapping = {
            "software": (
                "python", "code", "api", "server",
                "برمج", "كود", "مشروع"
            ),
            "data": (
                "data", "بيانات", "sqlite", "database",
                "قاعدة"
            ),
            "web": (
                "web", "ويب", "موقع", "واجهة", "browser"
            ),
            "automation": (
                "automation", "أتمتة", "نفذ", "execute"
            ),
            "ai": (
                "ai", "ذكاء", "نموذج", "model", "agent"
            ),
        }

        result = [
            name for name, words in mapping.items()
            if any(word in t for word in words)
        ]

        return result or ["general"]

    def complexity(self, text: str) -> str:
        score = len(text)

        if score < 60:
            return "low"

        if score < 200:
            return "medium"

        return "high"

    def priority(self, text: str) -> str:
        t = text.lower()

        if any(x in t for x in ("عاجل", "urgent", "critical", "ضروري")):
            return "critical"

        if any(x in t for x in ("مهم", "important", "priority")):
            return "high"

        return "normal"

    def tools(self, text: str) -> List[str]:
        t = text.lower()
        result = []

        if any(x in t for x in ("ابحث", "search", "research", "ويب")):
            result.append("web")

        if any(x in t for x in ("ملف", "files", "code", "كود", "مشروع")):
            result.append("filesystem")

        if any(x in t for x in ("database", "sqlite", "بيانات", "قاعدة")):
            result.append("database")

        if any(x in t for x in ("نفذ", "execute", "run", "شغل")):
            result.append("action_engine")

        return sorted(set(result))

    def plan(self, text: str) -> List[str]:
        return [
            "understand",
            "classify",
            "collect_context",
            "reason",
            "plan",
            "execute_allowed_actions",
            "verify",
            "learn",
            "finalize",
        ]

    def verification(self, text: str) -> Dict[str, Any]:
        return {
            "required": True,
            "checks": [
                "input_validation",
                "execution_status",
                "result_consistency",
                "error_detection",
            ],
        }
