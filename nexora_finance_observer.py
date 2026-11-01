"""NEXORA Finance Observer — safe, read-only market telemetry prototype.

This module observes public market aggregates and records operational metrics.
It does NOT trade, generate revenue, move funds, create GitHub repositories,
or claim predictive confidence. Financial allocation is accounting-only and
requires an externally verified revenue amount.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

LOG = logging.getLogger("nexora.finance_observer")
DB_PATH = Path(os.getenv("NEXORA_FINANCE_DB", "nexora_finance_observer.db"))
MARKET_URL = "https://api.coingecko.com/api/v3/global"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_market_change(change_pct: float) -> str:
    """Describe the observed 24h change; this is not a forecast."""
    if change_pct >= 1.0:
        return "POSITIVE_MOMENTUM"
    if change_pct <= -1.0:
        return "NEGATIVE_MOMENTUM"
    return "RANGE_BOUND"


def split_verified_revenue(amount_usd: float) -> dict[str, float]:
    """Return an accounting illustration only; never initiates a payment."""
    if amount_usd < 0:
        raise ValueError("Revenue must be non-negative")
    reinvestment = round(amount_usd * 0.05, 2)
    beneficiary = round(amount_usd - reinvestment, 2)
    return {
        "gross_verified_revenue_usd": round(amount_usd, 2),
        "reinvestment_5pct_usd": reinvestment,
        "beneficiary_95pct_usd": beneficiary,
    }


def fetch_market_snapshot(timeout: float = 8.0) -> dict[str, Any]:
    request = Request(
        MARKET_URL,
        headers={"Accept": "application/json", "User-Agent": "NEXORA-Finance-Observer/1.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"Market data endpoint returned HTTP {response.status}")
        payload = json.loads(response.read().decode("utf-8"))
    data = payload.get("data", {})
    change = float(data.get("market_cap_change_percentage_24h_usd", 0.0))
    return {
        "observed_at": utc_now(),
        "market_cap_change_24h_pct": change,
        "observed_signal": classify_market_change(change),
        "total_market_cap_usd": data.get("total_market_cap", {}).get("usd"),
        "total_volume_24h_usd": data.get("total_volume", {}).get("usd"),
        "source": MARKET_URL,
        "is_forecast": False,
    }


class FinanceStore:
    def __init__(self, path: Path = DB_PATH):
        self.path = path

    def initialize(self) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS market_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    observed_at TEXT NOT NULL,
                    market_cap_change_24h_pct REAL NOT NULL,
                    observed_signal TEXT NOT NULL,
                    total_market_cap_usd REAL,
                    total_volume_24h_usd REAL,
                    source TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    agent_id INTEGER PRIMARY KEY,
                    tasks_completed INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS revenue_allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gross_verified_revenue_usd REAL NOT NULL,
                    reinvestment_5pct_usd REAL NOT NULL,
                    beneficiary_95pct_usd REAL NOT NULL,
                    status TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                )
            """)

    def save_observation(self, snapshot: dict[str, Any]) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute(
                """INSERT INTO market_observations
                (observed_at, market_cap_change_24h_pct, observed_signal,
                 total_market_cap_usd, total_volume_24h_usd, source)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    snapshot["observed_at"],
                    snapshot["market_cap_change_24h_pct"],
                    snapshot["observed_signal"],
                    snapshot.get("total_market_cap_usd"),
                    snapshot.get("total_volume_24h_usd"),
                    snapshot["source"],
                ),
            )

    def record_agent(self, agent_id: int, tasks_completed: int, status: str) -> None:
        with sqlite3.connect(self.path) as db:
            db.execute(
                """INSERT INTO agent_metrics(agent_id, tasks_completed, status, last_updated)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                tasks_completed=excluded.tasks_completed,
                status=excluded.status, last_updated=excluded.last_updated""",
                (agent_id, tasks_completed, status, utc_now()),
            )

    def record_verified_revenue(self, amount_usd: float) -> dict[str, float]:
        allocation = split_verified_revenue(amount_usd)
        with sqlite3.connect(self.path) as db:
            db.execute(
                """INSERT INTO revenue_allocations
                (gross_verified_revenue_usd, reinvestment_5pct_usd,
                 beneficiary_95pct_usd, status, recorded_at)
                VALUES (?, ?, ?, 'RECORDED_NOT_PAID', ?)""",
                (
                    allocation["gross_verified_revenue_usd"],
                    allocation["reinvestment_5pct_usd"],
                    allocation["beneficiary_95pct_usd"],
                    utc_now(),
                ),
            )
        return allocation


@dataclass(frozen=True)
class Settings:
    workers: int = 4
    poll_seconds: int = 300

    @classmethod
    def from_env(cls) -> "Settings":
        workers = int(os.getenv("NEXORA_WORKERS", "4"))
        poll_seconds = int(os.getenv("NEXORA_POLL_SECONDS", "300"))
        if not 1 <= workers <= 16:
            raise ValueError("NEXORA_WORKERS must be between 1 and 16")
        if poll_seconds < 60:
            raise ValueError("NEXORA_POLL_SECONDS must be at least 60")
        return cls(workers=workers, poll_seconds=poll_seconds)


class NexoraFinanceObserver:
    """Bounded telemetry loop; workers do not imply independent earning agents."""

    def __init__(self, store: FinanceStore, settings: Settings):
        self.store = store
        self.settings = settings
        self._stop = asyncio.Event()

    async def observe_once(self) -> dict[str, Any]:
        snapshot = await asyncio.to_thread(fetch_market_snapshot)
        await asyncio.to_thread(self.store.save_observation, snapshot)
        LOG.info("Observed market signal: %s (%+.3f%%)",
                 snapshot["observed_signal"], snapshot["market_cap_change_24h_pct"])
        return snapshot

    async def run(self) -> None:
        self.store.initialize()
        LOG.info("Starting observer with %d bounded workers; interval=%ds",
                 self.settings.workers, self.settings.poll_seconds)
        while not self._stop.is_set():
            try:
                await self.observe_once()
            except Exception:
                LOG.exception("Market observation failed; no financial action was taken")
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.settings.poll_seconds)
            except asyncio.TimeoutError:
                pass

    def stop(self) -> None:
        self._stop.set()


async def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    observer = NexoraFinanceObserver(FinanceStore(), Settings.from_env())
    try:
        await observer.run()
    except KeyboardInterrupt:
        observer.stop()


if __name__ == "__main__":
    asyncio.run(main())
