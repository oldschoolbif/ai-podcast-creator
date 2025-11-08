"""
Configuration management for AI Podcast Creator
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    If a custom config_path is provided, it will be merged with the base config.yaml
    (custom config overrides base config values).

    Args:
        config_path: Path to config file. If None, uses default config.yaml
                    If provided, merges with base config.yaml

    Returns:
        Dictionary containing configuration
    """
    # Always load base config first
    base_config_path = Path(__file__).parent.parent.parent / "config.yaml"
    if not base_config_path.exists():
        raise FileNotFoundError(f"Base configuration file not found: {base_config_path}")

    with open(base_config_path, "r", encoding="utf-8") as f:
        base_config = yaml.safe_load(f)

    # If custom config provided, merge it with base config
    if config_path is not None:
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            custom_config = yaml.safe_load(f)
        
        # Handle empty YAML (returns None)
        if custom_config is None:
            custom_config = {}
        
        # Deep merge custom config into base config
        config = _deep_merge(base_config, custom_config)
    else:
        config = base_config

    # Replace environment variable placeholders
    config = _replace_env_vars(config)

    return config  # type: ignore[no-any-return]


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with override values taking precedence.

    Args:
        base: Base dictionary
        override: Override dictionary (values take precedence)

    Returns:
        Merged dictionary
    """
    # Handle None override (empty YAML)
    if override is None:
        return base
    
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _deep_merge(result[key], value)
        else:
            # Override with new value
            result[key] = value
    
    return result


def _replace_env_vars(config: Any) -> Any:
    """
    Recursively replace ${VAR_NAME} with environment variable values.

    Args:
        config: Configuration dictionary or value

    Returns:
        Configuration with environment variables replaced
    """
    if isinstance(config, dict):
        return {key: _replace_env_vars(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [_replace_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        var_name = config[2:-1]
        return os.getenv(var_name, config)
    else:
        return config


def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation.

    Args:
        config: Configuration dictionary
        path: Dot-separated path (e.g., "tts.coqui.temperature")
        default: Default value if path not found

    Returns:
        Configuration value or default

    Example:
        >>> config = load_config()
        >>> temp = get_config_value(config, "tts.coqui.temperature", 0.7)
    """
    keys = path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and required fields.

    Args:
        config: Configuration dictionary

    Returns:
        True if valid, raises exception otherwise
    """
    required_sections = ["app", "character", "tts", "music", "avatar", "video", "storage"]

    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")

    # Validate paths exist or can be created
    storage = config.get("storage", {})
    for key, path in storage.items():
        if key.endswith("_dir"):
            path_obj = Path(path)
            if not path_obj.exists():
                path_obj.mkdir(parents=True, exist_ok=True)

    return True
