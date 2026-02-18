"""Bash tool - execute shell commands."""

import asyncio
import os
import shlex
import subprocess
from typing import Any

from .base import Tool


class BashTool(Tool):
    """Execute shell commands."""

    name = "bash"
    description = "Execute a shell command and return its output. Use this to run git, npm, python, and other shell commands."

    @classmethod
    def parameters_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
                "description": {
                    "type": "string",
                    "description": "Description of what this command does",
                },
            },
            "required": ["command"],
        }

    def execute(self, command: str, description: str = "", **kwargs) -> dict[str, Any]:
        """Execute a shell command."""
        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )

            output = process.stdout
            if process.stderr:
                output += f"\n[stderr] {process.stderr}"

            if process.returncode != 0:
                output = f"[exit code: {process.returncode}]\n{output}"

            return {
                "title": description or f"bash: {command[:50]}...",
                "output": output,
                "success": process.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "title": description or f"bash: {command[:50]}...",
                "output": "Error: Command timed out after 60 seconds",
                "success": False,
            }
        except Exception as e:
            return {
                "title": description or f"bash: {command[:50]}...",
                "output": f"Error: {str(e)}",
                "success": False,
            }
