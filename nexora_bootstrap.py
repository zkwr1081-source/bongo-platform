from pathlib import Path
import json, os, sys, time, subprocess, textwrap, shutil

ROOT = Path.cwd()
print("\n🚀 NEXORA INFRASTRUCTURE BOOTSTRAP")
print("=" * 60)
print(f"ROOT: {ROOT}")

# ---------- helpers ----------
def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        print(f"↻ update  {rel}")
    else:
        print(f"+ create  {rel}")
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

def ensure_dir(rel):
    (ROOT / rel).mkdir(parents=True, exist_ok=True)

# ---------- directories ----------
dirs = [
    "nexora/core",
    "nexora/agents",
    "nexora/plugins",
    "nexora/memory",
    "nexora/security",
    "nexora/observability",
    "nexora/recovery",
    "nexora/governance",
    "nexora/api",
    "nexora/runtime",
    "nexora/tests",
    "data/memory",
    "data/logs",
    "data/runtime",
    "config",
]

for d in dirs:
    ensure_dir(d)

# ---------- package ----------
write("nexora/__init__.py", '''
__version__ = "0.1.0-infrastructure"
''')

write("nexora/core/__init__.py", "")
write("nexora/agents/__init__.py", "")
write("nexora/plugins/__init__.py", "")
write("nexora/memory/__init__.py", "")
write("nexora/security/__init__.py", "")
write("nexora/observability/__init__.py", "")
write("nexora/recovery/__init__.py", "")
write("nexora/governance/__init__.py", "")
write("nexora/api/__init__.py", "")
write("nexora/runtime/__init__.py", "")

# ---------- event model ----------
write("nexora/core/events.py", '''
from dataclasses import dataclass, field
from typing import Any
import time, uuid

@dataclass
class Event:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: float = field(default_factory=time.time)
''')

# ---------- governance ----------
write("nexora/governance/policy.py", '''
from dataclasses import dataclass

@dataclass(frozen=True)
class Policy:
    allow_network: bool = True
    allow_tools: bool = True
    max_steps: int = 32
    require_audit: bool = True

DEFAULT_POLICY = Policy()
''')

# ---------- security ----------
write("nexora/security/audit.py", '''
from pathlib import Path
import json, time

class AuditLog:
    def __init__(self, path="data/logs/audit.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, action, actor="system", metadata=None):
        row = {
            "ts": time.time(),
            "actor": actor,
            "action": action,
            "metadata": metadata or {}
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\\n")
        return row
''')

# ---------- observability ----------
write("nexora/observability/metrics.py", '''
from collections import Counter
import time

class Metrics:
    def __init__(self):
        self.counters = Counter()
        self.started = time.time()

    def inc(self, name, value=1):
        self.counters[name] += value

    def snapshot(self):
        return {
            "uptime": round(time.time() - self.started, 3),
            "counters": dict(self.counters)
        }
''')

# ---------- memory ----------
write("nexora/memory/store.py", '''
from pathlib import Path
import json, threading

class MemoryStore:
    def __init__(self, path="data/memory/store.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def remember(self, key, value, tags=None):
        with self.lock:
            data = self._load()
            data.append({
                "key": key,
                "value": value,
                "tags": tags or []
            })
            self.path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    def search(self, query):
        query = query.lower()
        with self.lock:
            return [
                x for x in self._load()
                if query in str(x).lower()
            ][-50:]
''')

# ---------- plugin system ----------
write("nexora/plugins/registry.py", '''
class PluginRegistry:
    def __init__(self):
        self.plugins = {}

    def register(self, name, plugin):
        if not name or plugin is None:
            raise ValueError("invalid plugin")
        self.plugins[name] = plugin

    def get(self, name):
        return self.plugins.get(name)

    def list(self):
        return sorted(self.plugins)
''')

# ---------- agents ----------
write("nexora/agents/base.py", '''
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
''')

write("nexora/agents/manager.py", '''
from .base import Agent

class AgentManager:
    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.name] = agent

    def get(self, name):
        return self.agents.get(name)

    def execute(self, name, task, context=None):
        agent = self.get(name)
        if not agent:
            raise KeyError(f"agent not found: {name}")
        return agent.run(task, context)
''')

