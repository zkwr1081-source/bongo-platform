import asyncio
import sqlite3

import pytest

from nexus_master_core.engine import (
    Database, EngineConfig, NexusMasterEngine, VaultTransferAgent
)


def test_config_rejects_invalid_interval():
    with pytest.raises(ValueError):
        EngineConfig(interval_seconds=0)


def test_one_cycle_records_audit_and_simulation_only(tmp_path):
    db_path = tmp_path / "nexus.db"
    engine = NexusMasterEngine(interval=1, db_path=db_path)
    result = asyncio.run(engine.run_once())
    assert result["mode"] == "simulation"
    assert result["trading"]["executed"] is False
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM agent_cycles").fetchone()[0] == 1
        row = conn.execute("SELECT status FROM financial_ledger").fetchone()
        assert row[0] == "SIMULATED_ONLY"


def test_vault_never_claims_transfer(tmp_path):
    db = Database(tmp_path / "ledger.db")
    db.initialize()
    result = asyncio.run(VaultTransferAgent().transfer_to_cold_storage(600, db, "test-ref"))
    assert result["transferred"] is False
    assert result["status"] == "simulated_only"


def test_negative_amount_rejected(tmp_path):
    db = Database(tmp_path / "ledger.db")
    db.initialize()
    with pytest.raises(ValueError):
        db.record_simulation("test", -1, "none", "ref")
