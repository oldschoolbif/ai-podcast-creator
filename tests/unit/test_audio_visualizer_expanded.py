"""
Expanded tests for AudioVisualizer - Additional coverage for uncovered paths
Focus on waveform configurations, error handling, and edge cases.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from PIL import Image

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


class TestWaveformConfigurations:
    """Test various waveform configuration options."""

    def test_waveform_multiple_positions(self, test_config_visualization, tmp_path):
        """Test waveform with multiple positions."""
        test_config_visualization["visualization"]["waveform"]["position"] = "top,bottom"
        test_config_visualization["visualization"]["waveform"]["num_lines"] = 2
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_left_right_positions(self, test_config_visualization, tmp_path):
        """Test waveform with left and right positions."""
        test_config_visualization["visualization"]["waveform"]["position"] = "left,right"
        test_config_visualization["visualization"]["waveform"]["orientation"] = "vertical"
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_middle_position(self, test_config_visualization, tmp_path):
        """Test waveform with middle position."""
        test_config_visualization["visualization"]["waveform"]["position"] = "middle"
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_per_line_thickness(self, test_config_visualization, tmp_path):
        """Test waveform with per-line thickness array."""
        test_config_visualization["visualization"]["waveform"]["line_thickness"] = [15, 12, 8]
        test_config_visualization["visualization"]["waveform"]["num_lines"] = 3
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_per_line_colors(self, test_config_visualization, tmp_path):
        """Test waveform with per-line colors."""
        test_config_visualization["visualization"]["waveform"]["line_colors"] = [
            [0, 255, 0],
            [0, 255, 100],
            [0, 200, 50],
        ]
        test_config_visualization["visualization"]["waveform"]["num_lines"] = 3
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_style_bars(self, test_config_visualization, tmp_path):
        """Test waveform with bars style."""
        test_config_visualization["visualization"]["waveform"]["waveform_style"] = "bars"
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_style_dots(self, test_config_visualization, tmp_path):
        """Test waveform with dots style."""
        test_config_visualization["visualization"]["waveform"]["waveform_style"] = "dots"
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_style_filled(self, test_config_visualization, tmp_path):
        """Test waveform with filled style."""
        test_config_visualization["visualization"]["waveform"]["waveform_style"] = "filled"
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_opacity(self, test_config_visualization, tmp_path):
        """Test waveform with custom opacity."""
        test_config_visualization["visualization"]["waveform"]["opacity"] = 0.5
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_rotation(self, test_config_visualization, tmp_path):
        """Test waveform with rotation."""
        test_config_visualization["visualization"]["waveform"]["rotation"] = 45.0
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_orientation_offset(self, test_config_visualization, tmp_path):
        """Test waveform with orientation offset."""
        test_config_visualization["visualization"]["waveform"]["orientation_offset"] = 50.0
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_multiple_instances(self, test_config_visualization, tmp_path):
        """Test waveform with multiple instances."""
        test_config_visualization["visualization"]["waveform"]["num_instances"] = 3
        test_config_visualization["visualization"]["waveform"]["instances_offset"] = 20
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_instances_intersect(self, test_config_visualization, tmp_path):
        """Test waveform with instances that can intersect."""
        test_config_visualization["visualization"]["waveform"]["num_instances"] = 2
        test_config_visualization["visualization"]["waveform"]["instances_intersect"] = True
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_amplitude_multiplier(self, test_config_visualization, tmp_path):
        """Test waveform with amplitude multiplier."""
        test_config_visualization["visualization"]["waveform"]["amplitude_multiplier"] = 2.0
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_height_width_percent(self, test_config_visualization, tmp_path):
        """Test waveform with custom height/width percent."""
        test_config_visualization["visualization"]["waveform"]["height_percent"] = 50
        test_config_visualization["visualization"]["waveform"]["width_percent"] = 30
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_left_right_spacing(self, test_config_visualization, tmp_path):
        """Test waveform with left/right spacing."""
        test_config_visualization["visualization"]["waveform"]["left_spacing"] = 50
        test_config_visualization["visualization"]["waveform"]["right_spacing"] = 50
        test_config_visualization["visualization"]["waveform"]["position"] = "left,right"
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_render_scale(self, test_config_visualization, tmp_path):
        """Test waveform with custom render scale."""
        test_config_visualization["visualization"]["waveform"]["render_scale"] = 3.0
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None

    def test_waveform_anti_alias(self, test_config_visualization, tmp_path):
        """Test waveform with anti-aliasing disabled."""
        test_config_visualization["visualization"]["waveform"]["anti_alias"] = False
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.random.randn(44100), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video") as mock_stream,
        ):
            mock_stream.return_value = tmp_path / "output.mp4"
            output = visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")
            assert output is not None


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_audio_file_not_found(self, test_config_visualization, tmp_path):
        """Test error handling when audio file doesn't exist."""
        visualizer = AudioVisualizer(test_config_visualization)
        missing_file = tmp_path / "missing.mp3"
        
        with pytest.raises((FileNotFoundError, ValueError)):
            visualizer.generate_visualization(missing_file, tmp_path / "output.mp4")

    def test_audio_duration_zero(self, test_config_visualization, tmp_path):
        """Test handling of zero-duration audio."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        with (
            patch("librosa.load", return_value=(np.array([]), 22050)),
            patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg", return_value=0.0),
        ):
            with pytest.raises((ValueError, ZeroDivisionError)):
                visualizer.generate_visualization(audio_path, tmp_path / "output.mp4")

    def test_randomize_config(self, test_config_visualization):
        """Test configuration randomization."""
        test_config_visualization["visualization"]["waveform"]["randomize"] = True
        
        visualizer = AudioVisualizer(test_config_visualization)
        
        # Should have randomized some config values
        assert hasattr(visualizer, 'num_lines')
        assert visualizer.num_lines >= 1
        assert visualizer.num_lines <= 5


class TestColorInterpolation:
    """Test color interpolation edge cases."""

    def test_interpolate_color_middle(self, test_config_visualization):
        """Test color interpolation at middle point."""
        visualizer = AudioVisualizer(test_config_visualization)
        color1 = [0, 0, 0]
        color2 = [255, 255, 255]
        result = visualizer._interpolate_color(color1, color2, 0.5)
        
        # Should be approximately in the middle
        assert all(100 < c < 150 for c in result)

    def test_interpolate_color_end(self, test_config_visualization):
        """Test color interpolation at end point."""
        visualizer = AudioVisualizer(test_config_visualization)
        color1 = [0, 0, 0]
        color2 = [255, 255, 255]
        result = visualizer._interpolate_color(color1, color2, 1.0)
        
        assert result == color2


class TestRotatePoints:
    """Test point rotation functionality."""

    def test_rotate_points_90_degrees(self, test_config_visualization):
        """Test rotating points 90 degrees."""
        visualizer = AudioVisualizer(test_config_visualization)
        points = [[10, 0], [20, 0]]
        center = (0, 0)
        rotated = visualizer._rotate_points(points, center, 90.0)
        
        # Rotated 90 degrees: (x, y) -> (-y, x)
        assert len(rotated) == 2
        # Points should have changed
        assert rotated != points

    def test_rotate_points_180_degrees(self, test_config_visualization):
        """Test rotating points 180 degrees."""
        visualizer = AudioVisualizer(test_config_visualization)
        points = [[10, 0], [20, 0]]
        center = (0, 0)
        rotated = visualizer._rotate_points(points, center, 180.0)
        
        # Rotated 180 degrees: (x, y) -> (-x, -y)
        assert len(rotated) == 2

