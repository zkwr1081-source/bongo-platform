from dataclasses import dataclass

@dataclass
class Agent:
    name: str
    description: str = ""

    def run(self, task, context=None):
        return {
            "agent": self.name,
            "task": task,
            "status": "accepted",
            "context": context or {}
        }
