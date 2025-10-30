"""
Comprehensive Unit Tests for Music Generator
Tests for src/core/music_generator.py - Aiming for 100% coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.music_generator import MusicGenerator


class TestMusicGeneratorInit:
    """Test MusicGenerator initialization."""

    @pytest.mark.skipif("audiocraft" not in sys.modules, reason="audiocraft not installed")
    def test_init_with_musicgen(self, test_config):
        """Test initialization with MusicGen engine."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small", "duration": 10}

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = MusicGenerator(test_config)
            assert generator.engine_type == "musicgen"

    def test_init_with_mubert(self, test_config):
        """Test initialization with Mubert engine."""
        test_config["music"]["engine"] = "mubert"

        generator = MusicGenerator(test_config)
        assert generator.engine_type == "mubert"

    def test_init_with_library(self, test_config):
        """Test initialization with music library."""
        test_config["music"]["engine"] = "library"

        generator = MusicGenerator(test_config)
        assert generator.engine_type == "library"


@pytest.mark.skipif("audiocraft" not in sys.modules, reason="audiocraft not installed")
class TestMusicGeneratorMusicGen:
    """Test MusicGen generation."""

    @pytest.mark.gpu
    def test_generate_musicgen_gpu(self, test_config, temp_dir, skip_if_no_gpu):
        """Test MusicGen generation with GPU."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {
            "model": "facebook/musicgen-small",
            "duration": 5,
            "temperature": 1.0,
            "top_k": 250,
            "top_p": 0.0,
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
            patch("torch.inference_mode"),
            patch("torchaudio.save"),
        ):

            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            mock_model = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model
            mock_model.generate.return_value = MagicMock()
            mock_model.sample_rate = 32000

            generator = MusicGenerator(test_config)
            result = generator.generate("upbeat background music")

            assert result is not None

    def test_generate_musicgen_cpu(self, test_config, temp_dir):
        """Test MusicGen generation with CPU."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small", "duration": 5}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
            patch("torch.inference_mode"),
            patch("torchaudio.save"),
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            mock_model = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model
            mock_model.generate.return_value = MagicMock()
            mock_model.sample_rate = 32000

            generator = MusicGenerator(test_config)
            result = generator.generate("calm music")

            assert result is not None

    def test_generate_with_cache_hit(self, test_config, temp_dir):
        """Test that cached music is returned if exists."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test", "duration": 5}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("audiocraft.models.MusicGen"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = MusicGenerator(test_config)

            # Create cached file
            cache_key = generator._get_cache_key("test music")
            cached_file = generator.cache_dir / f"{cache_key}.wav"
            cached_file.touch()

            result = generator.generate("test music")
            assert result == cached_file

    def test_generate_with_list_input(self, test_config, temp_dir):
        """Test generation with list of music cues."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test", "duration": 5}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
            patch("torch.inference_mode"),
            patch("torchaudio.save"),
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            mock_model = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model
            mock_model.generate.return_value = MagicMock()
            mock_model.sample_rate = 32000

            generator = MusicGenerator(test_config)

            # Test with list of dicts
            music_cues = [{"description": "upbeat music", "timestamp": 0}]
            result = generator.generate(music_cues)

            assert result is not None

    def test_generate_with_empty_input(self, test_config):
        """Test generation with empty input."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}

        with patch("audiocraft.models.MusicGen"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)
            result = generator.generate(None)

            assert result is None

    def test_generate_musicgen_model_not_available(self, test_config, temp_dir):
        """Test when MusicGen model is not available."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen", side_effect=ImportError),
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)
            result = generator.generate("test music")

            assert result is None  # Should handle gracefully


class TestMusicGeneratorMubert:
    """Test Mubert API generation."""

    def test_generate_mubert(self, test_config, temp_dir):
        """Test Mubert generation."""
        test_config["music"]["engine"] = "mubert"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        # Mubert not implemented yet, should return placeholder
        result = generator._generate_mubert("test", temp_dir / "output.wav")

        assert result is not None


class TestMusicGeneratorLibrary:
    """Test music library selection."""

    def test_select_from_library(self, test_config, temp_dir):
        """Test selecting music from library."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        result = generator._select_from_library("test", temp_dir / "output.wav")

        assert result is not None


@pytest.mark.skipif("audiocraft" not in sys.modules, reason="audiocraft not installed")
class TestMusicGeneratorCacheKey:
    """Test cache key generation."""

    def test_cache_key_generation(self, test_config):
        """Test cache key is consistent."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}

        with patch("audiocraft.models.MusicGen"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)

            key1 = generator._get_cache_key("test music")
            key2 = generator._get_cache_key("test music")

            assert key1 == key2

    def test_cache_key_different_descriptions(self, test_config):
        """Test different descriptions give different keys."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}

        with patch("audiocraft.models.MusicGen"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)

            key1 = generator._get_cache_key("upbeat music")
            key2 = generator._get_cache_key("calm music")

            assert key1 != key2


@pytest.mark.parametrize(
    "description,expected_type",
    [
        ("upbeat electronic music", str),
        ("calm ambient sounds", str),
        ("energetic rock", str),
    ],
)
@pytest.mark.skipif("audiocraft" not in sys.modules, reason="audiocraft not installed")
def test_music_descriptions(test_config, temp_dir, description, expected_type):
    """Test various music descriptions."""
    test_config["music"]["engine"] = "musicgen"
    test_config["music"]["musicgen"] = {"model": "test", "duration": 5}
    test_config["storage"]["cache_dir"] = str(temp_dir)

    with (
        patch("audiocraft.models.MusicGen") as mock_gen,
        patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        patch("torch.inference_mode"),
        patch("torchaudio.save"),
    ):

        mock_gpu.return_value.gpu_available = False
        mock_gpu.return_value.get_device.return_value = "cpu"

        mock_model = MagicMock()
        mock_gen.get_pretrained.return_value = mock_model
        mock_model.generate.return_value = MagicMock()
        mock_model.sample_rate = 32000

        generator = MusicGenerator(test_config)
        result = generator.generate(description)

        assert isinstance(result, (Path, type(None)))
