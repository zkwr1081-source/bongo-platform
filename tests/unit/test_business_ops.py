from __future__ import annotations

import pytest

from business_ops import store


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
    with pytest.raises(ValueError, match="positive integer"):
        store.add_transaction(project["id"], "income", 0, "USD", db_path=db)


def test_missing_project_is_rejected(db):
    with pytest.raises(ValueError, match="does not exist"):
        store.add_transaction(999, "income", 100, "USD", db_path=db)
