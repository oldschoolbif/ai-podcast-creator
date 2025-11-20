"""
Integration tests for AudioVisualizer - Test generate_visualization method
These tests exercise the full generate_visualization code path to improve coverage.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.audio_visualizer import AudioVisualizer


@pytest.fixture
def test_config_visualization(tmp_path):
    """Create test configuration for audio visualizer."""
    return {
        "visualization": {
            "style": "waveform",
            "primary_color": [0, 150, 255],
            "secondary_color": [255, 100, 200],
            "background_color": [10, 10, 20],
            "waveform": {
                "position": "bottom",
                "num_lines": 1,
                "line_thickness": 12,
                "opacity": 1.0,
            },
        },
        "video": {
            "resolution": [1920, 1080],
            "fps": 30,
        },
        "storage": {"cache_dir": str(tmp_path)},
    }


@pytest.mark.integration
class TestAudioVisualizerGenerateVisualization:
    """Integration tests for AudioVisualizer.generate_visualization method."""

    def test_generate_visualization_waveform_style(self, test_config_visualization, tmp_path):
        """Test generate_visualization with waveform style (line 191)."""
        test_config_visualization["visualization"]["style"] = "waveform"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            mock_stream.assert_called_once()

    def test_generate_visualization_spectrum_style(self, test_config_visualization, tmp_path):
        """Test generate_visualization with spectrum style (line 193-195)."""
        test_config_visualization["visualization"]["style"] = "spectrum"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            mock_stream.assert_called_once()

    def test_generate_visualization_circular_style(self, test_config_visualization, tmp_path):
        """Test generate_visualization with circular style (line 196-197)."""
        test_config_visualization["visualization"]["style"] = "circular"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            mock_stream.assert_called_once()

    def test_generate_visualization_particles_style(self, test_config_visualization, tmp_path):
        """Test generate_visualization with particles style (line 198-199)."""
        test_config_visualization["visualization"]["style"] = "particles"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            mock_stream.assert_called_once()

    def test_generate_visualization_unknown_style_fallback(self, test_config_visualization, tmp_path):
        """Test generate_visualization with unknown style falls back to waveform (line 200-202)."""
        test_config_visualization["visualization"]["style"] = "unknown_style"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            mock_stream.assert_called_once()

    def test_generate_visualization_ffmpeg_duration_fallback(self, test_config_visualization, tmp_path):
        """Test generate_visualization falls back to default duration when FFmpeg fails (line 179-182)."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=None),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            # Should use default duration of 10.0 seconds (line 182)
            mock_stream.assert_called_once()

    def test_generate_visualization_ffmpeg_duration_zero_fallback(self, test_config_visualization, tmp_path):
        """Test generate_visualization falls back to default duration when FFmpeg returns 0 (line 179-182)."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=0.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            # Should use default duration of 10.0 seconds (line 182)
            mock_stream.assert_called_once()

    def test_generate_visualization_chunked_loading(self, test_config_visualization, tmp_path):
        """Test generate_visualization uses chunked audio loading (line 185-187)."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load") as mock_load,
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            # First call for sample (line 185), then chunked calls in frame generator
            mock_load.return_value = (np.random.randn(4410), 22050)  # 0.1s sample
            mock_stream.return_value = output_path
            
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            # Should call librosa.load at least once for sample
            assert mock_load.call_count >= 1

    def test_generate_visualization_progress_prints(self, test_config_visualization, tmp_path):
        """Test generate_visualization prints progress messages (line 176, 207)."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video", return_value=output_path),
            patch("builtins.print") as mock_print,
        ):
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            # Should print generation start and completion messages
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Generating" in str(call) or "visualization" in str(call).lower() for call in print_calls)
            assert any("OK" in str(call) or "generated" in str(call).lower() for call in print_calls)

    def test_generate_visualization_with_custom_resolution(self, test_config_visualization, tmp_path):
        """Test generate_visualization with custom resolution."""
        test_config_visualization["video"]["resolution"] = [1280, 720]
        test_config_visualization["video"]["fps"] = 24
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=10.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            assert visualizer.resolution == [1280, 720]
            assert visualizer.fps == 24

    def test_generate_visualization_streams_frames_to_video(self, test_config_visualization, tmp_path):
        """Test generate_visualization streams frames to video (line 205)."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=5.0),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = output_path
            result = visualizer.generate_visualization(audio_path, output_path)
            
            assert result == output_path
            # Verify _stream_frames_to_video was called with correct arguments
            call_args = mock_stream.call_args
            assert call_args is not None
            # Should pass frame generator, audio_path, output_path, and duration
            assert len(call_args[0]) >= 3  # At least frame_generator, audio_path, output_path

