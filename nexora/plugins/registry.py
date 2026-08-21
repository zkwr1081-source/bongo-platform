class PluginRegistry:
    def __init__(self):
        self.plugins = {}

    def register(self, name, plugin):
        if not name or plugin is None:
            raise ValueError("invalid plugin")
        self.plugins[name] = plugin

    def get(self, name):
        return self.plugins.get(name)

    def list(self):
        return sorted(self.plugins)
