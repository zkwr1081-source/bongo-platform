"""FastAPI gateway for the existing NEXORA unified runtime.

Run locally with:
    uvicorn gateway:app --host 127.0.0.1 --port 8091

The legacy ThreadingHTTPServer in nexora_unified.py remains available and untouched.
Set NEXORA_API_TOKEN to enable POST /api/task. Requests must send
Authorization: Bearer <token>. The write endpoint stays disabled if no token is set.
"""
from __future__ import annotations

import asyncio
import hmac
import importlib
import logging
import os
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
CHECK_INTERVAL_SECONDS = 60
API_TOKEN = os.getenv("NEXORA_API_TOKEN", "").strip()

logging.basicConfig(
    level=os.getenv("NEXORA_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("nexora.gateway")

# Keep this list aligned with the real modules imported by nexora_unified.py.
CORE_FILES = (
    "nexora_unified.py",
    "action_engine.py",
    "command_gateway.py",
    "core/agents/__init__.py",
    "core/agents/analyst.py",
    "core/agents/future_intelligence.py",
    "core/agents/orchestrator.py",
    "core/agents/universal_intelligence.py",
    "core/agents/verify_agent.py",
)


def _load_core():
    """Import the actual unified module and validate its instantiated runtime objects."""
    core = importlib.import_module("nexora_unified")
    required = (
        "DB",
        "ACTION_ENGINE",
        "ANALYST_AGENT",
        "FUTURE_INTELLIGENCE_AGENT",
        "ORCHESTRATOR_AGENT",
        "VERIFY_AGENT",
        "UNIVERSAL_INTELLIGENCE_AGENT",
        "process_task",
    )
    missing = [name for name in required if not hasattr(core, name)]
    if missing:
        raise RuntimeError("NEXORA core exports missing: " + ", ".join(missing))
    return core


def _check_sqlite(database_path: str) -> dict[str, Any]:
    path = Path(database_path).resolve()
    if not path.is_file():
        return {"ok": False, "detail": "database_file_missing"}

    # as_uri() safely quotes spaces and special characters in filesystem paths.
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
    try:
        row = connection.execute("PRAGMA quick_check").fetchone()
        result = row[0] if row else "no_result"
        return {"ok": result == "ok", "detail": result}
    finally:
        connection.close()


def _perform_health_check(core) -> dict[str, Any]:
    files = {name: (ROOT / name).is_file() for name in CORE_FILES}
    missing = [name for name, exists in files.items() if not exists]
    try:
        instances = {
            "DB": core.DB is not None,
            "ACTION_ENGINE": core.ACTION_ENGINE is not None,
            "ANALYST_AGENT": core.ANALYST_AGENT is not None,
            "FUTURE_INTELLIGENCE_AGENT": core.FUTURE_INTELLIGENCE_AGENT is not None,
            "ORCHESTRATOR_AGENT": core.ORCHESTRATOR_AGENT is not None,
            "VERIFY_AGENT": core.VERIFY_AGENT is not None,
            "UNIVERSAL_INTELLIGENCE_AGENT": core.UNIVERSAL_INTELLIGENCE_AGENT is not None,
            "process_task": callable(core.process_task),
        }
        db_path = str(core.DB.path)
        database = _check_sqlite(db_path)
        ok = not missing and all(instances.values()) and database["ok"]
        return {
            "ok": ok,
            "checked_at": time.time(),
            "files": files,
            "missing_files": missing,
            "core_instances": instances,
            "sqlite": {"path": db_path, **database},
        }
    except Exception as exc:
        logger.exception("NEXORA health check failed")
        return {
            "ok": False,
            "checked_at": time.time(),
            "files": files,
            "missing_files": missing,
            "error": type(exc).__name__,
        }


async def _monitor_core(app: FastAPI) -> None:
    while True:
        try:
            app.state.health = await asyncio.to_thread(
                _perform_health_check, app.state.core
            )
            if app.state.health["ok"]:
                logger.info("core_health=healthy")
            else:
                logger.error("core_health=degraded details=%s", app.state.health)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Unexpected error in NEXORA monitoring loop")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.core = await asyncio.to_thread(_load_core)
    app.state.health = await asyncio.to_thread(_perform_health_check, app.state.core)
    monitor = asyncio.create_task(
        _monitor_core(app), name="nexora-core-health-monitor"
    )
    app.state.monitor_task = monitor
    logger.info(
        "NEXORA FastAPI gateway started; health interval=%ss",
        CHECK_INTERVAL_SECONDS,
    )
    try:
        yield
    finally:
        monitor.cancel()
        try:
            await monitor
        except asyncio.CancelledError:
            pass
        logger.info("NEXORA health monitor stopped")


app = FastAPI(title="NEXORA Gateway", version="1.1.0", lifespan=lifespan)


class TaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=4000)


@app.get("/health")
async def health():
    status = app.state.health
    if not status.get("ok"):
        raise HTTPException(status_code=503, detail=status)
    return status


@app.get("/api/status")
async def status():
    core = app.state.core
    return {
        "service": "nexora-fastapi-gateway",
        "core_module": core.__name__,
        "health": app.state.health,
        "monitor_interval_seconds": CHECK_INTERVAL_SECONDS,
        "monitor_running": not app.state.monitor_task.done(),
        "task_api_configured": bool(API_TOKEN),
        "database": str(core.DB.path),
    }


@app.get("/api/agents")
async def agents():
    records = await asyncio.to_thread(app.state.core.DB.agents)
    return {"agents": records, "count": len(records)}


@app.get("/api/stats")
async def stats():
    return await asyncio.to_thread(app.state.core.DB.stats)


@app.get("/api/tasks")
async def tasks():
    records = await asyncio.to_thread(app.state.core.DB.tasks)
    return {"tasks": records}


@app.get("/api/memory")
async def memories():
    records = await asyncio.to_thread(app.state.core.DB.memories)
    return {"memories": records}


@app.post("/api/task")
async def run_task(
    request: TaskRequest,
    authorization: str | None = Header(default=None),
):
    if not API_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Task API is disabled: configure NEXORA_API_TOKEN",
        )

    scheme, separator, supplied_token = (authorization or "").partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not hmac.compare_digest(supplied_token.strip(), API_TOKEN)
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")

    if not app.state.health.get("ok"):
        raise HTTPException(status_code=503, detail="NEXORA core health check is degraded")

    try:
        return await asyncio.to_thread(
            app.state.core.process_task, request.task.strip()
        )
    except Exception as exc:
        logger.exception("NEXORA task execution failed")
        raise HTTPException(
            status_code=500, detail="NEXORA task execution failed"
        ) from exc
