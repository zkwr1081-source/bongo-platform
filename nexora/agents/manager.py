class AgentManager:
    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.name] = agent

    def get(self, name):
        return self.agents.get(name)

    def list(self):
        return sorted(self.agents)

    def execute(self, name, task, context=None):
        agent = self.get(name)

        if not agent:
            raise KeyError(f"agent not found: {name}")

        return agent.run(task, context or {})
