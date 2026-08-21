class Health:
    def __init__(self):
        self.components = {}

    def register(self, name, checker):
        self.components[name] = checker

    def check(self):
        result = {}
        for name, checker in self.components.items():
            try:
                result[name] = bool(checker())
            except Exception:
                result[name] = False
        return result
