"""Write tool - write files."""

import os
from pathlib import Path
from typing import Any

from .base import Tool


class WriteTool(Tool):
    """Write content to a file."""

    name = "write"
    description = "Write content to a file. Creates the file if it doesn't exist, overwrites if it does."

    @classmethod
    def parameters_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file",
                },
            },
            "required": ["file_path", "content"],
        }

    def execute(self, file_path: str, content: str, **kwargs) -> dict[str, Any]:
        """Write content to a file."""
        path = Path(file_path).resolve()

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            lines = content.count("\n") + 1 if content else 0
            return {
                "title": f"Write {file_path}",
                "output": f"Successfully wrote {lines} lines to {file_path}",
                "success": True,
            }
        except PermissionError:
            return {
                "title": f"Write {file_path}",
                "output": f"Error: Permission denied: {file_path}",
                "success": False,
            }
        except Exception as e:
            return {
                "title": f"Write {file_path}",
                "output": f"Error: {str(e)}",
                "success": False,
            }
