from nexora.agents.manager import AgentManager
from nexora.plugins.registry import PluginRegistry
from nexora.memory.store import MemoryStore
from nexora.security.audit import AuditLog
from nexora.observability.metrics import Metrics
from nexora.recovery.health import Health
from nexora.governance.policy import DEFAULT_POLICY

class Kernel:
    def __init__(self):
        self.policy = DEFAULT_POLICY
        self.agents = AgentManager()
        self.plugins = PluginRegistry()
        self.memory = MemoryStore()
        self.audit = AuditLog()
        self.metrics = Metrics()
        self.health = Health()
        self.started = False

    def start(self):
        self.started = True
        self.audit.record("kernel.start")
        self.metrics.inc("kernel.starts")
        return self.status()

    def status(self):
        return {
            "name": "NEXORA",
            "version": "0.1.0-infrastructure",
            "started": self.started,
            "agents": self.agents.list() if hasattr(self.agents, "list") else list(self.agents.agents),
            "plugins": self.plugins.list(),
            "metrics": self.metrics.snapshot(),
            "health": self.health.check()
        }
