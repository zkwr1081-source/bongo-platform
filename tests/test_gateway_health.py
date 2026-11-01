import sqlite3
from types import SimpleNamespace

import gateway


class Database:
    def __init__(self, path):
        self.path = str(path)

    def agents(self):
        return []

    def tasks(self):
        return []

    def memories(self):
        return []

    def stats(self):
        return {}


def make_core(database_path):
    connection = sqlite3.connect(database_path)
    for table in ("agents", "tasks", "memories", "events"):
        connection.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
    connection.commit()
    connection.close()

    return SimpleNamespace(
        __name__="nexora_unified",
        DB=Database(database_path),
        ACTION_ENGINE=object(),
        ANALYST_AGENT=object(),
        FUTURE_INTELLIGENCE_AGENT=object(),
        ORCHESTRATOR_AGENT=object(),
        VERIFY_AGENT=object(),
        UNIVERSAL_INTELLIGENCE_AGENT=object(),
        process_task=lambda task: {"status": "completed"},
    )


def test_health_check_confirms_core_files_exports_and_database(tmp_path, monkeypatch):
    for relative_path in ("nexora_unified.py", "action_engine.py"):
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# present\n", encoding="utf-8")

    monkeypatch.setattr(gateway, "ROOT", tmp_path)
    monkeypatch.setattr(gateway, "CORE_FILES", ("nexora_unified.py", "action_engine.py"))
    core = make_core(tmp_path / "nexora.db")

    result = gateway._perform_health_check(core)

    assert result["ok"] is True
    assert result["missing_files"] == []
    assert result["sqlite"]["missing_tables"] == []
    assert all(result["core_instances"].values())


def test_health_check_fails_when_required_database_table_is_missing(tmp_path, monkeypatch):
    target = tmp_path / "nexora_unified.py"
    target.write_text("# present\n", encoding="utf-8")
    monkeypatch.setattr(gateway, "ROOT", tmp_path)
    monkeypatch.setattr(gateway, "CORE_FILES", ("nexora_unified.py",))

    database_path = tmp_path / "incomplete.db"
    connection = sqlite3.connect(database_path)
    connection.execute("CREATE TABLE agents (id INTEGER PRIMARY KEY)")
    connection.commit()
    connection.close()

    core = SimpleNamespace(
        DB=Database(database_path),
        ACTION_ENGINE=object(),
        ANALYST_AGENT=object(),
        FUTURE_INTELLIGENCE_AGENT=object(),
        ORCHESTRATOR_AGENT=object(),
        VERIFY_AGENT=object(),
        UNIVERSAL_INTELLIGENCE_AGENT=object(),
        process_task=lambda task: None,
    )

    result = gateway._perform_health_check(core)

    assert result["ok"] is False
    assert set(result["sqlite"]["missing_tables"]) == {"tasks", "memories", "events"}
