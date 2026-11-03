"""SQLite persistence for the NEXORA Business Operations MVP.

Amounts are stored as integer minor units (e.g. cents), never binary floats.
Metrics are grouped by currency and include collected cash only.
"""
from __future__ import annotations

import os
import re
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB = os.environ.get("NEXORA_BUSINESS_DB", "nexora_business.db")
CURRENCIES = re.compile(r"^[A-Z]{3}$")
STAGES = {"idea", "validation", "build", "launch", "operating", "paused", "archived"}
TX_STATUSES = {"pending", "collected", "void"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def init_db(db_path: str | Path = DEFAULT_DB) -> None:
    path = Path(db_path)
    if str(db_path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(db_path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'digital',
            stage TEXT NOT NULL CHECK(stage IN ('idea','validation','build','launch','operating','paused','archived')),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL REFERENCES projects(id),
            kind TEXT NOT NULL CHECK(kind IN ('income','expense')),
            amount_minor INTEGER NOT NULL CHECK(amount_minor > 0),
            currency TEXT NOT NULL CHECK(length(currency) = 3),
            status TEXT NOT NULL CHECK(status IN ('pending','collected','void')),
            source TEXT NOT NULL DEFAULT '',
            transaction_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_transactions_project_date
            ON transactions(project_id, transaction_date);
        CREATE INDEX IF NOT EXISTS idx_transactions_status_currency
            ON transactions(status, currency);
        """)


def _project(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def create_project(name: str, description: str = "", category: str = "digital",
                   stage: str = "idea", db_path: str | Path = DEFAULT_DB) -> dict[str, Any]:
    name = name.strip()
    description = description.strip()
    category = category.strip().lower()
    stage = stage.strip().lower()
    if not name or len(name) > 120:
        raise ValueError("name must be 1-120 characters")
    if len(description) > 2000:
        raise ValueError("description must be 2000 characters or fewer")
    if not category or len(category) > 60:
        raise ValueError("category must be 1-60 characters")
    if stage not in STAGES:
        raise ValueError(f"stage must be one of: {', '.join(sorted(STAGES))}")
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO projects(name,description,category,stage,created_at) VALUES(?,?,?,?,?)",
            (name, description, category, stage, _now()),
        )
        row = conn.execute("SELECT * FROM projects WHERE id=?", (cur.lastrowid,)).fetchone()
        return _project(row)


def list_projects(db_path: str | Path = DEFAULT_DB) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
        return [_project(row) for row in rows]


def add_transaction(project_id: int, kind: str, amount_minor: int, currency: str,
                    status: str = "collected", source: str = "",
                    transaction_date: str | None = None,
                    db_path: str | Path = DEFAULT_DB) -> dict[str, Any]:
    kind, status, currency = kind.strip().lower(), status.strip().lower(), currency.strip().upper()
    source = source.strip()
    if kind not in {"income", "expense"}:
        raise ValueError("kind must be income or expense")
    if status not in TX_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(sorted(TX_STATUSES))}")
    if isinstance(amount_minor, bool) or not isinstance(amount_minor, int) or amount_minor <= 0:
        raise ValueError("amount_minor must be a positive integer")
    if not CURRENCIES.fullmatch(currency):
        raise ValueError("currency must be a 3-letter uppercase currency code")
    if len(source) > 160:
        raise ValueError("source must be 160 characters or fewer")
    tx_date = transaction_date or date.today().isoformat()
    try:
        date.fromisoformat(tx_date)
    except (TypeError, ValueError):
        raise ValueError("transaction_date must use YYYY-MM-DD") from None
    with _connect(db_path) as conn:
        if conn.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone() is None:
            raise ValueError("project_id does not exist")
        cur = conn.execute("""
            INSERT INTO transactions(project_id,kind,amount_minor,currency,status,source,transaction_date,created_at)
            VALUES(?,?,?,?,?,?,?,?)
        """, (project_id, kind, amount_minor, currency, status, source, tx_date, _now()))
        row = conn.execute("SELECT * FROM transactions WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row)


def dashboard(db_path: str | Path = DEFAULT_DB) -> dict[str, Any]:
    with _connect(db_path) as conn:
        projects_total = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        projects_active = conn.execute(
            "SELECT COUNT(*) FROM projects WHERE stage IN ('build','launch','operating')"
        ).fetchone()[0]
        collected = conn.execute("""
            SELECT currency,
                   SUM(CASE WHEN kind='income' THEN amount_minor ELSE 0 END) AS income_minor,
                   SUM(CASE WHEN kind='expense' THEN amount_minor ELSE 0 END) AS expense_minor,
                   COUNT(*) AS collected_records
            FROM transactions WHERE status='collected'
            GROUP BY currency ORDER BY currency
        """).fetchall()
        pending = conn.execute("""
            SELECT currency, SUM(CASE WHEN kind='income' THEN amount_minor ELSE 0 END) AS pending_income_minor,
                   SUM(CASE WHEN kind='expense' THEN amount_minor ELSE 0 END) AS pending_expense_minor
            FROM transactions WHERE status='pending' GROUP BY currency ORDER BY currency
        """).fetchall()
        return {
            "generated_at": _now(),
            "projects_total": projects_total,
            "projects_active": projects_active,
            "cash_by_currency": [
                {"currency": row["currency"], "collected_income_minor": row["income_minor"] or 0,
                 "collected_expense_minor": row["expense_minor"] or 0,
                 "net_collected_minor": (row["income_minor"] or 0) - (row["expense_minor"] or 0),
                 "collected_records": row["collected_records"]}
                for row in collected
            ],
            "pending_by_currency": [dict(row) for row in pending],
            "revenue_definition": "Collected income only; pending items are excluded. Values are minor units and currencies are never combined.",
        }
