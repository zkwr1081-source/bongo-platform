from pathlib import Path
import json, threading

class MemoryStore:
    def __init__(self, path="data/memory/store.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def remember(self, key, value, tags=None):
        with self.lock:
            data = self._load()
            data.append({
                "key": key,
                "value": value,
                "tags": tags or []
            })
            self.path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    def search(self, query):
        query = query.lower()
        with self.lock:
            return [
                x for x in self._load()
                if query in str(x).lower()
            ][-50:]
