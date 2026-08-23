from bongo import create_runtime

def test_runtime():
    runtime = create_runtime()
    assert runtime.status()["status"] == "ok"
    assert runtime.registry.count() >= 3

def test_ping():
    runtime = create_runtime()
    result = runtime.router.dispatch("system.ping")
    assert result["ok"] is True

def test_echo():
    runtime = create_runtime()
    result = runtime.router.dispatch("utility.echo", text="BONGO")
    assert result["text"] == "BONGO"
