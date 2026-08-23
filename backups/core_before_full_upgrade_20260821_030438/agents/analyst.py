from typing import Any, Dict


class AnalystAgent:
    """
    NEXORA Analyst Agent.

    يحلل الطلب ويحدد:
    - الهدف
    - مستوى التعقيد
    - الحاجة إلى أدوات
    - نوع الإجراء المطلوب
    """

    name = "ANALYST"
    role = "تحليل الطلب والسياق وتحديد الإجراء"

    def run(self, context: Any) -> Dict[str, Any]:
        request = context.request.strip()

        requires_tools = self._requires_tools(request)

        return {
            "agent": self.name,
            "role": self.role,
            "task_id": context.task_id,
            "goal": request,
            "input_length": len(request),
            "complexity": self._complexity(request),
            "requires_tools": requires_tools,
            "action_type": (
                "shell"
                if requires_tools
                else "none"
            ),
        }

    @staticmethod
    def _complexity(request: str) -> str:
        length = len(request)

        if length < 40:
            return "low"

        if length < 150:
            return "medium"

        return "high"

    @staticmethod
    def _requires_tools(request: str) -> bool:
        keywords = (
            "ابحث",
            "حلل",
            "بيانات",
            "ملف",
            "ويب",
            "نفذ",
            "برمج",
            "أنشئ",
            "شغّل",
            "شغل",
            "افحص",
            "build",
            "search",
            "analyze",
            "execute",
            "run",
        )

        text = request.lower()

        return any(
            keyword.lower() in text
            for keyword in keywords
        )
