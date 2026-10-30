"""Local-first evidence ledger and opportunity scoring for BONGO discovery MVP.

No network access, model calls, shell execution, or external side effects occur here.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DOMAINS = {"water", "food", "energy", "health", "education", "disaster", "cyber", "climate", "public_services", "ai_accountability"}
CLAIM_TYPES = {"observed_fact", "estimate", "hypothesis", "opinion"}
REQUIRED = ("title", "source_name", "source_url", "excerpt", "domain", "claim_type", "geography")
DIMENSIONS = ("urgency", "reach", "evidence_quality", "gap", "feasibility", "time_to_impact")
RISK_DIMENSIONS = ("safety_risk", "privacy_risk", "environmental_risk")
SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
 id INTEGER PRIMARY KEY,
 record_key TEXT NOT NULL UNIQUE,
 title TEXT NOT NULL,
 source_name TEXT NOT NULL,
 source_url TEXT NOT NULL,
 license TEXT NOT NULL,
 published_at TEXT NOT NULL,
 collected_at TEXT NOT NULL,
 excerpt TEXT NOT NULL,
 domain TEXT NOT NULL,
 claim_type TEXT NOT NULL,
 geography TEXT NOT NULL,
 content_hash TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS opportunities (
 id INTEGER PRIMARY KEY,
 title TEXT NOT NULL UNIQUE,
 problem TEXT NOT NULL,
 proposal TEXT NOT NULL,
 evidence_ids TEXT NOT NULL,
 scores TEXT NOT NULL,
 total_score REAL NOT NULL,
 confidence TEXT NOT NULL,
 created_at TEXT NOT NULL
);
"""

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def validate_evidence(item: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if not str(item.get(key, "")).strip()]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))
    if item["domain"] not in DOMAINS:
        raise ValueError("Unsupported domain")
    if item["claim_type"] not in CLAIM_TYPES:
        raise ValueError("Unsupported claim_type")
    if not str(item["source_url"]).startswith(("https://", "http://")):
        raise ValueError("source_url must be HTTP(S)")
    if len(str(item["excerpt"])) > 12000:
        raise ValueError("excerpt is too long")

class DiscoveryStore:
    def __init__(self, path: str | Path = "bongo_discovery.sqlite3"):
        self.path = str(path)
        with self.connect() as db:
            db.executescript(SCHEMA)

    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def add_evidence(self, item: dict[str, Any]) -> tuple[int, bool]:
        validate_evidence(item)
        canonical = json.dumps(item, ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(str(item["excerpt"]).encode()).hexdigest()
        key = hashlib.sha256((str(item["source_url"]).rstrip("/") + "|" + digest).encode()).hexdigest()
        with self.connect() as db:
            cur = db.execute("""INSERT OR IGNORE INTO evidence
            (record_key,title,source_name,source_url,license,published_at,collected_at,excerpt,domain,claim_type,geography,content_hash,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (key, item["title"], item["source_name"], item["source_url"], item.get("license","unspecified"),
             item.get("published_at","unknown"), item.get("collected_at",utc_now()), item["excerpt"],
             item["domain"], item["claim_type"], item["geography"], digest, utc_now()))
            row = db.execute("SELECT id FROM evidence WHERE record_key=?", (key,)).fetchone()
            return int(row["id"]), cur.rowcount == 1

    def list_evidence(self) -> list[dict[str, Any]]:
        with self.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM evidence ORDER BY id DESC")]

    def count(self) -> int:
        with self.connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM evidence").fetchone()[0])

    def add_opportunity(self, item: dict[str, Any]) -> int:
        scores = item["scores"]
        for key in DIMENSIONS + RISK_DIMENSIONS:
            if key not in scores or not isinstance(scores[key], (int,float)) or not 0 <= scores[key] <= 5:
                raise ValueError(f"{key} must be a number from 0 to 5")
        ids = [int(x) for x in item.get("evidence_ids", [])]
        with self.connect() as db:
            if ids:
                marks = ",".join("?" for _ in ids)
                found = db.execute(f"SELECT COUNT(*) FROM evidence WHERE id IN ({marks})", ids).fetchone()[0]
                if found != len(set(ids)):
                    raise ValueError("Every evidence_id must exist")
            positive = sum(float(scores[k]) for k in DIMENSIONS) / len(DIMENSIONS)
            risk = sum(float(scores[k]) for k in RISK_DIMENSIONS) / len(RISK_DIMENSIONS)
            total = round(max(0.0, positive - risk * 0.6), 2)
            confidence = "low" if not ids else ("medium" if len(ids) < 3 else "review")
            cur = db.execute("""INSERT INTO opportunities(title,problem,proposal,evidence_ids,scores,total_score,confidence,created_at)
            VALUES(?,?,?,?,?,?,?,?)""", (item["title"], item["problem"], item["proposal"],
            json.dumps(ids), json.dumps(scores), total, confidence, utc_now()))
            return int(cur.lastrowid)

    def list_opportunities(self) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM opportunities ORDER BY total_score DESC,id DESC").fetchall()
            result = []
            for row in rows:
                obj = dict(row)
                obj["evidence_ids"] = json.loads(obj["evidence_ids"])
                obj["scores"] = json.loads(obj["scores"])
                result.append(obj)
            return result

def import_json(store: DiscoveryStore, path: str | Path) -> dict[str, int]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    items = payload if isinstance(payload, list) else payload.get("evidence", [])
    if not isinstance(items, list):
        raise ValueError("JSON must be a list or an object containing an evidence list")
    added = duplicates = 0
    for item in items:
        _, inserted = store.add_evidence(item)
        added += int(inserted)
        duplicates += int(not inserted)
    return {"added": added, "duplicates": duplicates}
