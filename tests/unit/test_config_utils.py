"""
Comprehensive Unit Tests for Config Utils
Tests for src/utils/config.py - Aiming for 100% coverage
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
    """Test config loading functionality."""

    def test_load_valid_yaml(self, temp_dir):
        """Test loading valid YAML config."""
        config_data = {
            "app": {"name": "Test"},
            "character": {},
            "tts": {"engine": "gtts"},
            "music": {"engine": "musicgen"},
            "avatar": {},
            "video": {},
            "storage": {"output_dir": str(temp_dir / "output")},
        }

        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        result = load_config(config_file)

        assert result["tts"]["engine"] == "gtts"
        assert "app" in result

    def test_load_nonexistent_file(self, temp_dir):
        """Test loading non-existent config file."""
        nonexistent = temp_dir / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_config(nonexistent)

    def test_load_invalid_yaml(self, temp_dir):
        """Test loading invalid YAML."""
        config_file = temp_dir / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            load_config(config_file)

    def test_load_empty_yaml(self, temp_dir):
        """Test loading empty YAML file."""
        config_file = temp_dir / "empty.yaml"
        config_file.write_text("")

        result = load_config(config_file)

        # Empty YAML returns base config (empty YAML is treated as no overrides)
        assert result is not None
        assert isinstance(result, dict)
        # Should have base config structure
        assert "tts" in result
        assert "avatar" in result

    def test_load_with_env_vars(self, temp_dir):
        """Test loading with environment variable replacement."""
        config_data = {
            "app": {"name": "${TEST_APP_NAME}"},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {"output_dir": str(temp_dir)},
        }

        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Set environment variable
        os.environ["TEST_APP_NAME"] = "MyApp"

        result = load_config(config_file)

        assert result["app"]["name"] == "MyApp"

        # Cleanup
        del os.environ["TEST_APP_NAME"]


class TestReplaceEnvVars:
    """Test environment variable replacement."""

    def test_replace_single_var(self):
        """Test replacing single environment variable."""
        os.environ["TEST_VAR"] = "test_value"

        config = {"key": "${TEST_VAR}"}
        result = _replace_env_vars(config)

        assert result["key"] == "test_value"

        del os.environ["TEST_VAR"]

    def test_replace_nested_vars(self):
        """Test replacing nested environment variables."""
        os.environ["TEST_NESTED"] = "nested_value"

        config = {"level1": {"level2": "${TEST_NESTED}"}}
        result = _replace_env_vars(config)

        assert result["level1"]["level2"] == "nested_value"

        del os.environ["TEST_NESTED"]

    def test_replace_in_list(self):
        """Test replacing variables in lists."""
        os.environ["TEST_LIST"] = "list_value"

        config = {"items": ["${TEST_LIST}", "static"]}
        result = _replace_env_vars(config)

        assert result["items"][0] == "list_value"
        assert result["items"][1] == "static"

        del os.environ["TEST_LIST"]

    def test_replace_undefined_var(self):
        """Test that undefined variables are left as-is."""
        config = {"key": "${UNDEFINED_VAR}"}
        result = _replace_env_vars(config)

        # Should keep original if not found
        assert result["key"] == "${UNDEFINED_VAR}"

    def test_replace_non_string_values(self):
        """Test that non-string values are preserved."""
        config = {"int": 42, "float": 3.14, "bool": True, "none": None}
        result = _replace_env_vars(config)

        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["bool"] == True
        assert result["none"] is None


class TestValidateConfig:
    """Test config validation."""

    def test_validate_valid_config(self, temp_dir):
        """Test validation of valid config."""
        config = {
            "app": {},
            "character": {},
            "tts": {"engine": "gtts"},
            "music": {"engine": "musicgen"},
            "avatar": {"engine": "sadtalker"},
            "video": {},
            "storage": {"output_dir": str(temp_dir / "output"), "cache_dir": str(temp_dir / "cache")},
        }

        result = validate_config(config)

        assert result == True

    def test_validate_missing_required_keys(self):
        """Test validation with missing required keys."""
        config = {
            "tts": {"engine": "gtts"}
            # Missing app, character, music, avatar, video, storage sections
        }

        with pytest.raises(ValueError) as exc_info:
            validate_config(config)

        assert "Missing required configuration section" in str(exc_info.value)

    def test_validate_creates_directories(self, temp_dir):
        """Test that validation creates missing directories."""
        output_dir = temp_dir / "new_output"
        cache_dir = temp_dir / "new_cache"

        config = {
            "app": {},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {"output_dir": str(output_dir), "cache_dir": str(cache_dir)},
        }

        validate_config(config)

        assert output_dir.exists()
        assert cache_dir.exists()

    def test_validate_non_dir_paths_ignored(self, temp_dir):
        """Test that non-directory paths are ignored."""
        config = {
            "app": {},
            "character": {},
            "tts": {},
            "music": {},
            "avatar": {},
            "video": {},
            "storage": {
                "output_dir": str(temp_dir),
                "config_file": str(temp_dir / "config.yaml"),  # Not ending with _dir
            },
        }

        result = validate_config(config)

        assert result == True


class TestGetConfigValue:
    """Test getting config values using dot notation."""

    def test_get_simple_value(self):
        """Test getting simple config value."""
        config = {"tts": {"engine": "gtts", "gtts_tld": "com"}}

        result = get_config_value(config, "tts.engine")

        assert result == "gtts"

    def test_get_nested_value(self):
        """Test getting deeply nested value."""
        config = {"avatar": {"sadtalker": {"checkpoint": {"path": "/models/sadtalker.pth"}}}}

        result = get_config_value(config, "avatar.sadtalker.checkpoint.path")

        assert result == "/models/sadtalker.pth"

    def test_get_missing_value_returns_default(self):
        """Test that missing values return default."""
        config = {"tts": {"engine": "gtts"}}

        result = get_config_value(config, "tts.missing_key", default="default_value")

        assert result == "default_value"

    def test_get_missing_section_returns_default(self):
        """Test that missing sections return default."""
        config = {"tts": {}}

        result = get_config_value(config, "missing.section.key", default=None)

        assert result is None

    def test_get_top_level_value(self):
        """Test getting top-level value."""
        config = {"debug": True}

        result = get_config_value(config, "debug")

        assert result == True

    def test_get_value_with_non_dict_intermediate(self):
        """Test that non-dict intermediate values return default."""
        config = {"tts": {"engine": "gtts"}}  # This is a string, not a dict

        # Try to access tts.engine.something
        result = get_config_value(config, "tts.engine.something", default="fallback")

        assert result == "fallback"


@pytest.mark.parametrize(
    "path,expected",
    [
        ("tts.engine", "gtts"),
        ("music.engine", "musicgen"),
        ("storage.output_dir", "/tmp/output"),
        ("missing.key", None),
    ],
)
def test_get_config_value_parametrized(path, expected):
    """Parametrized test for get_config_value."""
    config = {"tts": {"engine": "gtts"}, "music": {"engine": "musicgen"}, "storage": {"output_dir": "/tmp/output"}}

    result = get_config_value(config, path, default=None)

    assert result == expected
