from .registry import ServiceRegistry
from .router import ServiceRouter
from .health import Health

class BongoRuntime:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.router = ServiceRouter(self.registry)
        self.health = Health(self.registry)

    def register(self, service):
        return self.registry.register(service)

    def status(self):
        return self.health.check()
