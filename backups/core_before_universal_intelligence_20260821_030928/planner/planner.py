from typing import Any, Dict

class PlannerAgent:
    name = "PLANNER"
    role = "تحويل التحليل إلى خطة تنفيذ"

    def run(self, context: Any) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "role": self.role,
            "task_id": context.task_id,
            "steps": [
                "understand",
                "plan",
                "route",
                "execute",
                "verify",
            ],
        }
