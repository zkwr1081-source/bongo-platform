from bongo import create_runtime

def test_service_count():
    runtime = create_runtime(1000)
    assert runtime.registry.count() == 1003

def test_all_categories_exist():
    runtime = create_runtime(1000)
    assert len(runtime.registry.categories()) >= 20

def test_generated_service_executes():
    runtime = create_runtime(1000)
    result = runtime.router.dispatch("ai.service_0001", test="ok")
    assert result["ok"] is True
    assert result["service"] == "ai.service_0001"

def test_last_service_executes():
    runtime = create_runtime(1000)
    result = runtime.router.dispatch("knowledge.service_1000")
    assert result["ok"] is True
    assert result["service"] == "knowledge.service_1000"
