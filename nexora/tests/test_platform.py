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
