import sqlite3
from pathlib import Path

class MemoryStore:
    def __init__(self, path):
        self.path = str(Path(path))

    def save(self, content):
        con = sqlite3.connect(self.path)
        con.execute(
            "INSERT INTO memories(content, created_at) VALUES(?, datetime('now'))",
            (content,),
        )
        con.commit()
        con.close()
