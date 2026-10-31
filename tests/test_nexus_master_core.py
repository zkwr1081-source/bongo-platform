import asyncio
import sqlite3
import tempfile
import unittest
from pathlib import Path

from nexus_master_core.engine import Database, EngineConfig, NexusMasterEngine, VaultTransferAgent


class NexusMasterCoreTests(unittest.TestCase):
    def test_config_rejects_invalid_interval(self):
        with self.assertRaises(ValueError):
            EngineConfig(interval_seconds=0)

    def test_one_cycle_is_simulation_and_audited(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "nexus.db"
            engine = NexusMasterEngine(interval=1, db_path=db_path)
            result = asyncio.run(engine.run_once())
            self.assertEqual(result["mode"], "simulation")
            self.assertFalse(result["trading"]["executed"])
            with sqlite3.connect(db_path) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM agent_cycles").fetchone()[0], 1)
                self.assertEqual(conn.execute("SELECT status FROM financial_ledger").fetchone()[0],
                                 "SIMULATED_ONLY")

    def test_vault_never_claims_transfer(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Database(Path(directory) / "ledger.db")
            db.initialize()
            result = asyncio.run(VaultTransferAgent().transfer_to_cold_storage(600, db, "test-ref"))
            self.assertFalse(result["transferred"])
            self.assertEqual(result["status"], "simulated_only")

    def test_negative_amount_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Database(Path(directory) / "ledger.db")
            db.initialize()
            with self.assertRaises(ValueError):
                db.record_simulation("test", -1, "none", "ref")


if __name__ == "__main__":
    unittest.main()
