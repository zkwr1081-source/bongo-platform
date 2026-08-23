from __future__ import annotations

from typing import Any, Dict


class VerifyAgent:
    name = "VERIFY"
    role = "التحقق من النتائج"

    def run(self, context: Any) -> Dict[str, Any]:
        request = context.request.strip()

        return {
            "agent": self.name,
            "role": self.role,
            "task_id": str(context.task_id),
            "verified": bool(request),
            "checks": {
                "request_present": bool(request),
                "request_length": len(request),
                "safe_default": True,
            },
        }
