from dataclasses import dataclass

@dataclass(frozen=True)
class Policy:
    allow_network: bool = True
    allow_tools: bool = True
    max_steps: int = 32
    require_audit: bool = True

DEFAULT_POLICY = Policy()
