class Health:
    def __init__(self, registry):
        self.registry = registry

    def check(self):
        return {
            "status": "ok",
            "services": self.registry.count(),
            "categories": self.registry.categories(),
        }
