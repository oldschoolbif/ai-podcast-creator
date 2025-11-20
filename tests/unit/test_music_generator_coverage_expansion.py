"""
Music Generator Coverage Expansion Tests
Tests for missing paths to reach 80%+ coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.music_generator import MusicGenerator


class TestMusicGeneratorMissingPaths:
    """Test paths that are currently missing coverage."""

    def test_generate_musicgen_cpu_path(self, test_config, temp_dir):
        """Test _generate_musicgen with CPU (lines 169-170)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small", "duration": 5}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        # Mock audiocraft and torch
        mock_model = MagicMock()
        mock_model.sample_rate = 16000
        mock_model.generate.return_value = [MagicMock()]
        mock_model.set_generation_params = MagicMock()

        mock_audiocraft = MagicMock()
        mock_audiocraft.models.MusicGen.get_pretrained.return_value = mock_model

        mock_torch = MagicMock()
        mock_torch.inference_mode = MagicMock(return_value=MagicMock())
        mock_torch.cuda.amp.autocast = MagicMock(return_value=MagicMock())

        with patch.dict("sys.modules", {
            "torch": mock_torch,
            "torchaudio": MagicMock(),
            "audiocraft": mock_audiocraft,
            "audiocraft.models": mock_audiocraft.models
        }), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            
            mock_gpu.return_value.gpu_available = False  # CPU mode
            mock_gpu.return_value.get_device.return_value = "cpu"
            mock_gpu.return_value.clear_cache = MagicMock()

            generator = MusicGenerator(test_config)
            
            with patch("torchaudio.save") as mock_save:
                result = generator._generate_musicgen("test music", temp_dir / "output.wav")

                # Verify CPU path was used (no autocast)
                assert mock_torch.cuda.amp.autocast.called == False  # autocast not called in CPU mode
                assert mock_model.generate.called
                assert result is not None

    def test_generate_musicgen_exception_handling(self, test_config, temp_dir):
        """Test _generate_musicgen exception handling (lines 182-184)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        # Mock model that raises exception
        mock_model = MagicMock()
        mock_model.generate.side_effect = Exception("Generation failed")

        mock_audiocraft = MagicMock()
        mock_audiocraft.models.MusicGen.get_pretrained.return_value = mock_model

        mock_torch = MagicMock()
        mock_torch.inference_mode = MagicMock(return_value=MagicMock())
        mock_torch.cuda.amp.autocast = MagicMock(return_value=MagicMock())

        with patch.dict("sys.modules", {
            "torch": mock_torch,
            "torchaudio": MagicMock(),
            "audiocraft": mock_audiocraft,
            "audiocraft.models": mock_audiocraft.models
        }), patch("src.core.music_generator.get_gpu_manager") as mock_gpu, \
             patch("builtins.print") as mock_print:
            
            mock_gpu.return_value.gpu_available = True
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            generator = MusicGenerator(test_config)
            generator.model = mock_model  # Set model
            
            result = generator._generate_musicgen("test music", temp_dir / "output.wav")

            # Should return None on exception
            assert result is None
            # Verify error was printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Music generation failed" in call for call in print_calls)

    def test_generate_mubert_path(self, test_config, temp_dir):
        """Test generate with mubert engine (lines 124-125)."""
        test_config["music"]["engine"] = "mubert"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        output_path = temp_dir / "output.wav"

        result = generator._generate_mubert("test music", output_path)

        # Mubert currently just creates empty file
        assert result == output_path
        assert output_path.exists()

    def test_generate_library_path(self, test_config, temp_dir):
        """Test generate with library engine (lines 126-127)."""
        test_config["music"]["engine"] = "library"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        output_path = temp_dir / "output.wav"

        result = generator._select_from_library("test music", output_path)

        # Library currently just creates empty file
        assert result == output_path
        assert output_path.exists()

    def test_generate_unknown_engine(self, test_config, temp_dir):
        """Test generate with unknown engine type (lines 128-130)."""
        test_config["music"]["engine"] = "unknown_engine"
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)

        result = generator.generate("test music")

        # Should return None for unknown engine
        assert result is None

    def test_generate_musicgen_missing_model(self, test_config, temp_dir):
        """Test _generate_musicgen when model is None (lines 134-136)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        with patch("src.core.music_generator.get_gpu_manager") as mock_gpu, \
             patch("builtins.print") as mock_print:
            
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"

            generator = MusicGenerator(test_config)
            generator.model = None  # Model not available

            result = generator._generate_musicgen("test music", temp_dir / "output.wav")

            # Should return None when model is None
            assert result is None
            # Verify warning was printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("MusicGen not available" in call for call in print_calls)

    def test_generate_musicgen_with_autocast(self, test_config, temp_dir):
        """Test _generate_musicgen with GPU autocast (lines 166-168)."""
        test_config["music"]["engine"] = "musicgen"
        test_config["music"]["musicgen"] = {"model": "facebook/musicgen-small", "duration": 5}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        # Mock model
        mock_model = MagicMock()
        mock_model.sample_rate = 16000
        mock_model.generate.return_value = [MagicMock()]
        mock_model.set_generation_params = MagicMock()

        mock_audiocraft = MagicMock()
        mock_audiocraft.models.MusicGen.get_pretrained.return_value = mock_model

        mock_torch = MagicMock()
        mock_autocast_context = MagicMock()
        mock_autocast_context.__enter__ = MagicMock(return_value=mock_autocast_context)
        mock_autocast_context.__exit__ = MagicMock(return_value=False)
        mock_torch.cuda.amp.autocast.return_value = mock_autocast_context
        mock_torch.inference_mode = MagicMock(return_value=MagicMock())

        with patch.dict("sys.modules", {
            "torch": mock_torch,
            "torchaudio": MagicMock(),
            "audiocraft": mock_audiocraft,
            "audiocraft.models": mock_audiocraft.models
        }), patch("src.core.music_generator.get_gpu_manager") as mock_gpu:
            
            mock_gpu.return_value.gpu_available = True  # GPU mode
            mock_gpu.return_value.get_device.return_value = "cuda"
            mock_gpu.return_value.clear_cache = MagicMock()

            generator = MusicGenerator(test_config)
            
            with patch("torchaudio.save") as mock_save:
                result = generator._generate_musicgen("test music", temp_dir / "output.wav")

                # Verify autocast was used in GPU mode
                mock_torch.cuda.amp.autocast.assert_called_once()
                assert mock_model.generate.called
                assert result is not None

    def test_init_musicgen_exception_in_nvenc_check(self, test_config, temp_dir):
        """Test _stream_frames_to_video handles exception in NVENC check (lines 1396-1397)."""
        test_config["music"]["engine"] = "library"  # Use library to avoid musicgen init
        test_config["storage"]["cache_dir"] = str(temp_dir)

        generator = MusicGenerator(test_config)
        
        # Test the _stream_frames_to_video NVENC check exception path
        from src.core.audio_visualizer import AudioVisualizer
        viz_config = {
            "visualization": {"style": "waveform"},
            "video": {"resolution": [1920, 1080], "fps": 30},
            "storage": {"cache_dir": str(temp_dir)},
        }
        viz = AudioVisualizer(viz_config)
        
        audio_path = temp_dir / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = temp_dir / "output.mp4"

        def frame_gen():
            yield np.zeros((1080, 1920, 3), dtype=np.uint8)

        with patch("src.core.audio_visualizer.subprocess.run", side_effect=Exception("NVENC check failed")), \
             patch("src.core.audio_visualizer.subprocess.Popen") as mock_popen, \
             patch("src.utils.file_monitor.FileMonitor") as mock_monitor_class:
            
            # Mock process
            mock_process = MagicMock()
            mock_process.stdin = MagicMock()
            mock_process.stdin.write = MagicMock()
            mock_process.stdin.flush = MagicMock()
            mock_process.stdin.close = MagicMock()
            mock_process.poll.return_value = None
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_process.stderr = MagicMock()
            mock_process.stderr.readline = MagicMock(return_value=b"")
            mock_popen.return_value = mock_process

            mock_monitor = MagicMock()
            mock_monitor.get_current_size_mb.return_value = 1.0
            mock_monitor_class.return_value = mock_monitor

            # Should fall back to CPU encoding when NVENC check fails
            result = viz._stream_frames_to_video(frame_gen(), audio_path, output_path, 0.1)

            # Verify CPU encoding was used (libx264, not h264_nvenc)
            call_args = mock_popen.call_args[0][0]
            assert "libx264" in call_args
            assert "h264_nvenc" not in call_args
            assert result == output_path

