from nexora.agents.manager import AgentManager
from nexora.plugins.registry import PluginRegistry
from nexora.plugins.tools import ToolRegistry
from nexora.plugins.lifecycle import PluginManager
from nexora.memory.store import MemoryStore
from nexora.security.audit import AuditLog
from nexora.security.permissions import PermissionEngine
from nexora.observability.metrics import Metrics
from nexora.recovery.health import Health
from nexora.governance.policy import DEFAULT_POLICY
from nexora.core.bus import EventBus
from nexora.core.verify import Verifier
from nexora.agents.orchestrator import Orchestrator

class Kernel:
    def __init__(self):
        self.policy = DEFAULT_POLICY

        self.agents = AgentManager()
        self.plugins = PluginRegistry()
        self.plugin_manager = PluginManager()
        self.tools = ToolRegistry()

        self.memory = MemoryStore()
        self.audit = AuditLog()
        self.permissions = PermissionEngine()

        self.metrics = Metrics()
        self.health = Health()

        self.events = EventBus()
        self.verifier = Verifier()

        self.started = False
        self.orchestrator = Orchestrator(self)

    def start(self):
        if self.started:
            return self.status()

        self.started = True

        self.audit.record("kernel.start")
        self.metrics.inc("kernel.starts")

        self.events.publish(
            "kernel.started",
            {"version": "0.2.0"}
        )

        return self.status()

    def status(self):
        return {
            "name": "NEXORA",
            "version": "0.2.0",
            "started": self.started,
            "agents": list(self.agents.agents),
            "plugins": self.plugins.list(),
            "plugin_states": self.plugin_manager.status(),
            "tools": self.tools.list(),
            "metrics": self.metrics.snapshot(),
            "health": self.health.check()
        }
