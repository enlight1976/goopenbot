"""Tools for goopenbot."""

from .read import ReadTool
from .write import WriteTool
from .bash import BashTool
from .glob import GlobTool
from .grep import GrepTool
from .edit import EditTool

__all__ = [
    "ReadTool",
    "WriteTool",
    "BashTool",
    "GlobTool",
    "GrepTool",
    "EditTool",
]


def get_all_tools():
    """Get all available tools."""
    return [
        ReadTool,
        WriteTool,
        BashTool,
        GlobTool,
        GrepTool,
        EditTool,
    ]


def get_tool_by_name(name: str):
    """Get a tool by name."""
    tools = {tool.name: tool for tool in get_all_tools()}
    return tools.get(name)


def get_tools_schema():
    """Get OpenAI function calling schema for all tools."""
    return [tool.get_schema() for tool in get_all_tools()]
