from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

class TaskState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class Task:
    goal: str
    agent: str = "orchestrator"
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    state: TaskState = TaskState.CREATED
    result: object = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def transition(self, state):
        self.state = state
        self.updated_at = time.time()
