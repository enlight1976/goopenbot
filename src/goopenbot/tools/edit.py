"""Edit tool - edit files with diff."""

import re
from pathlib import Path
from typing import Any

from .base import Tool


class EditTool(Tool):
    """Edit a file by replacing specific text."""

    name = "edit"
    description = "Edit a file by replacing specific text with new text. Use this to modify existing files."

    @classmethod
    def parameters_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to edit",
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact text to find and replace",
                },
                "new_string": {
                    "type": "string",
                    "description": "The replacement text",
                },
            },
            "required": ["file_path", "old_string", "new_string"],
        }

    def execute(self, file_path: str, old_string: str, new_string: str, **kwargs) -> dict[str, Any]:
        """Edit a file by replacing text."""
        path = Path(file_path).resolve()

        if not path.exists():
            return {
                "title": f"Edit {file_path}",
                "output": f"Error: File not found: {file_path}",
                "success": False,
            }

        try:
            content = path.read_text(encoding="utf-8")

            if old_string not in content:
                return {
                    "title": f"Edit {file_path}",
                    "output": f"Error: String not found in file.\n\nExpected:\n{old_string}",
                    "success": False,
                }

            new_content = content.replace(old_string, new_string, 1)
            path.write_text(new_content, encoding="utf-8")

            return {
                "title": f"Edit {file_path}",
                "output": f"Successfully replaced:\n\n---\n{old_string}\n---\n\nwith:\n\n---\n{new_string}\n---",
                "success": True,
            }
        except UnicodeDecodeError:
            return {
                "title": f"Edit {file_path}",
                "output": "Error: Cannot edit binary file",
                "success": False,
            }
        except Exception as e:
            return {
                "title": f"Edit {file_path}",
                "output": f"Error: {str(e)}",
                "success": False,
            }
