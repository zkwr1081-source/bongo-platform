from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    handler: object
    description: str = ""
    permissions: tuple = ()

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool):
        if not isinstance(tool, Tool):
            raise TypeError("tool must be Tool")
        self.tools[tool.name] = tool

    def get(self, name):
        return self.tools.get(name)

    def execute(self, name, *args, **kwargs):
        tool = self.get(name)
        if not tool:
            raise KeyError(f"tool not found: {name}")
        return tool.handler(*args, **kwargs)

    def list(self):
        return sorted(self.tools)
