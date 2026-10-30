"""Deterministic planning primitives for the supervised BONGO Factory MVP.

This module deliberately does not call an LLM, execute shell commands, access
GitHub credentials, or perform external side effects.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class Task:
    task_id: str
    role: str
    title: str
    description: str
    requires_owner_approval: bool = False


@dataclass(frozen=True)
class ProjectPlan:
    request: str
    tasks: tuple[Task, ...]
    approval_gates: tuple[str, ...]
    status: str = "awaiting_owner_review"

    def to_dict(self) -> dict:
        result = asdict(self)
        result["tasks"] = [asdict(task) for task in self.tasks]
        result["approval_gates"] = list(self.approval_gates)
        return result


_APPROVAL_TERMS = (
    "deploy",
    "production",
    "delete data",
    "change permissions",
    "purchase",
    "payment",
    "wallet",
    "transfer funds",
    "merge to main",
)


def _requires_approval(request: str) -> bool:
    normalized = request.casefold()
    return any(term in normalized for term in _APPROVAL_TERMS)


def build_plan(request: str, extra_checks: Iterable[str] = ()) -> ProjectPlan:
    """Build a reviewable starter plan; never execute the requested work."""
    clean_request = request.strip()
    if not clean_request:
        raise ValueError("request must not be empty")
    if len(clean_request) > 4000:
        raise ValueError("request must be 4000 characters or fewer")

    sensitive = _requires_approval(clean_request)
    tasks = (
        Task("T1", "product_analyst", "Clarify scope", "Define users, problem, constraints, and acceptance criteria."),
        Task("T2", "solution_architect", "Design solution", "Propose components, interfaces, data flows, and risks."),
        Task("T3", "security_reviewer", "Review safety", "Identify data exposure, permission, dependency, and abuse risks."),
        Task("T4", "implementation_engineer", "Prepare implementation", "Break approved scope into small feature-branch changes.", True),
        Task("T5", "quality_engineer", "Verify outcome", "Define and run allowlisted tests; report evidence and limitations."),
        Task("T6", "business_analyst", "Assess value", "Estimate costs and validate customer value before commercial claims."),
    )
    gates = [
        "Owner approval before implementation beyond planning",
        "Owner approval before merge, deployment, purchases, or external side effects",
        "Never expose secrets, wallet keys, or recovery phrases to agents",
    ]
    if sensitive:
        gates.insert(0, "Explicit owner approval required: request mentions a sensitive operation")
    gates.extend(f"Additional check: {item}" for item in extra_checks if item.strip())
    return ProjectPlan(clean_request, tasks, tuple(gates))


__all__ = ["ProjectPlan", "Task", "build_plan"]
