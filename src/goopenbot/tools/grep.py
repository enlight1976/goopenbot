"""Grep tool - search for text in files."""

import re
from pathlib import Path
from typing import Any

from .base import Tool


class GrepTool(Tool):
    """Search for text patterns in files."""

    name = "grep"
    description = "Search for text patterns in files. Useful for finding function definitions, imports, or any code pattern."

    @classmethod
    def parameters_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The text pattern or regex to search for",
                },
                "path": {
                    "type": "string",
                    "description": "The directory or file to search in (defaults to current directory)",
                },
                "ignore_case": {
                    "type": "boolean",
                    "description": "Whether to ignore case when searching (default: false)",
                },
                "regex": {
                    "type": "boolean",
                    "description": "Whether to treat the pattern as a regex (default: true)",
                },
            },
            "required": ["pattern"],
        }

    def execute(
        self,
        pattern: str,
        path: str = ".",
        ignore_case: bool = False,
        regex: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """Search for a pattern in files."""
        try:
            search_path = Path(path).resolve()

            if not search_path.exists():
                return {
                    "title": f"grep: {pattern}",
                    "output": f"Error: Path not found: {path}",
                    "success": False,
                }

            # Compile regex
            flags = re.IGNORECASE if ignore_case else 0
            try:
                if regex:
                    pattern_obj = re.compile(pattern, flags)
                else:
                    pattern_obj = re.compile(re.escape(pattern), flags)
            except re.error as e:
                return {
                    "title": f"grep: {pattern}",
                    "output": f"Error: Invalid regex: {e}",
                    "success": False,
                }

            matches = []
            files_to_search = [search_path] if search_path.is_file() else list(search_path.rglob("*"))

            for file_path in files_to_search:
                if not file_path.is_file():
                    continue
                # Skip binary files
                if b"\x00" in file_path.read_bytes()[:1024]:
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    for line_num, line in enumerate(content.split("\n"), 1):
                        if pattern_obj.search(line):
                            matches.append(
                                f"{file_path}:{line_num}: {line.rstrip()}"
                            )
                except (UnicodeDecodeError, PermissionError):
                    continue

            if not matches:
                return {
                    "title": f"grep: {pattern}",
                    "output": "No matches found",
                    "success": True,
                }

            # Limit output
            output = "\n".join(matches[:100])
            if len(matches) > 100:
                output += f"\n... and {len(matches) - 100} more matches"

            return {
                "title": f"grep: {pattern} ({len(matches)} matches)",
                "output": output,
                "success": True,
            }
        except Exception as e:
            return {
                "title": f"grep: {pattern}",
                "output": f"Error: {str(e)}",
                "success": False,
            }
