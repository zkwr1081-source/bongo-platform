class ServiceRouter:
    def __init__(self, registry):
        self.registry = registry

    def dispatch(self, service_name, **kwargs):
        service = self.registry.get(service_name)
        if not service:
            raise KeyError(f"Unknown service: {service_name}")
        return service.handler(**kwargs)
