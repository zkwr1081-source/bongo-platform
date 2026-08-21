from nexora.core.tasks import Task, TaskState

class Orchestrator:
    def __init__(self, kernel):
        self.kernel = kernel

    def create(self, goal, agent="orchestrator"):
        return Task(goal=goal, agent=agent)

    def execute(self, task):
        self.kernel.permissions.require(
            "orchestrator",
            "task.execute"
        )

        task.transition(TaskState.RUNNING)

        try:
            result = self.kernel.agents.execute(
                task.agent,
                task.goal,
                {"task_id": task.id}
            )

            verification = self.kernel.verifier.verify(result)

            if not verification.ok:
                task.error = verification.reason
                task.transition(TaskState.FAILED)
            else:
                task.result = result
                task.transition(TaskState.SUCCESS)

            self.kernel.audit.record(
                "task.complete",
                actor="orchestrator",
                metadata={
                    "task_id": task.id,
                    "state": task.state.value
                }
            )

            return task

        except Exception as exc:
            task.error = str(exc)
            task.transition(TaskState.FAILED)

            self.kernel.audit.record(
                "task.failed",
                actor="orchestrator",
                metadata={
                    "task_id": task.id,
                    "error": str(exc)
                }
            )

            return task
