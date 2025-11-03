"""
Focused Unit Tests for MusicGenerator
Tests that don't require audiocraft to improve coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.music_generator import MusicGenerator


class TestMusicGeneratorInitialization:
    """Test MusicGenerator initialization paths."""

    def test_init_creates_cache_dir(self, test_config, temp_dir):
        """Test that cache directory is created on init."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)

        assert generator.cache_dir.exists()
        assert generator.cache_dir.is_dir()

    def test_init_sets_device_from_gpu_manager(self, test_config):
        """Test that device is set from GPU manager."""
        test_config["music"]["engine"] = "library"

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"

            generator = MusicGenerator(test_config)

            assert generator.device == "cuda"
            assert generator.use_gpu is True

    def test_init_sets_cpu_when_no_gpu(self, test_config):
        """Test that CPU is used when GPU not available."""
        test_config["music"]["engine"] = "library"

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = MusicGenerator(test_config)

            assert generator.device == "cpu"
            assert generator.use_gpu is False

    def test_init_musicgen_without_audiocraft(self, test_config):
        """Test MusicGen init when audiocraft not available."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            # Simulate ImportError for audiocraft
            with patch.dict("sys.modules", {"audiocraft": None}):
                generator = MusicGenerator(test_config)

                assert generator.engine_type == "musicgen"
                assert generator.model is None


class TestMusicGeneratorGenerateMethod:
    """Test the generate() method with various inputs."""

    def test_generate_with_string_description(self, test_config, temp_dir):
        """Test generation with string description."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        result = generator.generate("upbeat background music")

        assert result is not None
        assert isinstance(result, Path)

    def test_generate_with_empty_string(self, test_config):
        """Test generation with empty string."""
        test_config["music"]["engine"] = "library"

        generator = MusicGenerator(test_config)
        result = generator.generate("")

        assert result is None

    def test_generate_with_none(self, test_config):
        """Test generation with None."""
        test_config["music"]["engine"] = "library"

        generator = MusicGenerator(test_config)
        result = generator.generate(None)

        assert result is None

    def test_generate_with_list_of_strings(self, test_config, temp_dir):
        """Test generation with list of strings."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        result = generator.generate(["upbeat music"])

        assert result is not None

    def test_generate_with_list_of_dicts(self, test_config, temp_dir):
        """Test generation with list of dicts with description."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        music_cues = [{"description": "calm ambient music", "timestamp": 0}]
        result = generator.generate(music_cues)

        assert result is not None

    def test_generate_with_empty_list(self, test_config):
        """Test generation with empty list."""
        test_config["music"]["engine"] = "library"

        generator = MusicGenerator(test_config)
        result = generator.generate([])

        assert result is None

    def test_generate_with_list_no_description_key(self, test_config, temp_dir):
        """Test generation with list of dicts without description key."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        music_cues = [{"other_key": "value"}]
        result = generator.generate(music_cues)

        # Should use default description
        assert result is not None


class TestMusicGeneratorCaching:
    """Test cache functionality."""

    def test_cache_hit_returns_cached_file(self, test_config, temp_dir):
        """Test that cache hit returns existing file."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)

        # Pre-create cached file
        cache_key = generator._get_cache_key("test music")
        cached_file = generator.cache_dir / f"{cache_key}.wav"
        cached_file.write_bytes(b"cached audio")

        result = generator.generate("test music")

        assert result == cached_file
        assert result.exists()

    def test_cache_miss_generates_new(self, test_config, temp_dir):
        """Test that cache miss triggers generation."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)

        # Ensure cache doesn't exist
        cache_key = generator._get_cache_key("new music")
        cached_file = generator.cache_dir / f"{cache_key}.wav"
        if cached_file.exists():
            cached_file.unlink()

        result = generator.generate("new music")

        # Library engine creates file, so should exist
        assert result is not None
        assert result.exists()


class TestCacheKeyGeneration:
    """Test cache key generation."""

    def test_cache_key_consistency(self, test_config):
        """Test that same description generates same key."""
        test_config["music"]["engine"] = "library"

        generator = MusicGenerator(test_config)

        key1 = generator._get_cache_key("test description")
        key2 = generator._get_cache_key("test description")

        assert key1 == key2
        assert len(key1) == 32  # MD5 hex digest length

    def test_cache_key_uniqueness(self, test_config):
        """Test that different descriptions generate different keys."""
        test_config["music"]["engine"] = "library"

        generator = MusicGenerator(test_config)

        key1 = generator._get_cache_key("description one")
        key2 = generator._get_cache_key("description two")

        assert key1 != key2

    def test_cache_key_includes_engine_type(self, test_config):
        """Test that cache key includes engine type."""
        test_config["music"]["engine"] = "library"

        generator1 = MusicGenerator(test_config)

        test_config["music"]["engine"] = "mubert"
        generator2 = MusicGenerator(test_config)

        key1 = generator1._get_cache_key("same description")
        key2 = generator2._get_cache_key("same description")

        # Different engines should produce different keys
        assert key1 != key2


class TestMusicGeneratorMubert:
    """Test Mubert engine paths."""

    def test_generate_with_mubert_engine(self, test_config, temp_dir):
        """Test generation with Mubert engine."""
        test_config["music"]["engine"] = "mubert"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        result = generator.generate("test music")

        # Mubert currently creates placeholder file
        assert result is not None
        assert result.exists()

    def test_generate_mubert_method(self, test_config, temp_dir):
        """Test _generate_mubert method directly."""
        test_config["music"]["engine"] = "mubert"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        output_path = temp_dir / "mubert_output.wav"

        result = generator._generate_mubert("test description", output_path)

        assert result == output_path
        assert output_path.exists()


class TestMusicGeneratorLibrary:
    """Test library engine paths."""

    def test_generate_with_library_engine(self, test_config, temp_dir):
        """Test generation with library engine."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        result = generator.generate("test music")

        # Library currently creates placeholder file
        assert result is not None
        assert result.exists()

    def test_select_from_library_method(self, test_config, temp_dir):
        """Test _select_from_library method directly."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        output_path = temp_dir / "library_output.wav"

        result = generator._select_from_library("test description", output_path)

        assert result == output_path
        assert output_path.exists()


class TestMusicGeneratorMusicGenPaths:
    """Test MusicGen-specific paths (without requiring audiocraft)."""

    def test_generate_musicgen_when_model_none(self, test_config, temp_dir):
        """Test MusicGen generation when model is None."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            # Simulate audiocraft not available
            with patch.dict("sys.modules", {"audiocraft": None}):
                generator = MusicGenerator(test_config)
                assert generator.model is None

                result = generator.generate("test music")

                # Should return None when model not available
                assert result is None

    def test_generate_musicgen_exception_handling(self, test_config, temp_dir):
        """Test MusicGen generation exception handling."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            # Create generator with mocked model that raises exception
            with patch.dict("sys.modules", {"audiocraft": MagicMock()}):
                mock_model = MagicMock()
                mock_model.generate.side_effect = Exception("Generation failed")

                generator = MusicGenerator(test_config)
                generator.model = mock_model

                result = generator.generate("test music")

                # Should return None on exception
                assert result is None


class TestMusicGeneratorEdgeCases:
    """Test edge cases and error handling."""

    def test_generate_with_very_long_description(self, test_config, temp_dir):
        """Test generation with very long description."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        long_desc = "a" * 1000  # Very long description

        result = generator.generate(long_desc)

        assert result is not None

    def test_cache_dir_creation_on_multiple_init(self, test_config, temp_dir):
        """Test cache dir creation is idempotent."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        # Create first generator
        gen1 = MusicGenerator(test_config)
        cache_dir = gen1.cache_dir

        # Create second generator with same config
        gen2 = MusicGenerator(test_config)

        # Both should use same cache dir
        assert gen1.cache_dir == gen2.cache_dir
        assert cache_dir.exists()
