from bongo.core.capabilities import Capability, CapabilityIndex
from bongo.core.discovery import ServiceDiscovery

class IntegrationLayer:
    def __init__(self, runtime):
        self.runtime = runtime
        self.capabilities = CapabilityIndex()
        self.discovery = ServiceDiscovery(
            runtime.registry,
            self.capabilities
        )

    def register_service_capability(
        self,
        service_name,
        name,
        description,
        tags=None,
        input_schema=None,
        output_schema=None
    ):
        if not self.runtime.registry.get(service_name):
            raise KeyError(service_name)

        capability = Capability(
            name=name,
            description=description,
            tags=tags or [],
            input_schema=input_schema or {},
            output_schema=output_schema or {}
        )

        self.capabilities.add(service_name, capability)
        return capability

    def execute(self, service_name, **kwargs):
        return self.runtime.router.dispatch(
            service_name,
            **kwargs
        )

    def find(self, query):
        return self.discovery.discover(query)
