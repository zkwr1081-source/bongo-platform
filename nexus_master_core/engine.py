"""NEXUS Master Core: safe, auditable orchestration engine.

All market/trading/treasury activities in this package are simulations.
No exchange, bank, wallet, or payment API is called by this implementation.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import signal
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG = logging.getLogger("NexusMasterCore")
DEFAULT_DB = Path(os.getenv("NEXUS_DB_PATH", "nexus_master_core.db"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = str(path)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def initialize(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS agent_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_num INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agent_cycles_time
                    ON agent_cycles(timestamp);
                CREATE TABLE IF NOT EXISTS financial_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    destination TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    reference TEXT
                );
            """)

    def audit(self, cycle: int, module: str, status: str, details: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO agent_cycles
                   (cycle_num,module_name,status,details,timestamp)
                   VALUES (?,?,?,?,?)""",
                (cycle, module, status, json.dumps(details, ensure_ascii=False), utc_now()),
            )

    def record_simulation(self, source: str, amount: float, destination: str, reference: str) -> None:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO financial_ledger
                   (source,amount,destination,status,timestamp,reference)
                   VALUES (?,?,?,?,?,?)""",
                (source, amount, destination, "SIMULATED_ONLY", utc_now(), reference),
            )


class SecretsVault:
    """Read secrets from environment; never print or persist their values."""
    @staticmethod
    def get_secret(key_name: str, default: str = "") -> str:
        return os.getenv(key_name, default)


class MarketIntelligenceAgent:
    async def analyze(self) -> dict[str, Any]:
        LOG.info("Market intelligence: returning clearly marked demo signal")
        return {"mode": "simulation", "trend": "unknown", "opportunity_score": 0.0}


class AlgorithmicTradingAgent:
    async def execute_trade(self, intelligence: dict[str, Any]) -> dict[str, Any]:
        # No order placement is implemented. Fail closed even if a demo signal is injected.
        return {
            "mode": "simulation",
            "executed": False,
            "reason": "No broker integration; live trading is disabled",
            "input_mode": intelligence.get("mode", "unspecified"),
        }


class MicroSaaSBackend:
    async def process_service_request(self, user_payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "simulated", "revenue": 0.0, "persisted": False}


class InventoryManagerAgent:
    async def sync_inventory(self) -> dict[str, str]:
        return {"status": "simulated", "updated_items": "0"}


class ContentGeneratorAgent:
    async def generate_content(self) -> dict[str, str]:
        return {"status": "simulated", "published": "false"}


class VaultTransferAgent:
    async def transfer_to_cold_storage(self, amount: float, db: Database, reference: str) -> dict[str, Any]:
        # Ledger entry is explicitly a simulation, never a transfer.
        if amount <= 0:
            return {"status": "skipped", "reason": "amount must be positive"}
        db.record_simulation("SIMULATION", amount, "NO_WALLET_CONNECTED", reference)
        return {"status": "simulated_only", "amount": amount, "transferred": False}


class PortfolioRebalancer:
    async def rebalance(self) -> dict[str, str]:
        return {"status": "simulated", "orders_created": "0"}


class DigitalRealEstateAgent:
    async def scan_domains(self) -> dict[str, str]:
        return {"status": "simulated", "purchases": "0"}


class ComplianceReporter:
    def __init__(self, db: Database):
        self.db = db

    async def log_audit(self, cycle: int, event_type: str, details: dict[str, Any]) -> None:
        self.db.audit(cycle, event_type, "RECORDED", details)


@dataclass
class EngineConfig:
    interval_seconds: int = 15
    transfer_threshold: float = 500.0
    simulation_amount: float = 1200.0

    def __post_init__(self):
        if self.interval_seconds < 1:
            raise ValueError("interval_seconds must be >= 1")
        if self.transfer_threshold < 0 or self.simulation_amount < 0:
            raise ValueError("amounts must be non-negative")


class NexusMasterEngine:
    def __init__(self, interval: int = 15, db_path: str | Path = DEFAULT_DB):
        self.config = EngineConfig(interval_seconds=interval)
        self.db = Database(db_path)
        self.db.initialize()
        self.cycle = 0
        self.market_agent = MarketIntelligenceAgent()
        self.trading_agent = AlgorithmicTradingAgent()
        self.saas_backend = MicroSaaSBackend()
        self.inventory_agent = InventoryManagerAgent()
        self.content_agent = ContentGeneratorAgent()
        self.vault_agent = VaultTransferAgent()
        self.rebalancer = PortfolioRebalancer()
        self.domains_agent = DigitalRealEstateAgent()
        self.compliance = ComplianceReporter(self.db)

    async def run_once(self) -> dict[str, Any]:
        self.cycle += 1
        result: dict[str, Any] = {"cycle": self.cycle, "mode": "simulation"}
        try:
            intel = await self.market_agent.analyze()
            trade = await self.trading_agent.execute_trade(intel)
            result["market"] = intel
            result["trading"] = trade

            # Kept only as an explicitly simulated ledger demonstration.
            if self.config.simulation_amount > self.config.transfer_threshold:
                result["treasury"] = await self.vault_agent.transfer_to_cold_storage(
                    self.config.simulation_amount, self.db, f"cycle-{self.cycle}"
                )

            result["saas"] = await self.saas_backend.process_service_request({})
            result["inventory"] = await self.inventory_agent.sync_inventory()
            result["content"] = await self.content_agent.generate_content()
            result["portfolio"] = await self.rebalancer.rebalance()
            result["domains"] = await self.domains_agent.scan_domains()
            await self.compliance.log_audit(self.cycle, "CYCLE_COMPLETE", result)
            LOG.info("Cycle %s completed in simulation mode", self.cycle)
        except Exception as exc:
            LOG.exception("Cycle %s failed", self.cycle)
            self.db.audit(self.cycle, "CYCLE_FAILED", "ERROR", {"error": str(exc)})
            result["error"] = str(exc)
        return result

    async def run(self, stop_event: asyncio.Event | None = None) -> None:
        stop_event = stop_event or asyncio.Event()
        LOG.info("NEXUS Master Core started; interval=%ss; mode=simulation", self.config.interval_seconds)
        while not stop_event.is_set():
            started = asyncio.get_running_loop().time()
            await self.run_once()
            delay = max(0.0, self.config.interval_seconds - (asyncio.get_running_loop().time() - started))
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass
        LOG.info("NEXUS Master Core stopped cleanly")


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s [%(levelname)s] (NexusEngine): %(message)s",
    )
    parser = argparse.ArgumentParser(description="NEXUS Master Core (simulation only)")
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--once", action="store_true", help="run one cycle and exit")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    engine = NexusMasterEngine(interval=args.interval, db_path=args.db)

    async def runner():
        if args.once:
            print(json.dumps(await engine.run_once(), ensure_ascii=False, indent=2))
            return
        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop.set)
            except NotImplementedError:
                pass
        await engine.run(stop)

    asyncio.run(runner())


if __name__ == "__main__":
    main()
