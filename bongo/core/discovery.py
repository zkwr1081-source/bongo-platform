class ServiceDiscovery:
    def __init__(self, registry, capabilities):
        self.registry = registry
        self.capabilities = capabilities

    def discover(self, query):
        results = self.capabilities.search(query)

        if results:
            return results

        query = query.lower()

        return [
            {
                "service": service.name,
                "category": service.category,
                "description": service.description
            }
            for service in self.registry.list()
            if query in service.name.lower()
            or query in service.category.lower()
            or query in service.description.lower()
        ]
