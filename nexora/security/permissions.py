class PermissionEngine:
    def __init__(self):
        self.roles = {
            "system": {"*"},
            "orchestrator": {
                "task.execute",
                "memory.read",
                "memory.write",
                "tool.execute"
            },
            "guest": {
                "memory.read"
            }
        }

    def allowed(self, actor, permission):
        perms = self.roles.get(actor, set())
        return "*" in perms or permission in perms

    def require(self, actor, permission):
        if not self.allowed(actor, permission):
            raise PermissionError(
                f"permission denied: {actor} -> {permission}"
            )
        return True
