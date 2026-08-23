#!/usr/bin/env python3

import subprocess
import shlex
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class CommandGateway:
    """
    بوابة التنفيذ المركزية في NEXORA.

    الـBrain لا ينفذ أوامر مباشرة.
    يطلب تنفيذ Action، وهذه الطبقة تقرر هل يسمح بتنفيذه.
    """

    ALLOWED_COMMANDS = {
        "python",
        "python3",
        "pytest",
        "git",
        "grep",
        "sed",
        "cat",
        "ls",
        "pwd",
        "find",
    }

    BLOCKED_PATTERNS = (
        "rm -rf",
        "mkfs",
        "dd if=",
        "shutdown",
        "reboot",
        "passwd",
        "curl |",
        "wget |",
    )

    def __init__(self, workspace=None):
        self.workspace = Path(workspace or BASE_DIR).resolve()

    def validate(self, command):
        command = command.strip()

        if not command:
            return False, "empty_command"

        for pattern in self.BLOCKED_PATTERNS:
            if pattern in command:
                return False, f"blocked_pattern:{pattern}"

        try:
            parts = shlex.split(command)
        except ValueError as exc:
            return False, f"invalid_command:{exc}"

        if not parts:
            return False, "empty_command"

        executable = parts[0]

        if executable not in self.ALLOWED_COMMANDS:
            return False, f"command_not_allowed:{executable}"

        # منع shell operators حتى لا يتحول الأمر إلى سلسلة أوامر
        dangerous_tokens = {
            ";", "&&", "||", "|", ">", ">>", "<",
            "$(", "`"
        }

        if any(token in dangerous_tokens for token in parts):
            return False, "shell_operator_not_allowed"

        return True, "allowed"

    def execute(self, command, timeout=60):
        allowed, reason = self.validate(command)

        if not allowed:
            return {
                "status": "blocked",
                "command": command,
                "reason": reason,
            }

        try:
            result = subprocess.run(
                shlex.split(command),
                shell=False,
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "status": (
                    "success"
                    if result.returncode == 0
                    else "failed"
                ),
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout[-12000:],
                "stderr": result.stderr[-12000:],
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "command": command,
                "reason": "execution_timeout",
            }

        except Exception as exc:
            return {
                "status": "error",
                "command": command,
                "reason": str(exc),
            }


if __name__ == "__main__":
    gateway = CommandGateway()

    print(
        gateway.execute(
            "python3 -m py_compile nexora_unified.py"
        )
    )
