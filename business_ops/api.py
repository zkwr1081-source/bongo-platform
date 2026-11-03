"""Authenticated FastAPI interface for the NEXORA Business Operations MVP.
Run with: NEXORA_BUSINESS_API_KEY='<strong-secret>' uvicorn business_ops.api:app --host 127.0.0.1 --port 8094
"""
from __future__ import annotations

import os
import secrets
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from . import store

app = FastAPI(title="NEXORA Business Operations", version="0.1.0")


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    category: str = Field(default="digital", min_length=1, max_length=60)
    stage: Literal["idea", "validation", "build", "launch", "operating", "paused", "archived"] = "idea"


class ProjectStageInput(BaseModel):
    stage: Literal["idea", "validation", "build", "launch", "operating", "paused", "archived"]


class TransactionInput(BaseModel):
    project_id: int = Field(gt=0, le=store.MAX_SQLITE_INTEGER, strict=True)
    kind: Literal["income", "expense"]
    amount_minor: int = Field(gt=0, le=store.MAX_SQLITE_INTEGER, strict=True)
    currency: str = Field(min_length=3, max_length=3)
    status: Literal["pending", "collected", "void"] = "collected"
    source: str = Field(default="", max_length=160)
    transaction_date: str | None = None


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    configured = os.environ.get("NEXORA_BUSINESS_API_KEY", "")
    configured_bytes = configured.encode("utf-8")
    if len(configured_bytes) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API key is not configured; set NEXORA_BUSINESS_API_KEY to a secret of at least 32 UTF-8 bytes.",
        )
    if x_api_key is None or not secrets.compare_digest(x_api_key.encode("utf-8"), configured_bytes):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.on_event("startup")
def startup() -> None:
    store.init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "nexora-business-ops"}


@app.get("/api/projects", dependencies=[Depends(require_api_key)])
def projects() -> list[dict]:
    return store.list_projects()


@app.post("/api/projects", status_code=201, dependencies=[Depends(require_api_key)])
def create_project(payload: ProjectInput) -> dict:
    try:
        return store.create_project(payload.name, payload.description, payload.category, payload.stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise HTTPException(status_code=409, detail="Project name already exists") from exc
        raise


@app.patch("/api/projects/{project_id}/stage", dependencies=[Depends(require_api_key)])
def update_project_stage(project_id: int, payload: ProjectStageInput) -> dict:
    try:
        return store.update_project_stage(project_id, payload.stage)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/transactions", status_code=201, dependencies=[Depends(require_api_key)])
def create_transaction(payload: TransactionInput) -> dict:
    try:
        return store.add_transaction(payload.project_id, payload.kind, payload.amount_minor,
                                     payload.currency, payload.status, payload.source,
                                     payload.transaction_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/dashboard", dependencies=[Depends(require_api_key)])
def dashboard() -> dict:
    return store.dashboard()
