"""
Comprehensive Unit Tests for Script Parser
Tests for src/core/script_parser.py - 100% coverage
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.script_parser import ScriptParser


class TestScriptParser:
    """Test ScriptParser class."""

    def test_init(self, test_config):
        """Test ScriptParser initialization."""
        parser = ScriptParser(test_config)
        assert parser.config == test_config
        assert parser.music_pattern is not None

    def test_parse_simple_script(self, test_config):
        """Test parsing a simple script."""
        parser = ScriptParser(test_config)

        script_text = """Hello world.

This is a test."""

        result = parser.parse(script_text)

        assert "text" in result
        assert "music_cues" in result
        assert "metadata" in result
        assert "Hello world" in result["text"]
        assert "This is a test" in result["text"]

    def test_parse_with_title(self, test_config):
        """Test parsing script with title (# prefix)."""
        parser = ScriptParser(test_config)

        script_text = """# My Podcast Title
This is the content."""

        result = parser.parse(script_text)

        assert result["metadata"]["title"] == "My Podcast Title"
        assert "This is the content" in result["text"]
        assert "# My Podcast Title" not in result["text"]

    def test_parse_without_title(self, test_config):
        """Test parsing script without title."""
        parser = ScriptParser(test_config)

        script_text = """No title here.
Just content."""

        result = parser.parse(script_text)

        assert result["metadata"]["title"] == "Untitled Podcast"
        assert "No title here" in result["text"]

    def test_parse_with_music_cue(self, test_config):
        """Test parsing script with music tags."""
        parser = ScriptParser(test_config)

        script_text = """Hello.

[MUSIC: calm background music]

Goodbye."""

        result = parser.parse(script_text)

        assert "text" in result
        assert "music_cues" in result
        assert len(result["music_cues"]) == 1
        assert result["music_cues"][0]["description"] == "calm background music"
        assert "[MUSIC:" not in result["text"]

    def test_parse_with_multiple_music_cues(self, test_config):
        """Test parsing with multiple music cues."""
        parser = ScriptParser(test_config)

        script_text = """Introduction.

[MUSIC: upbeat intro music]

Main content.

[MUSIC: dramatic transition]

Conclusion."""

        result = parser.parse(script_text)

        assert len(result["music_cues"]) == 2
        assert result["music_cues"][0]["description"] == "upbeat intro music"
        assert result["music_cues"][1]["description"] == "dramatic transition"
        assert result["metadata"]["music_cue_count"] == 2

    def test_parse_music_cue_inline(self, test_config):
        """Test music cue in middle of line."""
        parser = ScriptParser(test_config)

        script_text = """Hello [MUSIC: soft music] and goodbye."""

        result = parser.parse(script_text)

        assert len(result["music_cues"]) == 1
        assert result["music_cues"][0]["description"] == "soft music"
        assert "Hello" in result["text"]
        assert "and goodbye" in result["text"]
        assert "[MUSIC:" not in result["text"]

    def test_parse_empty_script(self, test_config):
        """Test parsing empty script."""
        parser = ScriptParser(test_config)

        result = parser.parse("")

        assert result["text"] == ""
        assert len(result["music_cues"]) == 0
        assert result["metadata"]["title"] == "Untitled Podcast"

    def test_parse_whitespace_only(self, test_config):
        """Test parsing script with only whitespace."""
        parser = ScriptParser(test_config)

        result = parser.parse("   \n\n   \n")

        assert result["text"] == ""
        assert len(result["music_cues"]) == 0

    def test_parse_metadata_character_count(self, test_config):
        """Test that character count is tracked."""
        parser = ScriptParser(test_config)

        script_text = """Hello world.
This is a test."""

        result = parser.parse(script_text)

        assert "character_count" in result["metadata"]
        assert result["metadata"]["character_count"] > 0

    def test_parse_music_cue_positions(self, test_config):
        """Test that music cue positions are tracked."""
        parser = ScriptParser(test_config)

        script_text = """First line.
[MUSIC: test]
Second line."""

        result = parser.parse(script_text)

        assert result["music_cues"][0]["position"] >= 0
        assert result["music_cues"][0]["timestamp"] is None

    def test_parse_from_file(self, test_config, temp_dir):
        """Test parsing script from file."""
        parser = ScriptParser(test_config)

        script_file = temp_dir / "test_script.txt"
        script_file.write_text("# Test Podcast\nHello world.")

        result = parser.parse_file(script_file)

        assert result["metadata"]["title"] == "Test Podcast"
        assert "Hello world" in result["text"]

    def test_parse_file_not_found(self, test_config):
        """Test parsing non-existent file."""
        parser = ScriptParser(test_config)

        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path("nonexistent_file.txt"))

    def test_parse_file_utf8(self, test_config, temp_dir):
        """Test parsing UTF-8 file with special characters."""
        parser = ScriptParser(test_config)

        script_file = temp_dir / "utf8_script.txt"
        script_file.write_text("Hello 世界 🎵", encoding="utf-8")

        result = parser.parse_file(script_file)

        assert "世界" in result["text"]
        assert "🎵" in result["text"]

    def test_validate_empty_script(self, test_config):
        """Test validation of empty script."""
        parser = ScriptParser(test_config)

        warnings = parser.validate_script("")

        assert len(warnings) > 0
        assert any("empty" in w.lower() for w in warnings)

    def test_validate_short_script(self, test_config):
        """Test validation of very short script."""
        parser = ScriptParser(test_config)

        warnings = parser.validate_script("Short")

        assert len(warnings) > 0
        assert any("short" in w.lower() for w in warnings)

    def test_validate_long_script(self, test_config):
        """Test validation of very long script."""
        parser = ScriptParser(test_config)

        long_script = "A" * 60000  # Over 50,000 characters
        warnings = parser.validate_script(long_script)

        assert len(warnings) > 0
        assert any("long" in w.lower() for w in warnings)

    def test_validate_normal_script(self, test_config):
        """Test validation of normal script."""
        parser = ScriptParser(test_config)

        normal_script = "Hello world. " * 100  # Normal length
        warnings = parser.validate_script(normal_script)

        assert len(warnings) == 0

    def test_parse_complex_script(self, test_config):
        """Test parsing complex script with all features."""
        parser = ScriptParser(test_config)

        script_text = """# Amazing Podcast

Welcome to the show!

[MUSIC: exciting intro music]

Today we're going to discuss something interesting.

[MUSIC: thoughtful background music]

And that's the end of our episode."""

        result = parser.parse(script_text)

        assert result["metadata"]["title"] == "Amazing Podcast"
        assert len(result["music_cues"]) == 2
        assert "Welcome to the show" in result["text"]
        assert result["metadata"]["character_count"] > 0
        assert result["metadata"]["music_cue_count"] == 2


@pytest.mark.parametrize(
    "script_text,expected_music_count",
    [
        ("No music here", 0),
        ("[MUSIC: test]", 1),
        ("[MUSIC: one] and [MUSIC: two]", 2),
        ("[MUSIC: a]\n[MUSIC: b]\n[MUSIC: c]", 3),
    ],
)
def test_music_cue_counts(test_config, script_text, expected_music_count):
    """Parametrized test for different music cue counts."""
    parser = ScriptParser(test_config)

    result = parser.parse(script_text)

    assert len(result["music_cues"]) == expected_music_count
    assert result["metadata"]["music_cue_count"] == expected_music_count


@pytest.mark.parametrize(
    "title_line,expected_title",
    [
        ("# My Title", "My Title"),
        ("# Another Title", "Another Title"),
        ("#NoSpace", "Untitled Podcast"),  # Without space after #, not recognized as title
        ("# Title With Spaces ", "Title With Spaces"),
    ],
)
def test_title_extraction(test_config, title_line, expected_title):
    """Parametrized test for title extraction."""
    parser = ScriptParser(test_config)

    result = parser.parse(f"{title_line}\nContent")

    assert result["metadata"]["title"] == expected_title
