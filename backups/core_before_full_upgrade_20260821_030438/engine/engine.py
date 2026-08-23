from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class TaskContext:
    task_id: str
    request: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    task_id: str
    status: str
    phase: str
    result: Any = None
    agents: List[str] = field(default_factory=list)
    verification: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)


class NexoraEngine:
    """
    NEXORA Core Engine.

    Pipeline:
        receive -> analyze -> plan -> route -> execute -> verify -> finalize

    The engine does not assume that an agent has executed work.
    Agents must be explicitly registered and invoked.
    """

    PHASES = (
        "received",
        "analyzing",
        "planning",
        "routing",
        "executing",
        "verifying",
        "completed",
    )

    def __init__(self):
        self.agents: Dict[str, Any] = {}

    def register_agent(self, name: str, agent: Any) -> None:
        name = name.strip().upper()

        if not name:
            raise ValueError("agent name is required")

        self.agents[name] = agent

    def available_agents(self) -> List[str]:
        return sorted(self.agents.keys())

    def create_context(
        self,
        task_id: str,
        request: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TaskContext:

        request = request.strip()

        if not request:
            raise ValueError("request is required")

        return TaskContext(
            task_id=task_id,
            request=request,
            metadata=metadata or {},
        )

    def analyze(self, context: TaskContext) -> Dict[str, Any]:
        return {
            "goal": context.request,
            "input_length": len(context.request),
            "requires_execution": True,
        }

    def plan(
        self,
        context: TaskContext,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {
            "steps": [
                "analyze_request",
                "select_agents",
                "execute",
                "verify",
            ],
            "analysis": analysis,
        }

    def route(
        self,
        context: TaskContext,
        plan: Dict[str, Any],
    ) -> List[str]:

        if not self.agents:
            return []

        # Initial routing policy.
        # Later this becomes model/tool based routing.
        preferred = [
            "ANALYST",
            "PLANNER",
            "BUILDER",
            "VERIFY",
        ]

        selected = [
            name for name in preferred
            if name in self.agents
        ]

        return selected or list(self.agents.keys())[:1]

    def execute(
        self,
        context: TaskContext,
        agent_names: List[str],
    ) -> Dict[str, Any]:

        outputs = []

        for name in agent_names:
            agent = self.agents[name]

            try:
                if hasattr(agent, "run"):
                    output = agent.run(context)
                elif callable(agent):
                    output = agent(context)
                else:
                    raise TypeError(
                        f"Agent {name} has no runnable interface"
                    )

                outputs.append({
                    "agent": name,
                    "status": "completed",
                    "output": output,
                })

            except Exception as exc:
                outputs.append({
                    "agent": name,
                    "status": "error",
                    "error": str(exc),
                })

        return {
            "outputs": outputs
        }

    def verify(
        self,
        context: TaskContext,
        execution: Dict[str, Any],
    ) -> Dict[str, Any]:

        outputs = execution.get("outputs", [])

        errors = [
            item for item in outputs
            if item.get("status") != "completed"
        ]

        if not outputs:
            return {
                "verified": False,
                "completed_agents": 0,
                "failed_agents": 0,
                "errors": ["no_agent_execution"],
            }

        return {
            "verified": len(errors) == 0,
            "completed_agents": len(outputs) - len(errors),
            "failed_agents": len(errors),
            "errors": errors,
        }

    def run(
        self,
        task_id: str,
        request: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TaskResult:

        context = self.create_context(
            task_id,
            request,
            metadata,
        )

        try:
            analysis = self.analyze(context)
            plan = self.plan(context, analysis)
            agents = self.route(context, plan)
            execution = self.execute(context, agents)
            verification = self.verify(context, execution)

            status = (
                "completed"
                if verification["verified"]
                else "needs_review"
            )

            return TaskResult(
                task_id=task_id,
                status=status,
                phase="completed",
                result={
                    "analysis": analysis,
                    "plan": plan,
                    "execution": execution,
                },
                agents=agents,
                verification=verification,
            )

        except Exception as exc:
            return TaskResult(
                task_id=task_id,
                status="error",
                phase="failed",
                errors=[str(exc)],
            )
