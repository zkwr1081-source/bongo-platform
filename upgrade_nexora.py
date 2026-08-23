from pathlib import Path
import subprocess, sys, textwrap

ROOT = Path.cwd()

def put(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print("✓", path)

# ============================================================
# EVENT BUS
# ============================================================

put("nexora/core/bus.py", r'''
from collections import defaultdict
from threading import RLock

class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event, handler):
        with self._lock:
            self._handlers[event].append(handler)

    def publish(self, event, payload=None):
        payload = payload or {}
        with self._lock:
            handlers = list(self._handlers.get(event, []))

        results = []
        for handler in handlers:
            results.append(handler(payload))
        return results
''')

# ============================================================
# TASK ENGINE
# ============================================================

put("nexora/core/tasks.py", r'''
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

class TaskState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class Task:
    goal: str
    agent: str = "orchestrator"
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    state: TaskState = TaskState.CREATED
    result: object = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def transition(self, state):
        self.state = state
        self.updated_at = time.time()
''')

# ============================================================
# TOOL REGISTRY
# ============================================================

put("nexora/plugins/tools.py", r'''
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    handler: object
    description: str = ""
    permissions: tuple = ()

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool):
        if not isinstance(tool, Tool):
            raise TypeError("tool must be Tool")
        self.tools[tool.name] = tool

    def get(self, name):
        return self.tools.get(name)

    def execute(self, name, *args, **kwargs):
        tool = self.get(name)
        if not tool:
            raise KeyError(f"tool not found: {name}")
        return tool.handler(*args, **kwargs)

    def list(self):
        return sorted(self.tools)
''')

# ============================================================
# PERMISSION ENGINE
# ============================================================

put("nexora/security/permissions.py", r'''
class PermissionEngine:
    def __init__(self):
        self.roles = {
            "system": {"*"},
            "orchestrator": {
                "task.execute",
                "memory.read",
                "memory.write",
                "tool.execute"
            },
            "guest": {
                "memory.read"
            }
        }

    def allowed(self, actor, permission):
        perms = self.roles.get(actor, set())
        return "*" in perms or permission in perms

    def require(self, actor, permission):
        if not self.allowed(actor, permission):
            raise PermissionError(
                f"permission denied: {actor} -> {permission}"
            )
        return True
''')

# ============================================================
# VERIFICATION ENGINE
# ============================================================

put("nexora/core/verify.py", r'''
class VerificationResult:
    def __init__(self, ok, reason=""):
        self.ok = bool(ok)
        self.reason = reason

    def as_dict(self):
        return {
            "ok": self.ok,
            "reason": self.reason
        }

class Verifier:
    def verify(self, result):
        if result is None:
            return VerificationResult(False, "empty result")

        if isinstance(result, dict):
            if result.get("status") == "error":
                return VerificationResult(False, "result reports error")

        return VerificationResult(True, "accepted")
''')

# ============================================================
# PLUGIN LIFECYCLE
# ============================================================

put("nexora/plugins/lifecycle.py", r'''
from enum import Enum

class PluginState(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    DISABLED = "disabled"

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def install(self, name, plugin):
        self.plugins[name] = {
            "plugin": plugin,
            "state": PluginState.REGISTERED
        }

    def activate(self, name):
        item = self.plugins[name]
        item["state"] = PluginState.ACTIVE

        plugin = item["plugin"]
        hook = getattr(plugin, "on_activate", None)

        if hook:
            hook()

    def disable(self, name):
        item = self.plugins[name]
        item["state"] = PluginState.DISABLED

        plugin = item["plugin"]
        hook = getattr(plugin, "on_disable", None)

        if hook:
            hook()

    def status(self):
        return {
            name: item["state"].value
            for name, item in self.plugins.items()
        }
''')

# ============================================================
# ORCHESTRATOR
# ============================================================

put("nexora/agents/orchestrator.py", r'''
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
''')

# ============================================================
# UPDATE KERNEL
# ============================================================

put("nexora/core/kernel.py", r'''
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
''')

# ============================================================
# UPDATE AGENT MANAGER
# ============================================================

put("nexora/agents/manager.py", r'''
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
''')

# ============================================================
# UPDATE RUNTIME
# ============================================================

put("nexora/runtime/app.py", r'''
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
''')

# ============================================================
# API UPGRADE
# ============================================================

put("nexora/api/server.py", r'''
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from nexora.runtime.app import app

class Handler(BaseHTTPRequestHandler):

    def _send(self, code, data):
        raw = json.dumps(
            data,
            ensure_ascii=False,
            default=str
        ).encode()

        self.send_response(code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            return self._send(
                200,
                app.kernel.status()
            )

        if parsed.path == "/health":
            return self._send(
                200,
                {
                    "status": "ok",
                    "health": app.kernel.health.check()
                }
            )

        if parsed.path == "/metrics":
            return self._send(
                200,
                app.kernel.metrics.snapshot()
            )

        if parsed.path == "/agents":
            return self._send(
                200,
                {"agents": app.kernel.agents.list()}
            )

        if parsed.path == "/tools":
            return self._send(
                200,
                {"tools": app.kernel.tools.list()}
            )

        if parsed.path == "/plugins":
            return self._send(
                200,
                {
                    "plugins": app.kernel.plugin_manager.status()
                }
            )

        if parsed.path == "/task":
            query = parse_qs(parsed.query)
            goal = query.get("goal", [""])[0]

            if not goal:
                return self._send(
                    400,
                    {"error": "goal_required"}
                )

            task = app.task(goal)

            return self._send(
                200,
                {
                    "id": task.id,
                    "state": task.state.value,
                    "result": task.result,
                    "error": task.error
                }
            )

        self._send(404, {"error": "not_found"})

    def log_message(self, *_):
        pass

def run(host="127.0.0.1", port=8082):
    app.start()

    server = ThreadingHTTPServer(
        (host, port),
        Handler
    )

    print(f"NEXORA INFRASTRUCTURE → http://{host}:{port}")
    print("Endpoints:")
    print("  /")
    print("  /health")
    print("  /metrics")
    print("  /agents")
    print("  /tools")
    print("  /plugins")
    print("  /task?goal=hello")

    server.serve_forever()
''')

# ============================================================
# ADVANCED TESTS
# ============================================================

put("nexora/tests/test_platform.py", r'''
from nexora.runtime.app import NEXORA
from nexora.plugins.tools import Tool

def test_event_bus():
    app = NEXORA()

    values = []

    app.kernel.events.subscribe(
        "test",
        lambda payload: values.append(payload["value"])
    )

    app.kernel.events.publish(
        "test",
        {"value": 42}
    )

    assert values == [42]

def test_tool_registry():
    app = NEXORA()

    app.kernel.tools.register(
        Tool(
            name="add",
            handler=lambda a, b: a + b,
            description="addition"
        )
    )

    assert app.kernel.tools.execute(
        "add", 2, 3
    ) == 5

def test_task_engine():
    app = NEXORA()

    task = app.task("hello")

    assert task.state.value == "success"
    assert task.result["status"] == "accepted"

def test_permissions():
    app = NEXORA()

    assert app.kernel.permissions.allowed(
        "orchestrator",
        "task.execute"
    )

def test_verifier():
    app = NEXORA()

    result = app.kernel.verifier.verify(
        {"status": "accepted"}
    )

    assert result.ok is True

def test_plugin_lifecycle():
    app = NEXORA()

    class Plugin:
        def __init__(self):
            self.active = False

        def on_activate(self):
            self.active = True

    plugin = Plugin()

    app.kernel.plugin_manager.install(
        "demo",
        plugin
    )

    app.kernel.plugin_manager.activate("demo")

    assert plugin.active is True
    assert app.kernel.plugin_manager.status()["demo"] == "active"
''')

# ============================================================
# VERSION
# ============================================================

put("nexora/VERSION", "0.2.0\n")

# ============================================================
# TEST
# ============================================================

print("\n🧪 Running full NEXORA platform tests...\n")

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "nexora/tests"],
    cwd=ROOT
)

if result.returncode != 0:
    print("\n❌ TESTS FAILED — no commit created.")
    sys.exit(result.returncode)

# ============================================================
# GIT
# ============================================================

subprocess.run(
    ["git", "add", "nexora"],
    cwd=ROOT,
    check=True
)

subprocess.run(
    [
        "git",
        "commit",
        "-m",
        "Upgrade NEXORA autonomous infrastructure platform"
    ],
    cwd=ROOT
)

print("\n" + "=" * 64)
print("🔥 NEXORA PLATFORM UPGRADE COMPLETE")
print("=" * 64)
print("Tests: PASS")
print("Core: Event Bus + Task Engine + Verification")
print("Agents: Orchestrator")
print("Tools: Registry")
print("Plugins: Lifecycle")
print("Security: Permissions + Audit")
print("Memory: Persistent Store")
print("Recovery: Health")
print("API: Operational")
print("\nNext launch:")
print("python3 run_nexora.py")
print("=" * 64)
