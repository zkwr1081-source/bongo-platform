from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from business_ops import api, store


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "business.sqlite3"
    store.init_db(path)
    return path


def test_project_creation_and_listing(db):
    created = store.create_project("AI Support SaaS", "Customer support automation", db_path=db)
    assert created["stage"] == "idea"
    assert store.list_projects(db)[0]["name"] == "AI Support SaaS"


def test_cash_dashboard_counts_collected_only_and_separates_currency(db):
    project = store.create_project("Micro SaaS", db_path=db)
    store.add_transaction(project["id"], "income", 12500, "USD", "collected", db_path=db)
    store.add_transaction(project["id"], "expense", 2500, "USD", "collected", db_path=db)
    store.add_transaction(project["id"], "income", 5000, "USD", "pending", db_path=db)
    store.add_transaction(project["id"], "income", 7000, "TRY", "collected", db_path=db)

    result = store.dashboard(db)
    assert result["projects_total"] == 1
    usd = next(item for item in result["cash_by_currency"] if item["currency"] == "USD")
    assert usd["collected_income_minor"] == 12500
    assert usd["collected_expense_minor"] == 2500
    assert usd["net_collected_minor"] == 10000
    assert "TRY" in {item["currency"] for item in result["cash_by_currency"]}
    assert result["pending_by_currency"][0]["pending_income_minor"] == 5000


@pytest.mark.parametrize("kind", ["transfer", "", "INCOME_INVALID"])
def test_invalid_transaction_kind_rejected(db, kind):
    project = store.create_project("Project", db_path=db)
    with pytest.raises(ValueError, match="kind"):
        store.add_transaction(project["id"], kind, 100, "USD", db_path=db)


def test_invalid_currency_and_amount_rejected(db):
    project = store.create_project("Project", db_path=db)
    with pytest.raises(ValueError, match="currency"):
        store.add_transaction(project["id"], "income", 100, "US", db_path=db)
    with pytest.raises(ValueError, match="positive integer|SQLite 64-bit"):
        store.add_transaction(project["id"], "income", 0, "USD", db_path=db)


def test_missing_project_is_rejected(db):
    with pytest.raises(ValueError, match="does not exist"):
        store.add_transaction(999, "income", 100, "USD", db_path=db)


def test_project_stage_can_advance_and_invalid_stage_is_rejected(db):
    project = store.create_project("Stage workflow", db_path=db)
    updated = store.update_project_stage(project["id"], "validation", db_path=db)
    assert updated["stage"] == "validation"
    with pytest.raises(ValueError, match="stage must be one of"):
        store.update_project_stage(project["id"], "unknown", db_path=db)
    with pytest.raises(ValueError, match="does not exist"):
        store.update_project_stage(999, "build", db_path=db)


def test_api_key_configuration_must_be_at_least_32_utf8_bytes(monkeypatch):
    for configured in ("", "short", "a" * 31):
        monkeypatch.setenv("NEXORA_BUSINESS_API_KEY", configured)
        with pytest.raises(HTTPException) as exc:
            api.require_api_key("any")
        assert exc.value.status_code == 503


def test_api_key_missing_or_mismatch_is_rejected(monkeypatch):
    secret = "x" * 32
    monkeypatch.setenv("NEXORA_BUSINESS_API_KEY", secret)
    with pytest.raises(HTTPException) as missing:
        api.require_api_key(None)
    assert missing.value.status_code == 401
    with pytest.raises(HTTPException) as mismatch:
        api.require_api_key("y" * 32)
    assert mismatch.value.status_code == 401


def test_api_key_match_is_accepted_and_unicode_secret_is_supported(monkeypatch):
    secret = "x" * 32
    monkeypatch.setenv("NEXORA_BUSINESS_API_KEY", secret)
    assert api.require_api_key(secret) is None

    unicode_secret = "é" * 16  # exactly 32 UTF-8 bytes
    monkeypatch.setenv("NEXORA_BUSINESS_API_KEY", unicode_secret)
    assert api.require_api_key(unicode_secret) is None


def test_api_model_rejects_bool_and_out_of_range_sqlite_integers():
    base = {"kind": "income", "currency": "USD"}
    with pytest.raises(ValidationError):
        api.TransactionInput(project_id=True, amount_minor=100, **base)
    with pytest.raises(ValidationError):
        api.TransactionInput(project_id=1, amount_minor=store.MAX_SQLITE_INTEGER + 1, **base)
    with pytest.raises(ValidationError):
        api.TransactionInput(project_id=store.MAX_SQLITE_INTEGER + 1, amount_minor=100, **base)


def test_store_rejects_out_of_range_sqlite_integer_inputs(db):
    project = store.create_project("Integer bounds", db_path=db)
    with pytest.raises(ValueError, match="SQLite 64-bit"):
        store.add_transaction(project["id"], "income", store.MAX_SQLITE_INTEGER + 1, "USD", db_path=db)
    with pytest.raises(ValueError, match="SQLite 64-bit"):
        store.add_transaction(store.MAX_SQLITE_INTEGER + 1, "income", 100, "USD", db_path=db)
    with pytest.raises(ValueError, match="SQLite 64-bit"):
        store.update_project_stage(store.MAX_SQLITE_INTEGER + 1, "build", db_path=db)



def test_app_lifespan_initializes_store_once(monkeypatch):
    calls = 0

    def fake_init_db():
        nonlocal calls
        calls += 1

    monkeypatch.setattr(api.store, "init_db", fake_init_db)

    async def exercise_lifespan():
        async with api.lifespan(api.app):
            assert calls == 1
        assert calls == 1

    asyncio.run(exercise_lifespan())
