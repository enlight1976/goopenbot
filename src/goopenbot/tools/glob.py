"""Glob tool - find files by pattern."""

import os
from pathlib import Path
from typing import Any

from .base import Tool


class GlobTool(Tool):
    """Find files matching a glob pattern."""

    name = "glob"
    description = "Find files matching a glob pattern. Useful for finding all files of a certain type or pattern."

    @classmethod
    def parameters_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The glob pattern to match (e.g., '**/*.py', 'src/**/*.ts')",
                },
                "path": {
                    "type": "string",
                    "description": "The directory to search in (defaults to current directory)",
                },
            },
            "required": ["pattern"],
        }

    def execute(self, pattern: str, path: str = ".", **kwargs) -> dict[str, Any]:
        """Find files matching a glob pattern."""
        try:
            search_path = Path(path).resolve()
            files = list(search_path.glob(pattern))

            if not files:
                return {
                    "title": f"glob: {pattern}",
                    "output": "No files found",
                    "success": True,
                }

            # Sort and format output
            relative_files = sorted([str(f.relative_to(search_path)) for f in files])
            output = "\n".join(relative_files)

            return {
                "title": f"glob: {pattern} ({len(files)} files)",
                "output": output,
                "success": True,
            }
        except Exception as e:
            return {
                "title": f"glob: {pattern}",
                "output": f"Error: {str(e)}",
                "success": False,
            }
