"""Read tool - read files."""

import os
from pathlib import Path
from typing import Any

from .base import Tool


class ReadTool(Tool):
    """Read a file or directory."""

    name = "read"
    description = "Read the contents of a file or directory. Use this to read files to understand code."

    @classmethod
    def parameters_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute or relative path to the file or directory to read",
                },
                "offset": {
                    "type": "integer",
                    "description": "Line offset to start reading from",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of lines to read",
                },
            },
            "required": ["file_path"],
        }

    def execute(self, file_path: str, offset: int = 0, limit: int = None, **kwargs) -> dict[str, Any]:
        """Read a file."""
        path = Path(file_path).resolve()

        if not path.exists():
            return {
                "title": f"Read {file_path}",
                "output": f"Error: File not found: {file_path}",
                "success": False,
            }

        if path.is_dir():
            try:
                items = list(path.iterdir())
                content = "\n".join([f"{item.name}/" if item.is_dir() else item.name for item in sorted(items)])
                return {
                    "title": f"Read {file_path}",
                    "output": content,
                    "success": True,
                }
            except PermissionError:
                return {
                    "title": f"Read {file_path}",
                    "output": f"Error: Permission denied: {file_path}",
                    "success": False,
                }

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if offset > 0:
                lines = lines[offset:]

            if limit is not None:
                lines = lines[:limit]

            content = "".join(lines)

            # Get file stats
            stats = path.stat()
            file_info = f"({len(lines)} lines, {stats.st_size} bytes)"

            return {
                "title": f"Read {file_path} {file_info}",
                "output": content,
                "success": True,
            }
        except UnicodeDecodeError:
            return {
                "title": f"Read {file_path}",
                "output": "Error: Cannot read binary file",
                "success": False,
            }
        except Exception as e:
            return {
                "title": f"Read {file_path}",
                "output": f"Error: {str(e)}",
                "success": False,
            }
