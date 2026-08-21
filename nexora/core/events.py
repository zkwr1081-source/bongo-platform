from dataclasses import dataclass, field
from typing import Any
import time, uuid

@dataclass
class Event:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: float = field(default_factory=time.time)
