from nexora.core.kernel import Kernel
from nexora.agents.base import Agent

class NEXORA:
    def __init__(self):
        self.kernel = Kernel()
        self.kernel.agents.register(
            Agent(
                "orchestrator",
                "Coordinates NEXORA tasks and system operations."
            )
        )
        self.kernel.health.register("kernel", lambda: self.kernel.started)

    def start(self):
        return self.kernel.start()

app = NEXORA()
