#!/usr/bin/env python3

from command_gateway import CommandGateway


class ActionEngine:
    """
    طبقة بين Brain و CommandGateway.

    Brain يطلب Action.
    ActionEngine يحوله إلى أمر مسموح.
    CommandGateway هو الحاجز النهائي قبل التنفيذ.
    """

    def __init__(self, workspace=None):
        self.gateway = CommandGateway(workspace)

    def execute_action(self, action):
        if not isinstance(action, dict):
            return {
                "status": "blocked",
                "reason": "invalid_action"
            }

        action_type = action.get("type")

        if action_type != "shell":
            return {
                "status": "blocked",
                "reason": "unsupported_action_type"
            }

        command = str(action.get("command", "")).strip()

        if not command:
            return {
                "status": "blocked",
                "reason": "command_required"
            }

        return self.gateway.execute(command)


if __name__ == "__main__":
    engine = ActionEngine()

    print(
        engine.execute_action({
            "type": "shell",
            "command": "pwd"
        })
    )
