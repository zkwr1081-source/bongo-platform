from pathlib import Path
import json, time

class AuditLog:
    def __init__(self, path="data/logs/audit.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, action, actor="system", metadata=None):
        row = {
            "ts": time.time(),
            "actor": actor,
            "action": action,
            "metadata": metadata or {}
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row
