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
