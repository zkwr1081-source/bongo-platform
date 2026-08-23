from dataclasses import dataclass, field
from typing import Callable, Dict, Any

@dataclass
class Service:
    name: str
    category: str
    handler: Callable[..., Any]
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, Service] = {}

    def register(self, service: Service):
        if service.name in self._services:
            raise ValueError(f"Service already registered: {service.name}")
        self._services[service.name] = service
        return service

    def get(self, name: str):
        return self._services.get(name)

    def list(self):
        return list(self._services.values())

    def count(self):
        return len(self._services)

    def categories(self):
        return sorted(set(s.category for s in self._services.values()))
