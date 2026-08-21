from enum import Enum

class PluginState(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    DISABLED = "disabled"

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def install(self, name, plugin):
        self.plugins[name] = {
            "plugin": plugin,
            "state": PluginState.REGISTERED
        }

    def activate(self, name):
        item = self.plugins[name]
        item["state"] = PluginState.ACTIVE

        plugin = item["plugin"]
        hook = getattr(plugin, "on_activate", None)

        if hook:
            hook()

    def disable(self, name):
        item = self.plugins[name]
        item["state"] = PluginState.DISABLED

        plugin = item["plugin"]
        hook = getattr(plugin, "on_disable", None)

        if hook:
            hook()

    def status(self):
        return {
            name: item["state"].value
            for name, item in self.plugins.items()
        }
