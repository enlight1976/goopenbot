"""Core modules for goopenbot."""

from .config import Config, get_config_dir, get_data_dir, load_config, save_config

__all__ = ["Config", "get_config_dir", "get_data_dir", "load_config", "save_config"]
