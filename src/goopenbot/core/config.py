"""Configuration management for goopenbot."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class ProviderConfig(BaseModel):
    """Ollama provider configuration."""

    base_url: str = "http://localhost:11434/v1"
    model: str = "qwen2.5-coder:7b"
    api_key: Optional[str] = None


class ToolConfig(BaseModel):
    """Tool configuration."""

    allowed_commands: list[str] = ["*"]
    denied_commands: list[str] = []


class AgentConfig(BaseModel):
    """Default agent configuration."""

    model: str = "qwen2.5-coder:7b"
    tools: list[str] = ["read", "write", "bash", "glob", "grep"]
    max_iterations: int = 100


class Config(BaseModel):
    """Main configuration for goopenbot."""

    provider: ProviderConfig = ProviderConfig()
    tools: ToolConfig = ToolConfig()
    agent: AgentConfig = AgentConfig()


def get_project_dir() -> Path:
    """Get the project directory (where goopenbot.py is located)."""
    return Path(__file__).parent.parent.parent


def get_config_dir() -> Path:
    """Get the configuration directory (project directory)."""
    return get_project_dir()


def get_data_dir() -> Path:
    """Get the data directory for sessions (project directory)."""
    data_dir = get_project_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def load_config() -> Config:
    """Load configuration from file or return defaults."""
    # Check current directory first
    local_config = Path("goopenbot.json")
    if local_config.exists():
        with open(local_config) as f:
            data = json.load(f)
            return Config(**data)

    # Check project directory
    config_file = get_config_dir() / "goopenbot.json"
    if config_file.exists():
        with open(config_file) as f:
            data = json.load(f)
            return Config(**data)

    return Config()


def save_config(config: Config) -> None:
    """Save configuration to file."""
    config_file = get_config_dir() / "goopenbot.json"
    with open(config_file, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
