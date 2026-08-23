from typing import Any, Dict, List

class TaskRouter:
    def route(self, analysis: Dict[str, Any], agents: List[str]) -> List[str]:
        if analysis.get("requires_tools"):
            return agents
        return [a for a in agents if a in ("ANALYST", "VERIFY")]
