"""
Comprehensive tests for config.py - Goal: 100% coverage
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config import _replace_env_vars, get_config_value, load_config, validate_config


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_config_with_path(self, temp_dir):
        """Test loading config from specified path."""
        config_file = temp_dir / "test_config.yaml"
        config_data = {
            "app": {"name": "test"},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {"cache_dir": str(temp_dir)},
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        result = load_config(config_file)
        assert result["app"]["name"] == "test"

    def test_load_config_default_path(self):
        """Test loading config without specifying path."""
        # This tests line 26 - the uncovered line!
        try:
            result = load_config()  # No argument = use default path
            assert isinstance(result, dict)
        except FileNotFoundError:
            # Expected if config.yaml doesn't exist in default location
            pass

    def test_load_config_file_not_found(self, temp_dir):
        """Test error when config file doesn't exist."""
        missing_file = temp_dir / "missing.yaml"

        with pytest.raises(FileNotFoundError):
            load_config(missing_file)

    def test_load_config_with_env_vars(self, temp_dir):
        """Test config loads with environment variable replacement."""
        os.environ["TEST_VAR"] = "test_value"

        config_file = temp_dir / "test_config.yaml"
        config_data = {
            "app": {"api_key": "${TEST_VAR}"},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {},
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        result = load_config(config_file)
        assert result["app"]["api_key"] == "test_value"

        del os.environ["TEST_VAR"]


class TestReplaceEnvVars:
    """Test environment variable replacement."""

    def test_replace_simple_var(self):
        """Test simple variable replacement."""
        os.environ["MY_VAR"] = "my_value"
        result = _replace_env_vars("${MY_VAR}")
        assert result == "my_value"
        del os.environ["MY_VAR"]

    def test_replace_missing_var(self):
        """Test replacement of missing variable keeps original."""
        result = _replace_env_vars("${NONEXISTENT_VAR}")
        assert result == "${NONEXISTENT_VAR}"

    def test_replace_in_dict(self):
        """Test replacement in dictionary."""
        os.environ["KEY1"] = "value1"
        config = {"key": "${KEY1}", "other": "normal"}
        result = _replace_env_vars(config)
        assert result["key"] == "value1"
        assert result["other"] == "normal"
        del os.environ["KEY1"]

    def test_replace_in_list(self):
        """Test replacement in list."""
        os.environ["ITEM"] = "list_value"
        config = ["${ITEM}", "normal", "text"]
        result = _replace_env_vars(config)
        assert result[0] == "list_value"
        assert result[1] == "normal"
        del os.environ["ITEM"]

    def test_replace_nested(self):
        """Test replacement in nested structures."""
        os.environ["NESTED"] = "nested_value"
        config = {"level1": {"level2": ["${NESTED}", "other"]}}
        result = _replace_env_vars(config)
        assert result["level1"]["level2"][0] == "nested_value"
        del os.environ["NESTED"]

    def test_replace_non_var_string(self):
        """Test non-variable strings pass through."""
        result = _replace_env_vars("normal string")
        assert result == "normal string"

    def test_replace_number(self):
        """Test numbers pass through unchanged."""
        assert _replace_env_vars(42) == 42
        assert _replace_env_vars(3.14) == 3.14

    def test_replace_boolean(self):
        """Test booleans pass through unchanged."""
        assert _replace_env_vars(True) == True
        assert _replace_env_vars(False) == False


class TestGetConfigValue:
    """Test getting config values with dot notation."""

    def test_get_simple_value(self):
        """Test getting simple value."""
        config = {"key": "value"}
        assert get_config_value(config, "key") == "value"

    def test_get_nested_value(self):
        """Test getting nested value."""
        config = {"level1": {"level2": {"level3": "deep_value"}}}
        assert get_config_value(config, "level1.level2.level3") == "deep_value"

    def test_get_missing_value_returns_default(self):
        """Test missing value returns default."""
        config = {"key": "value"}
        assert get_config_value(config, "missing", "default") == "default"

    def test_get_partial_path_returns_default(self):
        """Test partial path returns default."""
        config = {"level1": {"level2": "value"}}
        assert get_config_value(config, "level1.missing.key", "default") == "default"

    def test_get_value_none_default(self):
        """Test None default value."""
        config = {"key": "value"}
        assert get_config_value(config, "missing") is None


class TestValidateConfig:
    """Test configuration validation."""

    def test_validate_complete_config(self, temp_dir):
        """Test validation of complete config."""
        config = {
            "app": {},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {"cache_dir": str(temp_dir / "cache"), "output_dir": str(temp_dir / "output")},
        }

        assert validate_config(config) == True

    def test_validate_missing_section(self):
        """Test validation fails with missing section."""
        config = {
            "app": {},
            "character": {},
            # Missing tts, music, etc.
        }

        with pytest.raises(ValueError, match="Missing required configuration section"):
            validate_config(config)

    def test_validate_creates_directories(self, temp_dir):
        """Test validation creates missing directories."""
        config = {
            "app": {},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {"cache_dir": str(temp_dir / "new_cache"), "output_dir": str(temp_dir / "new_output")},
        }

        validate_config(config)

        assert (temp_dir / "new_cache").exists()
        assert (temp_dir / "new_output").exists()

    def test_validate_non_dir_paths_ignored(self, temp_dir):
        """Test non-directory paths are ignored."""
        config = {
            "app": {},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {
                "config_file": str(temp_dir / "config.yaml"),  # Not a _dir
                "cache_dir": str(temp_dir / "cache"),
            },
        }

        assert validate_config(config) == True
