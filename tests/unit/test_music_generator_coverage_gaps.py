"""
Additional tests for music_generator.py to improve coverage from 74.07% to 80%+

Focus on uncovered code paths:
- generate() edge cases: list input with dict, empty list, None input
- _generate_mubert: TODO implementation path
- _select_from_library: TODO implementation path
- _get_cache_key: Cache key generation
- Error handling edge cases
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.music_generator import MusicGenerator


@pytest.fixture
def test_config(tmp_path):
    """Create test configuration."""
    return {
        "music": {
            "engine": "musicgen",
            "musicgen": {
                "model": "facebook/musicgen-small",
                "duration": 10,
            },
        },
        "storage": {"cache_dir": str(tmp_path / "cache")},
    }


class TestGenerateEdgeCases:
    """Test generate() method edge cases."""

    def test_generate_with_list_dict_input(self, test_config, tmp_path):
        """Test generate() with list containing dict."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        # Mock model
        generator.model = MagicMock()

        # Input is list with dict
        music_input = [{"description": "calm background music"}]

        with (
            patch.object(generator, "_generate_musicgen") as mock_gen,
            patch("pathlib.Path.exists", return_value=False),  # Not cached
        ):
            mock_gen.return_value = tmp_path / "output.wav"

            result = generator.generate(music_input)

            # Should extract description from dict
            mock_gen.assert_called_once()
            call_args = mock_gen.call_args[0]
            assert "calm background music" in call_args[0] or call_args[0] == "calm background music"

    def test_generate_with_list_string_input(self, test_config, tmp_path):
        """Test generate() with list containing string."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        # Mock model
        generator.model = MagicMock()

        # Input is list with string
        music_input = ["calm background music"]

        with (
            patch.object(generator, "_generate_musicgen") as mock_gen,
            patch("pathlib.Path.exists", return_value=False),  # Not cached
        ):
            mock_gen.return_value = tmp_path / "output.wav"

            result = generator.generate(music_input)

            # Should use string directly
            mock_gen.assert_called_once()
            call_args = mock_gen.call_args[0]
            assert call_args[0] == "calm background music"

    def test_generate_with_empty_list(self, test_config, tmp_path):
        """Test generate() with empty list."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        # Input is empty list
        music_input = []

        result = generator.generate(music_input)

        # Should return None
        assert result is None

    def test_generate_with_none_input(self, test_config, tmp_path):
        """Test generate() with None input."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        result = generator.generate(None)

        # Should return None
        assert result is None

    def test_generate_with_empty_string(self, test_config, tmp_path):
        """Test generate() with empty string."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        result = generator.generate("")

        # Should return None (empty string is falsy)
        assert result is None

    def test_generate_unknown_engine(self, test_config, tmp_path):
        """Test generate() with unknown engine type."""
        test_config["music"]["engine"] = "unknown_engine"
        generator = MusicGenerator(test_config)

        result = generator.generate("test music")

        # Should return None for unknown engine
        assert result is None

    def test_generate_cached_music(self, test_config, tmp_path):
        """Test generate() returns cached music if exists."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        cached_path = tmp_path / "cache" / "music" / "cached.wav"
        cached_path.parent.mkdir(parents=True, exist_ok=True)
        cached_path.write_bytes(b"cached audio")

        with patch.object(generator, "_get_cache_key", return_value="cached"):
            result = generator.generate("test music")

            # Should return cached path
            assert result == cached_path


class TestGenerateMubert:
    """Test _generate_mubert method."""

    def test_generate_mubert_creates_file(self, test_config, tmp_path):
        """Test _generate_mubert creates output file (TODO implementation)."""
        test_config["music"]["engine"] = "mubert"
        generator = MusicGenerator(test_config)

        output_path = tmp_path / "output.wav"

        result = generator._generate_mubert("test description", output_path)

        # Should create file (TODO implementation)
        assert result == output_path
        assert output_path.exists()


class TestSelectFromLibrary:
    """Test _select_from_library method."""

    def test_select_from_library_creates_file(self, test_config, tmp_path):
        """Test _select_from_library creates output file (TODO implementation)."""
        test_config["music"]["engine"] = "library"
        generator = MusicGenerator(test_config)

        output_path = tmp_path / "output.wav"

        result = generator._select_from_library("test description", output_path)

        # Should create file (TODO implementation)
        assert result == output_path
        assert output_path.exists()


class TestGetCacheKey:
    """Test _get_cache_key method."""

    def test_get_cache_key_generates_hash(self, test_config, tmp_path):
        """Test _get_cache_key generates MD5 hash."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        key1 = generator._get_cache_key("test description")
        key2 = generator._get_cache_key("test description")

        # Same input should generate same key
        assert key1 == key2
        assert len(key1) == 32  # MD5 hash length

    def test_get_cache_key_different_descriptions(self, test_config, tmp_path):
        """Test _get_cache_key generates different keys for different descriptions."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        key1 = generator._get_cache_key("description 1")
        key2 = generator._get_cache_key("description 2")

        # Different inputs should generate different keys
        assert key1 != key2

    def test_get_cache_key_includes_engine_type(self, test_config, tmp_path):
        """Test _get_cache_key includes engine type in hash."""
        test_config["music"]["engine"] = "musicgen"
        generator1 = MusicGenerator(test_config)

        test_config["music"]["engine"] = "mubert"
        generator2 = MusicGenerator(test_config)

        key1 = generator1._get_cache_key("same description")
        key2 = generator2._get_cache_key("same description")

        # Different engines should generate different keys
        assert key1 != key2


class TestGenerateMusicgenEdgeCases:
    """Test _generate_musicgen edge cases."""

    def test_generate_musicgen_cpu_no_autocast(self, test_config, tmp_path):
        """Test _generate_musicgen on CPU doesn't use autocast."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        # Mock CPU mode
        generator.use_gpu = False
        generator.model = MagicMock()
        generator.model.sample_rate = 32000
        generator.model.generate.return_value = [MagicMock()]

        output_path = tmp_path / "output.wav"

        with (
            patch("torch.inference_mode") as mock_inference,
            patch("torch.cuda.amp.autocast") as mock_autocast,
            patch("torchaudio.save") as mock_save,
        ):
            mock_inference.return_value.__enter__ = MagicMock()
            mock_inference.return_value.__exit__ = MagicMock(return_value=False)

            result = generator._generate_musicgen("test description", output_path)

            # Should not use autocast on CPU
            assert not mock_autocast.called
            assert mock_save.called

    def test_generate_musicgen_exception_returns_none(self, test_config, tmp_path):
        """Test _generate_musicgen returns None on exception."""
        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        generator.model = MagicMock()
        generator.model.generate.side_effect = Exception("Generation failed")

        output_path = tmp_path / "output.wav"

        result = generator._generate_musicgen("test description", output_path)

        # Should return None on exception
        assert result is None

    def test_generate_musicgen_uses_config_parameters(self, test_config, tmp_path):
        """Test _generate_musicgen uses parameters from config."""
        test_config["music"]["musicgen"]["duration"] = 15
        test_config["music"]["musicgen"]["temperature"] = 1.5
        test_config["music"]["musicgen"]["top_k"] = 200
        test_config["music"]["musicgen"]["top_p"] = 0.5

        test_config["music"]["engine"] = "musicgen"
        generator = MusicGenerator(test_config)

        generator.model = MagicMock()
        generator.model.sample_rate = 32000
        generator.model.generate.return_value = [MagicMock()]

        output_path = tmp_path / "output.wav"

        with (
            patch("torch.inference_mode") as mock_inference,
            patch("torchaudio.save") as mock_save,
        ):
            mock_inference.return_value.__enter__ = MagicMock()
            mock_inference.return_value.__exit__ = MagicMock(return_value=False)

            result = generator._generate_musicgen("test description", output_path)

            # Should call set_generation_params with config values
            assert generator.model.set_generation_params.called
            call_kwargs = generator.model.set_generation_params.call_args[1]
            assert call_kwargs.get("duration") == 15
            assert call_kwargs.get("temperature") == 1.5
            assert call_kwargs.get("top_k") == 200
            assert call_kwargs.get("top_p") == 0.5

