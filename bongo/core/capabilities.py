from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class Capability:
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

class CapabilityIndex:
    def __init__(self):
        self._index = {}

    def add(self, service_name, capability):
        self._index.setdefault(service_name, []).append(capability)

    def get(self, service_name):
        return self._index.get(service_name, [])

    def search(self, query):
        query = query.lower()
        results = []

        for service, capabilities in self._index.items():
            for capability in capabilities:
                text = " ".join([
                    capability.name,
                    capability.description,
                    " ".join(capability.tags)
                ]).lower()

                if query in text:
                    results.append({
                        "service": service,
                        "capability": capability.name,
                        "description": capability.description,
                        "tags": capability.tags
                    })

        return results
