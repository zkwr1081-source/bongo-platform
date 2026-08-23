from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import json
import re


@dataclass
class IntelligenceSignal:
    domain: str
    confidence: float
    reason: str


class UniversalIntelligence:
    """
    NEXORA Universal Intelligence Layer.

    لا يدّعي امتلاك "ذكاء الكون".
    يجمع طبقات تحليل متعددة داخل NEXORA:
    - فهم الطلب
    - تصنيف المجال
    - تقدير التعقيد
    - تحديد الأدوات
    - التخطيط
    - التحقق
    - استخراج الإشارات
    """

    name = "UNIVERSAL_INTELLIGENCE"
    role = "تنسيق طبقات الذكاء والتحليل والتخطيط والتحقق"

    DOMAINS = {
        "software": (
            "code", "python", "javascript", "api", "server",
            "database", "برمج", "كود", "مشروع", "خادم", "قاعدة"
        ),
        "research": (
            "ابحث", "بحث", "حلل", "دراسة", "research",
            "analyze", "investigate"
        ),
        "automation": (
            "أتمتة", "نفذ", "شغل", "execute", "run", "automation"
        ),
        "data": (
            "بيانات", "data", "csv", "json", "sqlite", "تحليل بيانات"
        ),
        "planning": (
            "خطة", "خطط", "plan", "roadmap", "architecture", "تصميم"
        ),
    }

    def run(self, context: Any) -> Dict[str, Any]:
        request = context.request.strip()

        domains = self.detect_domains(request)
        complexity = self.complexity(request)
        tools = self.required_tools(request)
        risks = self.detect_risks(request)
        plan = self.build_plan(
            request,
            domains,
            complexity,
            tools,
            risks,
        )

        return {
            "agent": self.name,
            "role": self.role,
            "task_id": str(context.task_id),
            "request": request,
            "domains": domains,
            "complexity": complexity,
            "required_tools": tools,
            "risks": risks,
            "plan": plan,
            "signals": [
                asdict(x)
                for x in self.signals(request, domains)
            ],
        }

    def detect_domains(self, text: str) -> List[str]:
        t = text.lower()
        found = []

        for domain, keywords in self.DOMAINS.items():
            if any(k.lower() in t for k in keywords):
                found.append(domain)

        return found or ["general"]

    def complexity(self, text: str) -> str:
        score = len(text)

        if score < 60:
            return "low"

        if score < 220:
            return "medium"

        return "high"

    def required_tools(self, text: str) -> List[str]:
        t = text.lower()
        tools = []

        if any(x in t for x in ("ابحث", "بحث", "research", "search")):
            tools.append("web")

        if any(x in t for x in ("ملف", "files", "مشروع", "code", "كود")):
            tools.append("filesystem")

        if any(x in t for x in ("بيانات", "sqlite", "database", "قاعدة")):
            tools.append("database")

        if any(x in t for x in ("نفذ", "شغل", "execute", "run")):
            tools.append("action_engine")

        return sorted(set(tools))

    def detect_risks(self, text: str) -> List[str]:
        t = text.lower()
        risks = []

        if any(x in t for x in ("delete", "rm ", "احذف", "حذف")):
            risks.append("destructive_operation")

        if any(x in t for x in ("password", "token", "secret", "مفتاح")):
            risks.append("secret_material")

        if any(x in t for x in ("shell", "terminal", "bash", "cmd")):
            risks.append("command_execution")

        return risks

    def build_plan(
        self,
        request: str,
        domains: List[str],
        complexity: str,
        tools: List[str],
        risks: List[str],
    ) -> List[str]:

        steps = [
            "understand_request",
            "classify_domains",
            "collect_context",
        ]

        if tools:
            steps.append("prepare_tools")

        steps += [
            "generate_solution",
            "verify_solution",
            "return_result",
        ]

        if risks:
            steps.insert(-1, "apply_safety_checks")

        return steps

    def signals(
        self,
        request: str,
        domains: List[str],
    ) -> List[IntelligenceSignal]:

        confidence = min(
            0.99,
            0.55 + min(len(request), 300) / 1000
        )

        return [
            IntelligenceSignal(
                domain=d,
                confidence=round(confidence, 3),
                reason="keyword_and_context_classification",
            )
            for d in domains
        ]
