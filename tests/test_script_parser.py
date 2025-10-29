"""
Unit tests for script parser
"""

import pytest
from src.core.script_parser import ScriptParser


@pytest.fixture
def config():
    """Sample configuration for testing."""
    return {
        'character': {'name': 'Vivienne Sterling'},
        'storage': {'cache_dir': './data/cache'}
    }


@pytest.fixture
def parser(config):
    """Create script parser instance."""
    return ScriptParser(config)


def test_parse_simple_script(parser):
    """Test parsing simple script without music cues."""
    script = "# Test Episode\n\nHello world. This is a test."
    result = parser.parse(script)
    
    assert result['metadata']['title'] == 'Test Episode'
    assert 'Hello world' in result['text']
    assert len(result['music_cues']) == 0


def test_parse_with_music_cues(parser):
    """Test parsing script with music cues."""
    script = """# Music Test
    
[MUSIC: upbeat intro]

Hello and welcome.

[MUSIC: soft background]

This is the main content.
"""
    result = parser.parse(script)
    
    assert len(result['music_cues']) == 2
    assert result['music_cues'][0]['description'] == 'upbeat intro'
    assert result['music_cues'][1]['description'] == 'soft background'
    assert '[MUSIC:' not in result['text']


def test_validate_empty_script(parser):
    """Test validation of empty script."""
    warnings = parser.validate_script("")
    assert len(warnings) > 0
    assert any('empty' in w.lower() for w in warnings)


def test_validate_long_script(parser):
    """Test validation of very long script."""
    long_script = "A" * 60000
    warnings = parser.validate_script(long_script)
    assert any('long' in w.lower() for w in warnings)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

