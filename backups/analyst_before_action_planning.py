from typing import Any, Dict


class AnalystAgent:
    """
    NEXORA Analyst Agent.

    مسؤول عن تحليل الطلب واستخراج:
    - الهدف
    - طبيعة المهمة
    - مستوى التعقيد
    - الحاجة المحتملة إلى أدوات أو تنفيذ
    """

    name = "ANALYST"
    role = "تحليل الطلب والسياق"

    def run(self, context: Any) -> Dict[str, Any]:
        request = context.request.strip()

        return {
            "agent": self.name,
            "role": self.role,
            "task_id": context.task_id,
            "goal": request,
            "input_length": len(request),
            "complexity": self._complexity(request),
            "requires_tools": self._requires_tools(request),
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
            "build",
            "search",
            "analyze",
        )

        text = request.lower()

        return any(keyword.lower() in text for keyword in keywords)
