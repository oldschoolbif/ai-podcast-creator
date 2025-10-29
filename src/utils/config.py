"""
Configuration management for AI Podcast Creator
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, uses default config.yaml
        
    Returns:
        Dictionary containing configuration
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Replace environment variable placeholders
    config = _replace_env_vars(config)
    
    return config


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
    keys = path.split('.')
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
    required_sections = ['app', 'character', 'tts', 'music', 'avatar', 'video', 'storage']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate paths exist or can be created
    storage = config.get('storage', {})
    for key, path in storage.items():
        if key.endswith('_dir'):
            path_obj = Path(path)
            if not path_obj.exists():
                path_obj.mkdir(parents=True, exist_ok=True)
    
    return True

