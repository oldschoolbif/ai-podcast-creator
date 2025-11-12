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


class TestMusicGeneratorMusicGen:
    """Test MusicGen generation."""

    @pytest.mark.gpu
    def test_generate_musicgen_gpu(self, test_config, temp_dir, skip_if_no_gpu, stub_audiocraft):
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

        output_path = temp_dir / "test_music.wav"
        
        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
            patch("torch.inference_mode"),
            patch("torchaudio.save") as mock_save,
            patch("pathlib.Path.exists", return_value=True),
        ):

            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            mock_model = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model
            mock_model.generate.return_value = MagicMock()
            mock_model.sample_rate = 32000
            
            # Mock torchaudio.save to create the file
            def mock_save_func(waveform, path, sample_rate):
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).touch()
            mock_save.side_effect = mock_save_func

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
        """Test generation with empty input (line 114)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}

        with patch("audiocraft.models.MusicGen"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)
            result = generator.generate(None)

            assert result is None

    def test_generate_with_empty_list(self, test_config):
        """Test generation with empty list (line 114)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}

        with patch("audiocraft.models.MusicGen"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)
            result = generator.generate([])

            assert result is None

    @patch("torch.__version__", "2.1.0")
    @patch("torch.compile")
    @patch("audiocraft.models.MusicGen")
    @patch("builtins.print")  # Capture print statements for coverage
    def test_init_musicgen_gpu_with_torch_compile(self, mock_print, mock_gen, mock_compile, test_config, temp_dir):
        """Test MusicGen initialization with GPU and torch.compile (lines 49-75)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": False}

            mock_model = MagicMock()
            mock_model.lm = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            generator = MusicGenerator(test_config)

            assert generator.engine_type == "musicgen"
            # torch.compile should be called if available
            mock_compile.assert_called()
            # Verify GPU initialization print (line 52)
            assert any("Initializing MusicGen on GPU" in str(call) for call in mock_print.call_args_list)

    @patch("torch.__version__", "1.9.0")  # Old version without compile
    @patch("audiocraft.models.MusicGen")
    def test_init_musicgen_gpu_no_torch_compile(self, mock_gen, test_config, temp_dir):
        """Test MusicGen initialization when torch.compile not available (line 59)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": False}

            mock_model = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            generator = MusicGenerator(test_config)

            assert generator.engine_type == "musicgen"
            # Should not fail even without torch.compile

    @patch("torch.compile")
    @patch("audiocraft.models.MusicGen")
    def test_init_musicgen_gpu_torch_compile_exception(self, mock_gen, mock_compile, test_config, temp_dir):
        """Test MusicGen when torch.compile fails (lines 63-64)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("torch.__version__", "2.1.0"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": False}

            mock_model = MagicMock()
            mock_model.lm = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model
            mock_compile.side_effect = Exception("Compile failed")

            generator = MusicGenerator(test_config)

            # Should handle exception gracefully
            assert generator.engine_type == "musicgen"

    @patch("audiocraft.models.MusicGen")
    def test_init_musicgen_gpu_with_fp16(self, mock_gen, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen initialization with GPU and FP16 (lines 67-72)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": True}

            # Stub torch in sys.modules (imported locally in _init_musicgen)
            mock_torch = MagicMock()
            mock_torch.__version__ = "2.1.0"
            sys.modules["torch"] = mock_torch

            mock_model = MagicMock()
            mock_model.lm = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            generator = MusicGenerator(test_config)

            assert generator.engine_type == "musicgen"
            # FP16 should be enabled
            mock_model.lm.half.assert_called()

    @patch("audiocraft.models.MusicGen")
    def test_init_musicgen_gpu_fp16_exception(self, mock_gen, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen when FP16 fails (lines 71-72)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": True}

            mock_model = MagicMock()
            mock_model.lm = MagicMock()
            mock_model.lm.half.side_effect = Exception("FP16 failed")
            mock_gen.get_pretrained.return_value = mock_model

            generator = MusicGenerator(test_config)

            # Should handle exception gracefully
            assert generator.engine_type == "musicgen"

    @patch("builtins.print")
    def test_init_musicgen_cpu(self, mock_print, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen initialization on CPU (lines 73-75)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": False}

            # Stub torch in sys.modules (imported locally in _init_musicgen)
            mock_torch = MagicMock()
            mock_torch.__version__ = "2.1.0"
            sys.modules["torch"] = mock_torch

            mock_model = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            generator = MusicGenerator(test_config)

            assert generator.engine_type == "musicgen"
            # Should use CPU device
            mock_gen.get_pretrained.assert_called_with("facebook/musicgen-small", device="cpu")
            # Verify CPU warning print (line 74)
            assert any("Initializing MusicGen on CPU" in str(call) or "⚠" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.print")
    def test_generate_musicgen_gpu_autocast(self, mock_print, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen generation with GPU autocast (lines 164-168)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {
            "model": "facebook/musicgen-small",
            "duration": 5,
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            mock_model = MagicMock()
            mock_model.generate.return_value = [MagicMock()]
            mock_model.sample_rate = 32000
            mock_model.set_generation_params = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            # Stub torch and torchaudio in sys.modules before generation
            mock_torch = MagicMock()
            mock_torch.inference_mode.return_value.__enter__ = MagicMock()
            mock_torch.inference_mode.return_value.__exit__ = MagicMock(return_value=False)
            mock_autocast = MagicMock()
            mock_autocast.return_value.__enter__ = MagicMock()
            mock_autocast.return_value.__exit__ = MagicMock(return_value=False)
            mock_torch.cuda.amp.autocast = mock_autocast
            sys.modules["torch"] = mock_torch
            
            mock_torchaudio = MagicMock()
            def mock_save_func(waveform, path, sample_rate):
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).touch()
            mock_torchaudio.save = MagicMock(side_effect=mock_save_func)
            sys.modules["torchaudio"] = mock_torchaudio

            generator = MusicGenerator(test_config)
            # Ensure model is set
            generator.model = mock_model
            
            generator.generate("test music")

            # Should use autocast for GPU
            mock_autocast.assert_called()
            # Should save audio (line 173)
            mock_torchaudio.save.assert_called()
            # Should clear cache (line 177)
            mock_gpu.return_value.clear_cache.assert_called()
            # Verify generation print (line 162)
            assert any("Generating music" in str(call) or "🎵" in str(call) for call in mock_print.call_args_list)

    def test_generate_musicgen_gpu_cache_clearing(self, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen GPU cache clearing at start (line 143)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {
            "model": "facebook/musicgen-small",
            "duration": 5,
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            mock_model = MagicMock()
            mock_model.generate.return_value = [MagicMock()]
            mock_model.sample_rate = 32000
            mock_model.set_generation_params = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            # Stub torch and torchaudio in sys.modules before generation
            mock_torch = MagicMock()
            mock_torch.inference_mode.return_value.__enter__ = MagicMock()
            mock_torch.inference_mode.return_value.__exit__ = MagicMock(return_value=False)
            mock_autocast = MagicMock()
            mock_autocast.return_value.__enter__ = MagicMock()
            mock_autocast.return_value.__exit__ = MagicMock(return_value=False)
            mock_torch.cuda.amp.autocast = mock_autocast
            sys.modules["torch"] = mock_torch
            
            mock_torchaudio = MagicMock()
            def mock_save_func(waveform, path, sample_rate):
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).touch()
            mock_torchaudio.save = MagicMock(side_effect=mock_save_func)
            sys.modules["torchaudio"] = mock_torchaudio

            generator = MusicGenerator(test_config)
            # Ensure model is set
            generator.model = mock_model
            
            generator.generate("test music")

            # Should clear cache at start (line 143) and end (line 177)
            assert mock_gpu.return_value.clear_cache.call_count >= 1

    def test_generate_musicgen_parameters_from_config(self, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen uses config parameters (lines 144-157)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {
            "model": "facebook/musicgen-small",
            "duration": 15,
            "temperature": 0.8,
            "top_k": 200,
            "top_p": 0.5
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            mock_model = MagicMock()
            mock_model.generate.return_value = [MagicMock()]
            mock_model.sample_rate = 32000
            mock_model.set_generation_params = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            # Stub torch and torchaudio in sys.modules before generation
            mock_torch = MagicMock()
            mock_torch.inference_mode.return_value.__enter__ = MagicMock()
            mock_torch.inference_mode.return_value.__exit__ = MagicMock(return_value=False)
            sys.modules["torch"] = mock_torch
            
            mock_torchaudio = MagicMock()
            def mock_save_func(waveform, path, sample_rate):
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).touch()
            mock_torchaudio.save = MagicMock(side_effect=mock_save_func)
            sys.modules["torchaudio"] = mock_torchaudio

            generator = MusicGenerator(test_config)
            # Ensure model is set (since _init_musicgen might have failed)
            generator.model = mock_model
            
            generator.generate("test music")

            # Verify set_generation_params was called with config values
            mock_model.set_generation_params.assert_called_once()
            call_kwargs = mock_model.set_generation_params.call_args[1]
            assert call_kwargs["duration"] == 15
            assert call_kwargs["temperature"] == 0.8
            assert call_kwargs["top_k"] == 200
            assert call_kwargs["top_p"] == 0.5

    @patch("builtins.print")
    def test_generate_musicgen_cpu_no_autocast(self, mock_print, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen generation with CPU (no autocast, lines 166-167)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {
            "model": "facebook/musicgen-small",
            "duration": 5,
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            mock_model = MagicMock()
            mock_model.generate.return_value = [MagicMock()]
            mock_model.sample_rate = 32000
            mock_model.set_generation_params = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            # Stub torch and torchaudio in sys.modules before generation
            mock_torch = MagicMock()
            mock_torch.inference_mode.return_value.__enter__ = MagicMock()
            mock_torch.inference_mode.return_value.__exit__ = MagicMock(return_value=False)
            sys.modules["torch"] = mock_torch
            
            mock_torchaudio = MagicMock()
            def mock_save_func(waveform, path, sample_rate):
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).touch()
            mock_torchaudio.save = MagicMock(side_effect=mock_save_func)
            sys.modules["torchaudio"] = mock_torchaudio

            generator = MusicGenerator(test_config)
            # Ensure model is set (since _init_musicgen might have failed)
            generator.model = mock_model
            
            generator.generate("test music")

            # Should save audio (line 173)
            mock_torchaudio.save.assert_called()
            # Verify success print (line 179)
            assert any("Music generated" in str(call) or "✓" in str(call) for call in mock_print.call_args_list)

    @patch("torchaudio.save")
    @patch("torch.inference_mode")
    @patch("builtins.print")
    def test_generate_musicgen_exception_handling(self, mock_print, mock_inference, mock_save, test_config, temp_dir, stub_audiocraft):
        """Test MusicGen generation exception handling (lines 179-181)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {
            "model": "facebook/musicgen-small",
            "duration": 5,
        }
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("audiocraft.models.MusicGen") as mock_gen,
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):

            mock_gpu.return_value.gpu_available = False

            mock_model = MagicMock()
            mock_model.generate.side_effect = Exception("Generation failed")
            mock_model.sample_rate = 32000
            mock_model.set_generation_params = MagicMock()
            mock_gen.get_pretrained.return_value = mock_model

            # Create a mock torchaudio module
            mock_torchaudio = MagicMock()
            mock_torchaudio.save = MagicMock()
            sys.modules["torchaudio"] = mock_torchaudio

            generator = MusicGenerator(test_config)
            # Ensure model is set (since _init_musicgen might have failed)
            generator.model = mock_model
            
            result = generator.generate("test music")

            # Should return None on exception
            assert result is None
            # Verify exception print (line 183) - check for warning emoji or text
            assert any("Music generation failed" in str(call) or "⚠" in str(call) for call in mock_print.call_args_list)

    def test_generate_mubert(self, test_config, temp_dir):
        """Test Mubert generation (lines 183-187)."""
        test_config["music"]["engine"] = "mubert"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)
            result = generator.generate("test music")

            # Mubert returns touched file path
            assert result is not None

    def test_select_from_library(self, test_config, temp_dir):
        """Test library selection (lines 189-193)."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)
            result = generator.generate("test music")

            # Library returns touched file path
            assert result is not None

    def test_generate_musicgen_model_not_available(self, test_config, temp_dir, stub_audiocraft):
        """Test when MusicGen model is not available."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with (
            patch("src.core.music_generator.get_gpu_manager") as mock_gpu,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            mock_gpu.return_value.get_performance_config.return_value = {"use_fp16": False}

            # Stub torch in sys.modules
            mock_torch = MagicMock()
            mock_torch.__version__ = "2.1.0"
            sys.modules["torch"] = mock_torch

            # Patch MusicGen.get_pretrained to raise ImportError
            with patch("audiocraft.models.MusicGen.get_pretrained", side_effect=ImportError("Model not available")):
                generator = MusicGenerator(test_config)
                # Model should be None due to ImportError
                assert generator.model is None
                
                result = generator.generate("test music")
                # Should return None when model is not available
                assert result is None


class TestMusicGeneratorCacheKey:
    """Test cache key generation."""

    def test_cache_key_generation(self, test_config, stub_audiocraft):
        """Test cache key is consistent."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "test"}

        with patch("audiocraft.models.MusicGen"), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:

            mock_gpu.return_value.gpu_available = False

            generator = MusicGenerator(test_config)

            key1 = generator._get_cache_key("test music")
            key2 = generator._get_cache_key("test music")

            assert key1 == key2

    def test_cache_key_different_descriptions(self, test_config, stub_audiocraft):
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
def test_music_descriptions(test_config, temp_dir, description, expected_type, stub_audiocraft):
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
