"""Base tool class."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Tool(ABC):
    """Base class for all tools."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the tool with given arguments."""
        pass

    @classmethod
    def get_schema(cls) -> dict[str, Any]:
        """Get the OpenAI function calling schema for this tool."""
        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": cls.parameters_schema(),
            },
        }

    @classmethod
    def parameters_schema(cls) -> dict[str, Any]:
        """Get the parameters schema. Override in subclass."""
        return {"type": "object", "properties": {}, "required": []}
