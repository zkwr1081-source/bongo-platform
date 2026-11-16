"""Keep NEXORA persistence isolated from the working tree during tests."""
import pytest

from nexora.memory.store import MemoryStore
from nexora.security.audit import AuditLog


@pytest.fixture(autouse=True)
def isolate_nexora_persistence(tmp_path, monkeypatch):
    """Route test-created memory and audit data into pytest's temp directory."""
    monkeypatch.setattr(
        "nexora.core.kernel.MemoryStore",
        lambda: MemoryStore(tmp_path / "memory" / "store.json"),
    )
    monkeypatch.setattr(
        "nexora.core.kernel.AuditLog",
        lambda: AuditLog(tmp_path / "logs" / "audit.jsonl"),
    )