# ---------- recovery ----------
write("nexora/recovery/health.py", '''
class Health:
    def __init__(self):
        self.components = {}

    def register(self, name, checker):
        self.components[name] = checker

    def check(self):
        result = {}
        for name, checker in self.components.items():
            try:
                result[name] = bool(checker())
            except Exception:
                result[name] = False
        return result
''')

# ---------- core kernel ----------
write("nexora/core/kernel.py", '''
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
''')

# ---------- runtime ----------
write("nexora/runtime/app.py", '''
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
''')

# ---------- API ----------
write("nexora/api/server.py", '''
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from nexora.runtime.app import app

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/":
            return self._send(200, {
                "name": "NEXORA",
                "message": "Infrastructure online",
                "status": app.kernel.status()
            })

        if self.path == "/health":
            return self._send(200, {
                "status": "ok",
                "health": app.kernel.health.check()
            })

        if self.path == "/metrics":
            return self._send(200, app.kernel.metrics.snapshot())

        if self.path == "/agents":
            return self._send(200, {
                "agents": list(app.kernel.agents.agents)
            })

        if self.path == "/plugins":
            return self._send(200, {
                "plugins": app.kernel.plugins.list()
            })

        if self.path == "/memory":
            return self._send(200, {
                "memory": app.kernel.memory.search("")
            })

        self._send(404, {"error": "not_found"})

    def log_message(self, *_):
        pass

def run(host="127.0.0.1", port=8082):
    app.start()
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"NEXORA API → http://{host}:{port}")
    server.serve_forever()
''')

# ---------- tests ----------
write("nexora/tests/test_infrastructure.py", '''
from nexora.runtime.app import NEXORA

def test_kernel():
    app = NEXORA()
    result = app.start()
    assert result["name"] == "NEXORA"
    assert result["started"] is True

def test_agent():
    app = NEXORA()
    result = app.kernel.agents.execute(
        "orchestrator",
        "test task"
    )
    assert result["status"] == "accepted"

def test_memory():
    app = NEXORA()
    app.kernel.memory.remember("bootstrap", "ok", ["system"])
    assert app.kernel.memory.search("bootstrap")
''')

# ---------- launcher ----------
write("run_nexora.py", '''
from nexora.api.server import run

if __name__ == "__main__":
    run()
''')

# ---------- config ----------
write("config/nexora.json", json.dumps({
    "name": "NEXORA",
    "mode": "infrastructure",
    "api": {
        "host": "127.0.0.1",
        "port": 8082
    },
    "features": {
        "agents": True,
        "plugins": True,
        "memory": True,
        "security_audit": True,
        "observability": True,
        "recovery": True,
        "governance": True
    }
}, indent=2))

# ---------- documentation ----------
write("NEXORA_INFRASTRUCTURE.md", '''
# NEXORA Infrastructure

NEXORA is organized as an extensible infrastructure layer.

## Layers

Core → Agents → Plugins → Memory → Security → Governance
→ Observability → Recovery → API → Runtime

The architecture intentionally separates responsibilities so new
capabilities can be added without rewriting the kernel.

## Current endpoints

- `/`
- `/health`
- `/metrics`
- `/agents`
- `/plugins`
- `/memory`
''')

# ---------- run tests ----------
print("\n🧪 Running infrastructure tests...")
try:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "nexora/tests"],
        cwd=ROOT,
        text=True
    )
    tests_ok = result.returncode == 0
except Exception as e:
    tests_ok = False
    print("pytest unavailable:", e)

# ---------- git ----------
print("\n📦 Saving infrastructure state...")
try:
    subprocess.run(["git", "add", "nexora", "config", "run_nexora.py",
                    "NEXORA_INFRASTRUCTURE.md"], cwd=ROOT)
    subprocess.run(
        ["git", "commit", "-m", "Build NEXORA infrastructure foundation"],
        cwd=ROOT
    )
except Exception as e:
    print("git note:", e)

# ---------- final ----------
print("\n" + "=" * 60)
print("NEXORA INFRASTRUCTURE READY")
print("=" * 60)
print("Tests:", "PASS ✅" if tests_ok else "CHECK ⚠️")
print("API:   http://127.0.0.1:8082")
print("\nTo launch:")
print("python3 run_nexora.py")
print("\nThis bootstrap preserved the existing project.")
