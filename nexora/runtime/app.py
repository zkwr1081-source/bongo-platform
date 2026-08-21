from nexora.core.kernel import Kernel
from nexora.agents.base import Agent

class NEXORA:
    def __init__(self):
        self.kernel = Kernel()

        self.kernel.agents.register(
            Agent(
                "orchestrator",
                "Coordinates tasks and system operations."
            )
        )

        self.kernel.health.register(
            "kernel",
            lambda: self.kernel.started
        )

        self.kernel.health.register(
            "memory",
            lambda: self.kernel.memory.path.exists()
        )

    def start(self):
        return self.kernel.start()

    def task(self, goal, agent="orchestrator"):
        task = self.kernel.orchestrator.create(
            goal,
            agent
        )
        return self.kernel.orchestrator.execute(task)

app = NEXORA()
