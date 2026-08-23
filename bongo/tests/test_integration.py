from bongo import create_runtime

def test_integration_exists():
    runtime = create_runtime(1000)
    assert runtime.integration is not None

def test_every_service_has_capability():
    runtime = create_runtime(1000)

    for service in runtime.registry.list():
        capabilities = runtime.integration.capabilities.get(service.name)
        assert capabilities

def test_discovery():
    runtime = create_runtime(1000)

    results = runtime.integration.find("translation")

    assert results
    assert any("translation" in x["service"] for x in results)

def test_integrated_execution():
    runtime = create_runtime(1000)

    result = runtime.integration.execute(
        "ai.service_0001",
        source="integration-test"
    )

    assert result["ok"] is True
