import pytest

from factory.planner import build_plan


def test_build_plan_creates_reviewable_tasks():
    plan = build_plan("Build a small inventory dashboard")
    assert plan.status == "awaiting_owner_review"
    assert len(plan.tasks) == 6
    assert plan.tasks[0].role == "product_analyst"
    assert any("Owner approval" in gate for gate in plan.approval_gates)


@pytest.mark.parametrize(
    "request",
    ["", "   "],
)
def test_build_plan_rejects_empty_request(request):
    with pytest.raises(ValueError):
        build_plan(request)


def test_build_plan_rejects_oversized_request():
    with pytest.raises(ValueError):
        build_plan("x" * 4001)


@pytest.mark.parametrize(
    "request",
    [
        "Deploy the service to production",
        "Delete data from the customer database",
        "Transfer funds from the wallet",
        "Merge to main",
    ],
)
def test_sensitive_requests_get_explicit_approval_gate(request):
    plan = build_plan(request)
    assert any("sensitive operation" in gate for gate in plan.approval_gates)


def test_extra_checks_are_preserved():
    plan = build_plan("Build API", extra_checks=["Check rate limits"])
    assert "Additional check: Check rate limits" in plan.approval_gates
