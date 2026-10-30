"""A bounded, auditable agent task runtime.

Planning is separated from side effects. This runtime has no shell, GitHub write,
deployment, payment, or external publishing capability.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
import urllib.request
import uuid
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Agent:
    agent_id: str
    name: str
    specialty: str
    system_prompt: str
    max_output_chars: int = 8000


@dataclass(frozen=True)
class Task:
    task_id: str
    agent_id: str
    instruction: str
    status: str = "queued"


@dataclass(frozen=True)
class TaskResult:
    task_id: str
    agent_id: str
    status: str
    output: str
    error: str = ""


class Provider(Protocol):
    def generate(self, system_prompt: str, instruction: str) -> str: ...


class MockProvider:
    """Predictable provider for offline tests and safe dry runs."""
    def generate(self, system_prompt: str, instruction: str) -> str:
        return "MOCK RESULT\\n" + instruction[:2000]


class OpenAICompatibleProvider:
    """Minimal OpenAI-compatible chat-completions client using stdlib only."""
    def __init__(self, base_url: str, model: str, api_key: str = "",
                 timeout: int = 45, max_response_bytes: int = 1_000_000):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = max(5, min(int(timeout), 120))
        self.max_response_bytes = max(1024, min(int(max_response_bytes), 5_000_000))

    def generate(self, system_prompt: str, instruction: str) -> str:
        url = self.base_url
        if not url.endswith("/chat/completions"):
            url += "/chat/completions"
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction},
            ],
            "temperature": 0.2,
        }).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key
        request = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            raw = response.read(self.max_response_bytes + 1)
        if len(raw) > self.max_response_bytes:
            raise ValueError("Provider response exceeded configured size limit")
        data = json.loads(raw.decode("utf-8"))
        return str(data["choices"][0]["message"]["content"])


DEFAULT_AGENTS = (
    Agent("scout-01", "راصد الاحتياجات", "research",
          "أنت باحث احتياجات. افصل الحقائق عن الفرضيات، واطلب أدلة قابلة للتحقق."),
    Agent("planner-01", "مخطط المشاريع", "planning",
          "أنت مخطط مشاريع. حوّل الهدف إلى خطوات ومخرجات ومخاطر قابلة للقياس."),
    Agent("engineer-01", "مهندس البرمجيات", "engineering",
          "أنت مهندس برمجيات. اقترح تغييرات صغيرة قابلة للاختبار ولا تدّع تنفيذها."),
    Agent("reviewer-01", "مراجع الجودة", "quality",
          "أنت مراجع مستقل. ابحث عن الثغرات والاختبارات الناقصة والافتراضات."),
    Agent("security-01", "مراجع الأمن", "security",
          "أنت مراجع أمن. امنع كشف الأسرار والبيانات الخاصة والعمليات غير المصرح بها."),
)


class AgentRuntime:
    """SQLite-backed task queue with bounded concurrency and an audit trail."""
    def __init__(self, db_path: str | Path, agents=DEFAULT_AGENTS,
                 provider: Provider | None = None, max_workers: int = 4,
                 max_tasks_per_batch: int = 20):
        self.db_path = str(db_path)
        agent_list = tuple(agents)
        self.agents = {a.agent_id: a for a in agent_list}
        if len(self.agents) != len(agent_list):
            raise ValueError("Agent IDs must be unique")
        self.provider = provider or MockProvider()
        self.max_workers = max(1, min(int(max_workers), 16))
        self.max_tasks_per_batch = max(1, min(int(max_tasks_per_batch), 100))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._database() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY, agent_id TEXT NOT NULL,
                instruction TEXT NOT NULL, status TEXT NOT NULL,
                output TEXT NOT NULL DEFAULT '', error TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL, updated_at REAL NOT NULL)""")

    def _connect(self):
        db = sqlite3.connect(self.db_path, timeout=15)
        db.row_factory = sqlite3.Row
        return db

    @contextmanager
    def _database(self):
        """Close every SQLite connection and commit/rollback its transaction."""
        db = self._connect()
        try:
            with db:
                yield db
        finally:
            db.close()

    def submit(self, agent_id: str, instruction: str) -> Task:
        if agent_id not in self.agents:
            raise KeyError("Unknown agent_id")
        instruction = instruction.strip()
        if not instruction or len(instruction) > 12000:
            raise ValueError("Instruction must contain 1..12000 characters")
        task_id, now = str(uuid.uuid4()), time.time()
        with self._database() as db:
            db.execute("INSERT INTO tasks(task_id,agent_id,instruction,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                       (task_id, agent_id, instruction, "queued", now, now))
        return Task(task_id, agent_id, instruction)

    def _run_one(self, task: Task) -> TaskResult:
        agent = self.agents[task.agent_id]
        try:
            output = str(self.provider.generate(agent.system_prompt, task.instruction))
            output = output[:agent.max_output_chars]
            status, error = "completed", ""
        except Exception as exc:
            output, status = "", "failed"
            error = type(exc).__name__ + ": task execution failed"
        with self._database() as db:
            db.execute("UPDATE tasks SET status=?,output=?,error=?,updated_at=? WHERE task_id=?",
                       (status, output, error, time.time(), task.task_id))
        return TaskResult(task.task_id, task.agent_id, status, output, error)

    def run_batch(self) -> list[TaskResult]:
        with self._database() as db:
            rows = db.execute("SELECT task_id,agent_id,instruction,status FROM tasks "
                              "WHERE status='queued' ORDER BY created_at LIMIT ?",
                              (self.max_tasks_per_batch,)).fetchall()
            tasks = [Task(r["task_id"], r["agent_id"], r["instruction"], r["status"]) for r in rows]
            for task in tasks:
                db.execute("UPDATE tasks SET status='running',updated_at=? WHERE task_id=? AND status='queued'",
                           (time.time(), task.task_id))
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(self._run_one, task) for task in tasks]
            for future in as_completed(futures):
                results.append(future.result())
        return sorted(results, key=lambda result: result.task_id)

    def get_task(self, task_id: str) -> dict | None:
        with self._database() as db:
            row = db.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return dict(row) if row else None


def provider_from_env() -> Provider:
    """Use mock by default; configure a compatible endpoint explicitly."""
    base = os.getenv("BONGO_AGENT_BASE_URL", "").strip()
    model = os.getenv("BONGO_AGENT_MODEL", "").strip()
    if not base or not model:
        return MockProvider()
    return OpenAICompatibleProvider(base, model, os.getenv("BONGO_AGENT_API_KEY", ""))
