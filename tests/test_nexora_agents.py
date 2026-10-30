import asyncio

from nexora_agents import REGISTRY, build_registry, registry_summary, run_batch


def test_registry_has_1000_unique_agents():
    agents = build_registry()
    assert len(agents) == 1000
    assert len({agent.agent_id for agent in agents}) == 1000


def test_registry_summary_is_honest_about_model_connection():
    summary = registry_summary()
    assert summary["logical_agents"] == 1000
    assert summary["model_connected"] is False


def test_run_batch_executes_selected_agents():
    async def handler(agent, goal):
        return f"{agent.department}:{goal}"

    results = asyncio.run(
        run_batch("audit", handler, agent_ids=[REGISTRY[0].agent_id, REGISTRY[1].agent_id])
    )
    assert len(results) == 2
    assert all(item["status"] == "ok" for item in results)


def test_run_batch_rejects_unknown_agent():
    async def handler(agent, goal):
        return goal

    try:
        asyncio.run(run_batch("audit", handler, agent_ids=["NX-UNKNOWN-001"]))
    except ValueError as exc:
        assert "Unknown agent IDs" in str(exc)
    else:
        raise AssertionError("Expected unknown agent ID to be rejected")
