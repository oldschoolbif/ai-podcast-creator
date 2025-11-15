"""
Tests for AudioVisualizer module
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def test_config_visualization(temp_dir):
    """Create test config with visualization settings."""
    return {
        "video": {
            "resolution": [1920, 1080],
            "fps": 30,
        },
        "visualization": {
            "style": "waveform",
            "primary_color": [0, 150, 255],
            "secondary_color": [255, 100, 200],
            "background_color": [10, 10, 20],
            "blur": 3,
            "sensitivity": 1.0,
        },
    }


@pytest.fixture
def mock_audio_data():
    """Create mock audio data."""
    # Simulate 2 seconds of audio at 22050 Hz
    sr = 22050
    duration = 2.0
    samples = int(sr * duration)
    y = np.random.randn(samples).astype(np.float32) * 0.3
    return y, sr, duration


class TestAudioVisualizerInit:
    """Test AudioVisualizer initialization."""

    def test_init_default_config(self, temp_dir):
        """Test initialization with minimal config."""
        from src.core.audio_visualizer import AudioVisualizer

        config = {"video": {"resolution": [1280, 720], "fps": 24}}
        viz = AudioVisualizer(config)

        assert viz.style == "waveform"  # Default
        assert viz.resolution == [1280, 720]
        assert viz.fps == 24
        assert viz.primary_color == [0, 150, 255]  # Default blue
        assert viz.secondary_color == [255, 100, 200]  # Default pink

    def test_init_custom_style(self, test_config_visualization):
        """Test initialization with custom style."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["style"] = "spectrum"
        viz = AudioVisualizer(test_config_visualization)

        assert viz.style == "spectrum"

    def test_init_custom_colors(self, test_config_visualization):
        """Test initialization with custom colors."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["primary_color"] = [255, 0, 0]
        test_config_visualization["visualization"]["secondary_color"] = [0, 255, 0]
        test_config_visualization["visualization"]["background_color"] = [0, 0, 0]

        viz = AudioVisualizer(test_config_visualization)

        assert viz.primary_color == [255, 0, 0]
        assert viz.secondary_color == [0, 255, 0]
        assert viz.background_color == [0, 0, 0]

    def test_init_custom_sensitivity(self, test_config_visualization):
        """Test initialization with custom sensitivity."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["sensitivity"] = 2.0
        viz = AudioVisualizer(test_config_visualization)

        assert viz.sensitivity == 2.0


class TestColorInterpolation:
    """Test color interpolation functionality."""

    def test_interpolate_color_start(self, test_config_visualization):
        """Test color interpolation at start (t=0)."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        color1 = [100, 200, 300]
        color2 = [400, 500, 600]
        result = viz._interpolate_color(color1, color2, 0.0)

        assert result == color1

    def test_interpolate_color_end(self, test_config_visualization):
        """Test color interpolation at end (t=1)."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        color1 = [100, 200, 300]
        color2 = [400, 500, 600]
        result = viz._interpolate_color(color1, color2, 1.0)

        assert result == color2

    def test_interpolate_color_midpoint(self, test_config_visualization):
        """Test color interpolation at midpoint (t=0.5)."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        color1 = [0, 0, 0]
        color2 = [100, 100, 100]
        result = viz._interpolate_color(color1, color2, 0.5)

        assert result == [50, 50, 50]

    def test_interpolate_color_values(self, test_config_visualization):
        """Test color interpolation produces valid RGB values."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        color1 = [10, 20, 30]
        color2 = [200, 150, 100]

        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = viz._interpolate_color(color1, color2, t)
            assert all(0 <= c <= 255 for c in result)
            assert len(result) == 3


class TestWaveformGeneration:
    """Test waveform frame generation."""

    def test_generate_waveform_frames(self, test_config_visualization, mock_audio_data):
        """Test waveform frame generation."""
        from src.core.audio_visualizer import AudioVisualizer

        y, sr, duration = mock_audio_data

        viz = AudioVisualizer(test_config_visualization)
        # Use the streaming method and convert generator to list
        frame_generator = viz._generate_waveform_frames_streaming_chunked_from_array(y, sr, duration)
        frames = list(frame_generator)

        assert isinstance(frames, list)
        assert len(frames) > 0
        expected_frames = int(duration * viz.fps)
        assert len(frames) == expected_frames

        # Check frame structure
        for frame in frames:
            assert isinstance(frame, np.ndarray)
            assert frame.shape[:2] == tuple(viz.resolution[::-1])  # Height, Width
            assert frame.shape[2] == 3  # RGB

    def test_generate_waveform_small_audio(self, test_config_visualization):
        """Test waveform generation with very small audio."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        # Use non-empty but very small audio to avoid NaN/empty issues
        y = np.array([0.1, -0.1, 0.05] * 100, dtype=np.float32)  # 300 samples
        sr = 22050
        duration = 0.1  # ~2205 samples for 0.1s, but we have 300 - will work with math

        # Use the streaming method and convert generator to list
        frame_generator = viz._generate_waveform_frames_streaming_chunked_from_array(y, sr, duration)
        frames = list(frame_generator)

        assert isinstance(frames, list)
        # Should still generate at least 1 frame
        assert len(frames) >= 1


class TestWaveformHelpers:
    """Test helper utilities for waveform rendering."""

    def test_get_orientation_manual_override(self, test_config_visualization):
        """Custom orientation config should override automatic detection."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["waveform"] = {
            "orientation": "vertical"
        }
        viz = AudioVisualizer(test_config_visualization)

        # Even though "top" normally maps to horizontal, manual override wins
        assert viz._get_orientation("top") == "vertical"

    def test_get_orientation_auto_detection(self, test_config_visualization):
        """Auto orientation should map left/right to vertical, others to horizontal."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["waveform"] = {}
        viz = AudioVisualizer(test_config_visualization)

        assert viz._get_orientation("left") == "vertical"
        assert viz._get_orientation("right") == "vertical"
        assert viz._get_orientation("bottom") == "horizontal"

    def test_rotate_points_quarter_turn(self, test_config_visualization):
        """Points should rotate 90 degrees around the origin."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        points = [(1, 0), (0, 1)]
        rotated = viz._rotate_points(points, center=(0, 0), angle_degrees=90)

        assert rotated[0] == (0, 1)
        # Allow small rounding differences
        assert rotated[1][0] == -1
        assert rotated[1][1] == 0


class TestAdvancedWaveformRendering:
    """Test advanced waveform rendering options."""

    def test_amplitude_multiplier_propagates(self, monkeypatch, test_config_visualization):
        """Amplitude multiplier should be applied before rendering (PIL fallback path)."""
        from src.core import audio_visualizer
        from src.core.audio_visualizer import AudioVisualizer

        # Force PIL path to avoid OpenCV dependency
        monkeypatch.setattr(audio_visualizer, "OPENCV_AVAILABLE", False)

        test_config_visualization["video"]["resolution"] = [64, 36]
        test_config_visualization["video"]["fps"] = 5
        test_config_visualization["visualization"]["waveform"] = {
            "anti_alias": False,
            "amplitude_multiplier": 1.7,
            "num_lines": 1,
            "line_thickness": 4,
        }

        viz = AudioVisualizer(test_config_visualization)

        captured_amplitudes = []

        def fake_draw(self, draw, chunk, amplitude, width, height, position, base_thickness):
            captured_amplitudes.append(amplitude)

        monkeypatch.setattr(AudioVisualizer, "_draw_waveform_pil", fake_draw)

        sr = 50
        duration = 1.0
        y = np.ones(int(sr * duration), dtype=np.float32)

        frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(y, sr, duration))

        assert len(frames) == int(duration * viz.fps)
        assert captured_amplitudes
        # Peak and RMS are both 1.0 for the constant signal -> amplitude == multiplier
        for amp in captured_amplitudes:
            assert amp == pytest.approx(viz.amplitude_multiplier, rel=1e-3)

    def test_opencv_rendering_multiline_configuration(self, monkeypatch, test_config_visualization):
        """OpenCV path should honor multi-line, multi-position, and opacity settings."""
        from types import SimpleNamespace

        from src.core import audio_visualizer
        from src.core.audio_visualizer import AudioVisualizer
        import numpy as np

        draw_calls = []

        def fake_resize(frame, size, interpolation):
            return np.zeros((size[1], size[0], 3), dtype=np.uint8)

        def fake_polylines(frame, pts, isClosed, color, thickness, lineType):
            draw_calls.append(
                {
                    "color": color,
                    "thickness": thickness,
                    "num_points": len(pts[0]) if pts else 0,
                }
            )

        def fake_line(frame, pt1, pt2, color, thickness, lineType=None):
            draw_calls.append(
                {
                    "color": color,
                    "thickness": thickness,
                    "num_points": 2,
                }
            )

        fake_cv2 = SimpleNamespace(
            INTER_LANCZOS4=4,
            LINE_AA=16,
            resize=fake_resize,
            polylines=fake_polylines,
            line=fake_line,
        )

        monkeypatch.setattr(audio_visualizer, "cv2", fake_cv2, raising=False)
        monkeypatch.setattr(audio_visualizer, "OPENCV_AVAILABLE", True)

        test_config_visualization["video"]["resolution"] = [96, 64]
        test_config_visualization["video"]["fps"] = 4
        test_config_visualization["visualization"]["waveform"] = {
            "render_scale": 1.0,
            "anti_alias": True,
            "num_lines": 2,
            "line_thickness": [3, 5],
            "line_colors": [[10, 20, 30], [40, 50, 60]],
            "position": "top,left",
            "orientation_offset": 75,
            "height_percent": 40,
            "width_percent": 35,
            "left_spacing": 6,
            "right_spacing": 8,
            "rotation": 15,
            "num_instances": 2,
            "instances_offset": 4,
            "opacity": 0.5,
            "amplitude_multiplier": 1.0,
        }

        viz = AudioVisualizer(test_config_visualization)

        sr = 40
        duration = 1.0
        y = np.ones(int(sr * duration), dtype=np.float32)

        frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(y, sr, duration))

        expected_frames = int(duration * viz.fps)
        assert len(frames) == expected_frames
        assert draw_calls, "OpenCV polylines should be invoked"

        positions = [p.strip() for p in viz.position.split(",")]
        expected_calls = expected_frames * len(positions) * viz.num_instances * viz.num_lines
        assert len(draw_calls) >= expected_calls

        # Colors should respect opacity scaling
        expected_color = tuple(int(c * viz.opacity) for c in viz.line_colors[0])
        assert draw_calls[0]["color"] == expected_color

        expected_thickness = max(1, int(test_config_visualization["visualization"]["waveform"]["line_thickness"][0] * viz.render_scale))
        assert draw_calls[0]["thickness"] == expected_thickness


class TestSpectrumGeneration:
    """Test spectrum frame generation."""

    @pytest.mark.skip(reason="librosa.stft has lazy loading that conflicts with mocking")
    def test_generate_spectrum_frames(self, test_config_visualization, mock_audio_data):
        """Test spectrum frame generation - skipped due to librosa lazy loading."""
        pass


class TestCircularGeneration:
    """Test circular/radial frame generation."""

    def test_generate_circular_frames(self, test_config_visualization, mock_audio_data):
        """Test circular frame generation."""
        from src.core.audio_visualizer import AudioVisualizer

        y, sr, duration = mock_audio_data

        viz = AudioVisualizer(test_config_visualization)
        # Use the streaming method and convert generator to list
        frame_generator = viz._generate_circular_frames_streaming(y, sr, duration)
        frames = list(frame_generator)

        assert isinstance(frames, list)
        assert len(frames) > 0
        expected_frames = int(duration * viz.fps)
        assert len(frames) == expected_frames

        # Check frame structure
        for frame in frames:
            assert isinstance(frame, np.ndarray)
            assert frame.shape[:2] == tuple(viz.resolution[::-1])


class TestParticleGeneration:
    """Test particle frame generation."""

    def test_generate_particle_frames(self, test_config_visualization, mock_audio_data):
        """Test particle frame generation."""
        from src.core.audio_visualizer import AudioVisualizer

        y, sr, duration = mock_audio_data

        viz = AudioVisualizer(test_config_visualization)
        # Use the streaming method and convert generator to list
        frame_generator = viz._generate_particle_frames_streaming_chunked_from_array(y, sr, duration)
        frames = list(frame_generator)

        assert isinstance(frames, list)
        assert len(frames) > 0
        expected_frames = int(duration * viz.fps)
        assert len(frames) == expected_frames

        # Check frame structure
        for frame in frames:
            assert isinstance(frame, np.ndarray)
            assert frame.shape[:2] == tuple(viz.resolution[::-1])


class TestStyleSelection:
    """Test style selection logic."""

    def test_waveform_style_selected(self, test_config_visualization):
        """Test waveform style is set correctly."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["style"] = "waveform"
        viz = AudioVisualizer(test_config_visualization)
        assert viz.style == "waveform"

    def test_spectrum_style_selected(self, test_config_visualization):
        """Test spectrum style is set correctly."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["style"] = "spectrum"
        viz = AudioVisualizer(test_config_visualization)
        assert viz.style == "spectrum"

    def test_circular_style_selected(self, test_config_visualization):
        """Test circular style is set correctly."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["style"] = "circular"
        viz = AudioVisualizer(test_config_visualization)
        assert viz.style == "circular"

    def test_particles_style_selected(self, test_config_visualization):
        """Test particles style is set correctly."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["style"] = "particles"
        viz = AudioVisualizer(test_config_visualization)
        assert viz.style == "particles"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_resolution_config(self, test_config_visualization):
        """Test visualization respects resolution config."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["video"]["resolution"] = [1280, 720]
        viz = AudioVisualizer(test_config_visualization)

        assert viz.resolution == [1280, 720]

    def test_fps_config(self, test_config_visualization):
        """Test visualization respects FPS config."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["video"]["fps"] = 24
        viz = AudioVisualizer(test_config_visualization)

        assert viz.fps == 24

    def test_default_style_fallback(self, temp_dir):
        """Test that unknown style is set but defaults during generate."""
        from src.core.audio_visualizer import AudioVisualizer

        config = {
            "video": {"resolution": [1280, 720], "fps": 30},
            "visualization": {"style": "unknown_style"},
        }
        viz = AudioVisualizer(config)

        # Style is set to what was configured
        assert viz.style == "unknown_style"
        # But will fallback to waveform during generate() call

    @patch("src.core.audio_visualizer.librosa.load")
    @patch("src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg")
    @patch("src.core.audio_visualizer.AudioVisualizer._generate_waveform_frames_streaming_chunked")
    @patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video")
    def test_generate_visualization_calls_load_and_duration(self, mock_stream_video, mock_waveform, mock_get_duration, mock_load, test_config_visualization, temp_dir):
        """Test that generate_visualization loads audio and gets duration (lines 44-45)."""
        from src.core.audio_visualizer import AudioVisualizer

        import numpy as np

        y_data = np.random.randn(1000).astype(np.float32)
        mock_load.return_value = (y_data, 22050)
        mock_get_duration.return_value = 2.0  # FFmpeg method returns float directly
        # Mock returns a generator that yields frames
        mock_waveform.return_value = iter([np.zeros((720, 1280, 3), dtype=np.uint8)])
        mock_stream_video.return_value = temp_dir / "output.mp4"

        viz = AudioVisualizer(test_config_visualization)
        audio_path = temp_dir / "test.wav"
        output_path = temp_dir / "output.mp4"
        audio_path.write_bytes(b"fake audio")

        result = viz.generate_visualization(audio_path, output_path)

        # Verify librosa was called for sample rate detection
        assert mock_load.called
        # _get_audio_duration_ffmpeg called to get audio duration
        assert mock_get_duration.called
        assert result == mock_stream_video.return_value

    @patch("src.core.audio_visualizer.librosa.load")
    @patch("src.core.audio_visualizer.librosa")
    @patch("src.core.audio_visualizer.AudioVisualizer._generate_spectrum_frames_streaming_chunked")
    @patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video")
    def test_generate_visualization_spectrum_style(self, mock_stream_video, mock_spectrum, mock_get_duration, mock_load, test_config_visualization, temp_dir):
        """Test generate_visualization with spectrum style (lines 50-51)."""
        from src.core.audio_visualizer import AudioVisualizer

        import numpy as np

        test_config_visualization["visualization"]["style"] = "spectrum"
        y_data = np.random.randn(1000).astype(np.float32)
        mock_load.return_value = (y_data, 22050)
        mock_get_duration.get_duration.return_value = 2.0
        # Mock returns a generator that yields frames
        mock_spectrum.return_value = iter([np.zeros((720, 1280, 3), dtype=np.uint8)])
        mock_stream_video.return_value = temp_dir / "output.mp4"

        viz = AudioVisualizer(test_config_visualization)
        audio_path = temp_dir / "test.wav"
        output_path = temp_dir / "output.mp4"
        audio_path.write_bytes(b"fake audio")

        result = viz.generate_visualization(audio_path, output_path)

        assert mock_spectrum.called
        assert result == mock_stream_video.return_value

    @patch("src.core.audio_visualizer.librosa.load")
    @patch("src.core.audio_visualizer.librosa")
    @patch("src.core.audio_visualizer.AudioVisualizer._generate_particle_frames_streaming_chunked")
    @patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video")
    def test_generate_visualization_particles_style(self, mock_stream_video, mock_particles, mock_get_duration, mock_load, test_config_visualization, temp_dir):
        """Test generate_visualization with particles style (lines 54-55)."""
        from src.core.audio_visualizer import AudioVisualizer

        import numpy as np

        test_config_visualization["visualization"]["style"] = "particles"
        y_data = np.random.randn(1000).astype(np.float32)
        mock_load.return_value = (y_data, 22050)
        mock_get_duration.get_duration.return_value = 2.0
        # Mock returns a generator that yields frames
        mock_particles.return_value = iter([np.zeros((720, 1280, 3), dtype=np.uint8)])
        mock_stream_video.return_value = temp_dir / "output.mp4"

        viz = AudioVisualizer(test_config_visualization)
        audio_path = temp_dir / "test.wav"
        output_path = temp_dir / "output.mp4"
        audio_path.write_bytes(b"fake audio")

        result = viz.generate_visualization(audio_path, output_path)

        assert mock_particles.called
        assert result == mock_stream_video.return_value

    @patch("src.core.audio_visualizer.librosa.load")
    @patch("src.core.audio_visualizer.librosa")
    @patch("src.core.audio_visualizer.AudioVisualizer._generate_waveform_frames_streaming_chunked")
    @patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video")
    def test_generate_visualization_default_fallback(self, mock_stream_video, mock_waveform, mock_get_duration, mock_load, test_config_visualization, temp_dir):
        """Test generate_visualization defaults to waveform for unknown style (lines 56-58)."""
        from src.core.audio_visualizer import AudioVisualizer

        import numpy as np

        test_config_visualization["visualization"]["style"] = "unknown_style_xyz"
        y_data = np.random.randn(1000).astype(np.float32)
        mock_load.return_value = (y_data, 22050)
        mock_get_duration.get_duration.return_value = 2.0
        # Mock returns a generator that yields frames
        mock_waveform.return_value = iter([np.zeros((720, 1280, 3), dtype=np.uint8)])
        mock_stream_video.return_value = temp_dir / "output.mp4"

        viz = AudioVisualizer(test_config_visualization)
        audio_path = temp_dir / "test.wav"
        output_path = temp_dir / "output.mp4"
        audio_path.write_bytes(b"fake audio")

        result = viz.generate_visualization(audio_path, output_path)

        # Should fallback to waveform
        assert mock_waveform.called
        assert result == mock_stream_video.return_value

    @patch("src.core.audio_visualizer.librosa.load")
    @patch("src.core.audio_visualizer.librosa")
    @patch("src.core.audio_visualizer.AudioVisualizer._generate_circular_frames_streaming_chunked")
    @patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video")
    def test_generate_visualization_circular_style(self, mock_stream_video, mock_circular, mock_get_duration, mock_load, test_config_visualization, temp_dir):
        """Test generate_visualization with circular style (lines 52-53)."""
        from src.core.audio_visualizer import AudioVisualizer

        import numpy as np

        test_config_visualization["visualization"]["style"] = "circular"
        y_data = np.random.randn(1000).astype(np.float32)
        mock_load.return_value = (y_data, 22050)
        mock_get_duration.get_duration.return_value = 2.0
        # Mock returns a generator that yields frames
        mock_circular.return_value = iter([np.zeros((720, 1280, 3), dtype=np.uint8)])
        mock_stream_video.return_value = temp_dir / "output.mp4"

        viz = AudioVisualizer(test_config_visualization)
        audio_path = temp_dir / "test.wav"
        output_path = temp_dir / "output.mp4"
        audio_path.write_bytes(b"fake audio")

        result = viz.generate_visualization(audio_path, output_path)

        assert mock_circular.called
        assert result == mock_stream_video.return_value

    @patch("src.core.audio_visualizer.librosa.load")
    @patch("src.core.audio_visualizer.librosa")
    @patch("src.core.audio_visualizer.AudioVisualizer._generate_waveform_frames_streaming_chunked_from_array")
    @patch("src.core.audio_visualizer.AudioVisualizer._stream_frames_to_video")
    @patch("builtins.print")
    def test_generate_visualization_print_statements(self, mock_print, mock_stream_video, mock_waveform, mock_get_duration, mock_load, test_config_visualization, temp_dir):
        """Test generate_visualization print statements (lines 41, 63)."""
        from src.core.audio_visualizer import AudioVisualizer

        import numpy as np

        y_data = np.random.randn(1000).astype(np.float32)
        mock_load.return_value = (y_data, 22050)
        mock_get_duration.get_duration.return_value = 2.0
        mock_waveform.return_value = iter([np.zeros((720, 1280, 3), dtype=np.uint8)])
        mock_stream_video.return_value = temp_dir / "output.mp4"

        viz = AudioVisualizer(test_config_visualization)
        audio_path = temp_dir / "test.wav"
        output_path = temp_dir / "output.mp4"
        audio_path.write_bytes(b"fake audio")

        result = viz.generate_visualization(audio_path, output_path)

        # Verify print statements were called (lines 41, 63)
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Generating" in call for call in print_calls) or any("visualization" in call.lower() for call in print_calls)
        assert any("Visualization generated" in call for call in print_calls) or any("generated" in call.lower() for call in print_calls)

    # Note: Spectrum generation internal tests removed due to librosa.stft lazy loading
    # These methods (lines 137-179) require integration tests with real librosa

    def test_waveform_sample_index_boundary(self, test_config_visualization, mock_audio_data):
        """Test waveform generation handles sample index boundary (line 101)."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        
        # Test with audio that triggers boundary condition
        y, sr, duration = mock_audio_data
        # Use very small chunk to trigger boundary
        y_small = y[:100]  # Very small audio
        
        frame_generator = viz._generate_waveform_frames_streaming_chunked_from_array(y_small, sr, 0.1)
        frames = list(frame_generator)

        assert isinstance(frames, list)
        assert len(frames) > 0

    def test_circular_line_amplitude_zero(self, test_config_visualization):
        """Test circular generation handles zero amplitude fallback (line 229)."""
        from src.core.audio_visualizer import AudioVisualizer

        import numpy as np

        viz = AudioVisualizer(test_config_visualization)
        # Use audio that might trigger the boundary condition
        y = np.zeros(1000, dtype=np.float32)  # Silent audio
        sr = 22050
        duration = 0.1

        frame_generator = viz._generate_circular_frames_streaming(y, sr, duration)
        frames = list(frame_generator)

        assert isinstance(frames, list)

    # Note: _frames_to_video test removed due to complex moviepy mocking requirements
    # This method (lines 329-349) can be tested via integration tests with real moviepy
    
    def test_output_directory_created(self, test_config_visualization, temp_dir):
        """Test that output directory is created before writing video file.
        
        This test verifies the fix for file opening errors when the output
        directory doesn't exist. The _stream_frames_to_video method should
        create the parent directory before attempting to write the output file.
        """
        from src.core.audio_visualizer import AudioVisualizer
        from pathlib import Path
        
        viz = AudioVisualizer(test_config_visualization)
        
        # Create a nested directory path that doesn't exist
        nested_dir = temp_dir / "nested" / "deep" / "path"
        output_path = nested_dir / "output.mp4"
        audio_path = temp_dir / "test.wav"
        audio_path.write_bytes(b"fake audio")
        
        # Verify directory doesn't exist yet
        assert not nested_dir.exists()
        
        # Ensure ram_monitor module is imported so that patch lookup succeeds
        ram_module = None
        with patch.dict('sys.modules', {'psutil': MagicMock()}):
            import importlib

            utils_pkg = importlib.import_module('src.utils')
            ram_module = importlib.import_module('src.utils.ram_monitor')
            setattr(utils_pkg, 'ram_monitor', ram_module)
        
        # Verify the directory creation code is executed
        # We'll just check that mkdir is called on the parent path
        # The actual fix is at line 385: output_path.parent.mkdir(parents=True, exist_ok=True)
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            # Mock subprocess to avoid actual FFmpeg execution
            with patch('subprocess.Popen') as mock_popen:
                # Mock FFmpeg process
                mock_process = MagicMock()
                mock_process.poll.return_value = None  # Process is still running
                mock_process.stdin = MagicMock()
                mock_process.stderr = MagicMock()
                mock_process.stderr.readline.return_value = b''
                mock_popen.return_value = mock_process
                
                # Mock threading and other dependencies
                with patch('threading.Thread'), \
                     patch('src.utils.file_monitor.FileMonitor'), \
                     patch.object(ram_module, 'RAMMonitor'):
                    # Mock frame generator
                    import numpy as np
                    def mock_frame_gen():
                        yield np.zeros((1080, 1920, 3), dtype=np.uint8)
                        return
                    
                    # This should create the directory before writing
                    try:
                        viz._stream_frames_to_video(
                            mock_frame_gen(),
                            audio_path,
                            output_path,
                            duration=0.1
                        )
                    except Exception:
                        # Expected to fail due to mocking, but mkdir should be called
                        pass
        
        # Verify mkdir was called on the parent directory
        # This confirms the fix is working
        assert mock_mkdir.called, "mkdir should be called on output_path.parent"
        # Check that it was called with parents=True and exist_ok=True
        call_args = mock_mkdir.call_args
        assert call_args is not None, "mkdir should be called with arguments"
        assert call_args.kwargs.get('parents') == True, "mkdir should be called with parents=True"
        assert call_args.kwargs.get('exist_ok') == True, "mkdir should be called with exist_ok=True"


@pytest.mark.unit
def test_generate_visualization_dispatches_particles(tmp_path, monkeypatch):
    from src.core.audio_visualizer import AudioVisualizer

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"audio")
    output_path = tmp_path / "output.mp4"

    config = {
        "video": {"resolution": [320, 240], "fps": 24},
        "visualization": {"style": "particles"},
    }
    viz = AudioVisualizer(config)

    monkeypatch.setattr(
        "src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg",
        lambda self, path: 0.5,
    )
    monkeypatch.setattr("librosa.load", lambda *args, **kwargs: (np.zeros(10, dtype=np.float32), 22050))

    frame_iter = iter([np.zeros((10, 10, 3), dtype=np.uint8)])

    with patch.object(
        AudioVisualizer, "_generate_particle_frames_streaming_chunked", return_value=frame_iter
    ) as mock_generator, patch.object(
        AudioVisualizer, "_stream_frames_to_video", return_value=output_path
    ) as mock_stream:
        result = viz.generate_visualization(audio_path, output_path)

    assert result == output_path
    mock_generator.assert_called_once()
    mock_stream.assert_called_once()


@pytest.mark.unit
def test_generate_visualization_dispatches_circular(tmp_path, monkeypatch):
    from src.core.audio_visualizer import AudioVisualizer

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"audio")
    output_path = tmp_path / "output.mp4"

    config = {
        "video": {"resolution": [320, 240], "fps": 24},
        "visualization": {"style": "circular"},
    }
    viz = AudioVisualizer(config)

    monkeypatch.setattr(
        "src.core.audio_visualizer.AudioVisualizer._get_audio_duration_ffmpeg",
        lambda self, path: 0.5,
    )
    monkeypatch.setattr("librosa.load", lambda *args, **kwargs: (np.zeros(10, dtype=np.float32), 22050))

    frame_iter = iter([np.zeros((10, 10, 3), dtype=np.uint8)])

    with patch.object(
        AudioVisualizer, "_generate_circular_frames_streaming_chunked", return_value=frame_iter
    ) as mock_generator, patch.object(
        AudioVisualizer, "_stream_frames_to_video", return_value=output_path
    ) as mock_stream:
        result = viz.generate_visualization(audio_path, output_path)

    assert result == output_path
    mock_generator.assert_called_once()
    mock_stream.assert_called_once()


@pytest.mark.unit
def test_waveform_streaming_chunked_handles_librosa_failure(tmp_path, monkeypatch):
    from src.core.audio_visualizer import AudioVisualizer

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"audio")

    config = {
        "video": {"resolution": [128, 72], "fps": 5},
        "visualization": {"style": "waveform"},
    }
    viz = AudioVisualizer(config)

    monkeypatch.setattr("src.core.audio_visualizer.OPENCV_AVAILABLE", False, raising=False)

    def failing_load(*args, **kwargs):
        raise RuntimeError("load error")

    monkeypatch.setattr("librosa.load", failing_load)

    generator = viz._generate_waveform_frames_streaming_chunked(audio_path, sr=22050, duration=0.2)
    frame = next(generator)
    assert frame.shape == (72, 128, 3)


class TestAudioVisualizerUncoveredMethods:
    """Test methods that need coverage improvement."""

    def test_randomize_config(self, test_config_visualization):
        """Test _randomize_config method."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["waveform"] = {"randomize": True}
        viz = AudioVisualizer(test_config_visualization)

        # Verify randomization was applied
        assert 1 <= viz.num_lines <= 5
        assert isinstance(viz.line_thickness, (int, list))
        assert viz.position in ["top", "bottom", "left", "right", "middle"] or "," in viz.position
        assert 10 <= viz.height_percent <= 40
        assert 10 <= viz.width_percent <= 40
        assert 0.7 <= viz.opacity <= 1.0

    def test_get_audio_duration_ffmpeg_success(self, test_config_visualization, tmp_path):
        """Test _get_audio_duration_ffmpeg success path."""
        from src.core.audio_visualizer import AudioVisualizer

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"mp3")
        viz = AudioVisualizer(test_config_visualization)

        with patch("src.core.audio_visualizer.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "10.5\n"
            duration = viz._get_audio_duration_ffmpeg(audio_path)

        assert duration == 10.5

    def test_get_audio_duration_ffmpeg_failure(self, test_config_visualization, tmp_path):
        """Test _get_audio_duration_ffmpeg failure path."""
        from src.core.audio_visualizer import AudioVisualizer

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"mp3")
        viz = AudioVisualizer(test_config_visualization)

        with patch("src.core.audio_visualizer.subprocess.run", side_effect=FileNotFoundError("ffprobe not found")):
            duration = viz._get_audio_duration_ffmpeg(audio_path)

        assert duration is None

    def test_get_audio_duration_ffmpeg_timeout(self, test_config_visualization, tmp_path):
        """Test _get_audio_duration_ffmpeg timeout handling."""
        from src.core.audio_visualizer import AudioVisualizer
        import subprocess

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"mp3")
        viz = AudioVisualizer(test_config_visualization)

        with patch("src.core.audio_visualizer.subprocess.run", side_effect=subprocess.TimeoutExpired("ffprobe", 10)):
            duration = viz._get_audio_duration_ffmpeg(audio_path)

        assert duration is None

    def test_cleanup_ffmpeg_process_none(self, test_config_visualization):
        """Test _cleanup_ffmpeg_process with None process."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        # Should not raise exception
        viz._cleanup_ffmpeg_process(None)

    def test_cleanup_ffmpeg_process_graceful(self, test_config_visualization):
        """Test _cleanup_ffmpeg_process with graceful termination."""
        from src.core.audio_visualizer import AudioVisualizer
        import subprocess

        viz = AudioVisualizer(test_config_visualization)

        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running
        mock_process.stdin = MagicMock()
        mock_process.stdin.closed = False
        mock_process.stderr = MagicMock()
        mock_process.stderr.closed = False
        mock_process.stdout = MagicMock()
        mock_process.stdout.closed = False
        mock_process.wait.return_value = 0

        viz._cleanup_ffmpeg_process(mock_process, timeout=1.0)

        mock_process.stdin.close.assert_called_once()
        mock_process.stderr.close.assert_called_once()
        mock_process.stdout.close.assert_called_once()
        mock_process.terminate.assert_called_once()

    def test_get_orientation_auto_detection(self, test_config_visualization):
        """Test _get_orientation with auto-detection."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["waveform"] = {"orientation": "auto"}
        viz = AudioVisualizer(test_config_visualization)

        # Test auto-detection for horizontal positions
        assert viz._get_orientation("top") == "horizontal"
        assert viz._get_orientation("bottom") == "horizontal"
        assert viz._get_orientation("middle") == "horizontal"

        # Test auto-detection for vertical positions
        assert viz._get_orientation("left") == "vertical"
        assert viz._get_orientation("right") == "vertical"

        # Test default fallback
        assert viz._get_orientation("unknown") == "horizontal"

    def test_get_orientation_explicit(self, test_config_visualization):
        """Test _get_orientation with explicit orientation."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_visualization["visualization"]["waveform"] = {"orientation": "vertical"}
        viz = AudioVisualizer(test_config_visualization)

        # Should return explicit orientation regardless of position
        assert viz._get_orientation("top") == "vertical"
        assert viz._get_orientation("bottom") == "vertical"
        assert viz._get_orientation("left") == "vertical"

    def test_rotate_points(self, test_config_visualization):
        """Test _rotate_points method."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)

        # Test with zero rotation (should return same points)
        points = [(10, 20), (30, 40), (50, 60)]
        center = (0, 0)
        result = viz._rotate_points(points, center, 0)
        assert result == points

        # Test with 90 degree rotation
        points = [(10, 0), (0, 10)]
        center = (0, 0)
        result = viz._rotate_points(points, center, 90)
        # After 90° rotation: (10, 0) -> (0, 10), (0, 10) -> (-10, 0)
        assert len(result) == 2
        assert result[0] == (0, 10)  # (10, 0) rotated 90° around (0, 0) = (0, 10)

    def test_get_audio_duration_ffmpeg_returncode_nonzero(self, test_config_visualization, tmp_path):
        """Test _get_audio_duration_ffmpeg when returncode is non-zero."""
        from src.core.audio_visualizer import AudioVisualizer

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"mp3")
        viz = AudioVisualizer(test_config_visualization)

        with patch("src.core.audio_visualizer.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            duration = viz._get_audio_duration_ffmpeg(audio_path)

        assert duration is None

    def test_get_audio_duration_ffmpeg_empty_stdout(self, test_config_visualization, tmp_path):
        """Test _get_audio_duration_ffmpeg when stdout is empty."""
        from src.core.audio_visualizer import AudioVisualizer

        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"mp3")
        viz = AudioVisualizer(test_config_visualization)

        with patch("src.core.audio_visualizer.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""  # Empty stdout
            duration = viz._get_audio_duration_ffmpeg(audio_path)

        assert duration is None

    def test_draw_waveform_pil_fallback(self, test_config_visualization, tmp_path):
        """Test _draw_waveform_pil fallback when OpenCV not available."""
        from src.core.audio_visualizer import AudioVisualizer
        import numpy as np

        # Disable OpenCV
        with patch("src.core.audio_visualizer.OPENCV_AVAILABLE", False):
            viz = AudioVisualizer(test_config_visualization)
            
            # Create a simple frame and chunk
            frame = np.zeros((100, 200, 3), dtype=np.uint8)
            chunk = np.random.randn(1000).astype(np.float32) * 0.3
            amplitude = 0.5
            
            # Should not raise exception
            viz._draw_waveform_pil(
                MagicMock(),  # draw object
                chunk,
                amplitude,
                200,
                100,
                "bottom",
                12
            )

    def test_cleanup_ffmpeg_process_force_kill(self, test_config_visualization):
        """Test _cleanup_ffmpeg_process with force kill."""
        from src.core.audio_visualizer import AudioVisualizer
        import subprocess

        viz = AudioVisualizer(test_config_visualization)

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdin = MagicMock()
        mock_process.stdin.closed = False
        mock_process.stderr = MagicMock()
        mock_process.stderr.closed = False
        mock_process.stdout = MagicMock()
        mock_process.stdout.closed = False
        mock_process.wait.side_effect = [subprocess.TimeoutExpired("ffmpeg", 1.0), None]

        viz._cleanup_ffmpeg_process(mock_process, timeout=0.1)

        mock_process.kill.assert_called_once()
        assert mock_process.wait.call_count == 2

    def test_cleanup_ffmpeg_process_terminate_exception(self, test_config_visualization):
        """Test _cleanup_ffmpeg_process when terminate raises exception."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.stdin = MagicMock()
        mock_process.stdin.closed = False
        mock_process.stderr = MagicMock()
        mock_process.stderr.closed = False
        mock_process.stdout = MagicMock()
        mock_process.stdout.closed = False
        mock_process.terminate.side_effect = Exception("Terminate failed")
        mock_process.wait.return_value = 0

        # Should not raise exception, should try kill
        viz._cleanup_ffmpeg_process(mock_process)

        mock_process.kill.assert_called_once()

    def test_interpolate_color(self, test_config_visualization):
        """Test _interpolate_color method."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)

        # Test at start (t=0)
        result = viz._interpolate_color([0, 0, 0], [255, 255, 255], 0.0)
        assert result == [0, 0, 0]

        # Test at end (t=1)
        result = viz._interpolate_color([0, 0, 0], [255, 255, 255], 1.0)
        assert result == [255, 255, 255]

        # Test at middle (t=0.5)
        result = viz._interpolate_color([0, 0, 0], [255, 255, 255], 0.5)
        assert result == [127, 127, 127]

        # Test with custom colors
        result = viz._interpolate_color([100, 50, 200], [200, 150, 50], 0.3)
        assert len(result) == 3
        assert all(isinstance(c, int) for c in result)

    def test_get_orientation_auto_detection(self, test_config_visualization):
        """Test _get_orientation auto-detection for different positions."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        
        # Test auto-detection for horizontal positions
        assert viz._get_orientation("top") == "horizontal"
        assert viz._get_orientation("bottom") == "horizontal"
        assert viz._get_orientation("middle") == "horizontal"
        
        # Test auto-detection for vertical positions
        assert viz._get_orientation("left") == "vertical"
        assert viz._get_orientation("right") == "vertical"
        
        # Test explicit orientation override
        test_config_visualization["visualization"]["waveform"] = {"orientation": "vertical"}
        viz2 = AudioVisualizer(test_config_visualization)
        assert viz2._get_orientation("top") == "vertical"  # Override takes precedence

    def test_rotate_points(self, test_config_visualization):
        """Test _rotate_points method for point rotation."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        
        # Test no rotation (0 degrees)
        points = [(10, 10), (20, 10), (20, 20)]
        center = (15, 15)
        result = viz._rotate_points(points, center, 0)
        assert result == points  # Should return unchanged
        
        # Test 90 degree rotation
        points = [(0, 0), (10, 0), (10, 10)]
        center = (5, 5)
        result = viz._rotate_points(points, center, 90)
        # After 90° rotation around (5,5), points should be rotated
        assert len(result) == 3
        assert all(isinstance(p, tuple) and len(p) == 2 for p in result)
        
        # Test 180 degree rotation
        points = [(0, 0)]
        center = (5, 5)
        result = viz._rotate_points(points, center, 180)
        assert len(result) == 1
        # Point should be rotated 180 degrees around center
        assert result[0][0] == 10
        assert result[0][1] == 10

    def test_draw_waveform_pil_fallback(self, test_config_visualization, tmp_path):
        """Test _draw_waveform_pil fallback method."""
        from src.core.audio_visualizer import AudioVisualizer
        from PIL import Image, ImageDraw
        import numpy as np

        viz = AudioVisualizer(test_config_visualization)
        
        # Create a test image and draw object
        img = Image.new('RGB', (800, 600), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Create test audio chunk
        chunk = np.random.randn(1000).astype(np.float32) * 0.5
        
        # Test drawing waveform at different positions
        viz._draw_waveform_pil(draw, chunk, amplitude=1.0, width=800, height=600, 
                               position="bottom", base_thickness=2)
        
        # Test top position
        img2 = Image.new('RGB', (800, 600), color=(0, 0, 0))
        draw2 = ImageDraw.Draw(img2)
        viz._draw_waveform_pil(draw2, chunk, amplitude=1.0, width=800, height=600,
                               position="top", base_thickness=2)
        
        # Test middle position
        img3 = Image.new('RGB', (800, 600), color=(0, 0, 0))
        draw3 = ImageDraw.Draw(img3)
        viz._draw_waveform_pil(draw3, chunk, amplitude=0.5, width=800, height=600,
                               position="middle", base_thickness=2)
        
        # If no exception raised, test passed
        assert True

    def test_cleanup_ffmpeg_process_none(self, test_config_visualization):
        """Test _cleanup_ffmpeg_process with None process."""
        from src.core.audio_visualizer import AudioVisualizer

        viz = AudioVisualizer(test_config_visualization)
        
        # Should not raise exception
        viz._cleanup_ffmpeg_process(None)

    def test_cleanup_ffmpeg_process_already_closed(self, test_config_visualization):
        """Test _cleanup_ffmpeg_process with already closed handles."""
        from src.core.audio_visualizer import AudioVisualizer
        from unittest.mock import MagicMock

        viz = AudioVisualizer(test_config_visualization)
        
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running
        mock_process.stdin = MagicMock()
        mock_process.stdin.closed = True  # Already closed
        mock_process.stderr = MagicMock()
        mock_process.stderr.closed = True
        mock_process.stdout = MagicMock()
        mock_process.stdout.closed = True
        mock_process.terminate.return_value = None
        mock_process.wait.return_value = 0
        
        # Should handle already-closed handles gracefully
        viz._cleanup_ffmpeg_process(mock_process)

    # Note: _stream_frames_to_video is complex and requires real FFmpeg process mocking
    # These tests are skipped as they require extensive mocking that may not be reliable
    # The method is tested indirectly through generate_visualization integration tests

    # Note: Randomization tests are complex due to module-level random import


# ============================================================================
# Tests for _stream_frames_to_video error paths
# ============================================================================

@pytest.mark.unit
def test_stream_frames_to_video_process_dies(tmp_path, test_config_visualization):
    """Test _stream_frames_to_video handles FFmpeg process death."""
    from src.core.audio_visualizer import AudioVisualizer
    import subprocess
    import io

    viz = AudioVisualizer(test_config_visualization)
    audio_path = tmp_path / "audio.mp3"
    output_path = tmp_path / "output.mp4"
    audio_path.write_bytes(b"mp3" * 100)

    def frame_generator():
        yield np.zeros((1080, 1920, 3), dtype=np.uint8)

    class DyingProcess:
        def __init__(self):
            self.returncode = None
            self.stdin = MagicMock()
            # Make stderr a file-like object that returns bytes when readline() is called
            # The stderr reading thread uses iter(process.stderr.readline, b'')
            # So readline() should return bytes, and b'' when done
            stderr_data = [b"FFmpeg error: Process died\n"]
            stderr_read_count = [0]
            
            class StderrMock:
                def readline(self):
                    if stderr_read_count[0] < len(stderr_data):
                        result = stderr_data[stderr_read_count[0]]
                        stderr_read_count[0] += 1
                        return result
                    return b''  # EOF
            
            self.stderr = StderrMock()
            self.stdout = MagicMock()

        def poll(self):
            return 1  # Process died

        def communicate(self, timeout=None):
            return (b"", b"Process died")

    with (
        patch("src.core.audio_visualizer.subprocess.run") as mock_run,
        patch("src.core.audio_visualizer.subprocess.Popen", return_value=DyingProcess()),
        patch("src.utils.file_monitor.FileMonitor") as mock_monitor_class,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram_monitor_class,
    ):
        mock_run.return_value.stdout = "h264_nvenc"
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_ram_monitor = MagicMock()
        mock_ram_monitor.check_ram_limit.return_value = (False, None)
        mock_ram_monitor_class.return_value = mock_ram_monitor

        with pytest.raises(Exception, match="FFmpeg process died"):
            viz._stream_frames_to_video(frame_generator(), audio_path, output_path, 1.0)


@pytest.mark.unit
def test_stream_frames_to_video_timeout_final_encoding(tmp_path, test_config_visualization):
    """Test _stream_frames_to_video handles timeout during final encoding."""
    from src.core.audio_visualizer import AudioVisualizer
    import subprocess

    viz = AudioVisualizer(test_config_visualization)
    audio_path = tmp_path / "audio.mp3"
    output_path = tmp_path / "output.mp4"
    audio_path.write_bytes(b"mp3" * 100)

    frame_count = [0]

    def frame_generator():
        for _ in range(10):
            frame_count[0] += 1
            yield np.zeros((1080, 1920, 3), dtype=np.uint8)

    class TimeoutProcess:
        def __init__(self):
            self.returncode = 0
            self.stdin = MagicMock()
            self.stderr = MagicMock()
            self.stdout = MagicMock()

        def poll(self):
            return None

        def communicate(self, timeout=None):
            raise subprocess.TimeoutExpired("ffmpeg", 10)

    with (
        patch("src.core.audio_visualizer.subprocess.run") as mock_run,
        patch("src.core.audio_visualizer.subprocess.Popen", return_value=TimeoutProcess()),
        patch("src.utils.file_monitor.FileMonitor") as mock_monitor_class,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram_monitor_class,
    ):
        mock_run.return_value.stdout = "h264_nvenc"
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_ram_monitor = MagicMock()
        mock_ram_monitor.check_ram_limit.return_value = (False, None)
        mock_ram_monitor_class.return_value = mock_ram_monitor

        with pytest.raises(Exception, match="timed out"):
            viz._stream_frames_to_video(frame_generator(), audio_path, output_path, 1.0)


@pytest.mark.unit
def test_stream_frames_to_video_broken_pipe(tmp_path, test_config_visualization):
    """Test _stream_frames_to_video handles broken pipe error."""
    from src.core.audio_visualizer import AudioVisualizer

    viz = AudioVisualizer(test_config_visualization)
    audio_path = tmp_path / "audio.mp3"
    output_path = tmp_path / "output.mp4"
    audio_path.write_bytes(b"mp3" * 100)

    frame_count = [0]

    def frame_generator():
        for _ in range(10):
            frame_count[0] += 1
            yield np.zeros((1080, 1920, 3), dtype=np.uint8)

    class BrokenPipeProcess:
        def __init__(self):
            self.returncode = 0
            self.stdin = MagicMock()
            self.stdin.write.side_effect = BrokenPipeError("Pipe broken")
            self.stderr = MagicMock()
            self.stdout = MagicMock()

        def poll(self):
            return None

        def communicate(self, timeout=None):
            return (b"", b"Error")

    with (
        patch("src.core.audio_visualizer.subprocess.run") as mock_run,
        patch("src.core.audio_visualizer.subprocess.Popen", return_value=BrokenPipeProcess()),
        patch("src.utils.file_monitor.FileMonitor") as mock_monitor_class,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram_monitor_class,
    ):
        mock_run.return_value.stdout = "h264_nvenc"
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_ram_monitor = MagicMock()
        mock_ram_monitor.check_ram_limit.return_value = (False, None)
        mock_ram_monitor_class.return_value = mock_ram_monitor

        with pytest.raises(Exception, match="FFmpeg closed input"):
            viz._stream_frames_to_video(frame_generator(), audio_path, output_path, 1.0)


@pytest.mark.skip(reason="Complex stderr reading thread mocking - tested via integration")
def test_stream_frames_to_video_ffmpeg_error_detection(tmp_path, test_config_visualization):
    """Test _stream_frames_to_video detects FFmpeg errors in stderr."""
    # This test requires complex mocking of threading and stderr reading
    # Better tested through integration tests
    pass


@pytest.mark.unit
def test_stream_frames_to_video_nonzero_returncode(tmp_path, test_config_visualization):
    """Test _stream_frames_to_video handles non-zero FFmpeg return code."""
    from src.core.audio_visualizer import AudioVisualizer

    viz = AudioVisualizer(test_config_visualization)
    audio_path = tmp_path / "audio.mp3"
    output_path = tmp_path / "output.mp4"
    audio_path.write_bytes(b"mp3" * 100)

    def frame_generator():
        for _ in range(10):
            yield np.zeros((1080, 1920, 3), dtype=np.uint8)

    class FailedProcess:
        def __init__(self):
            self.returncode = 1
            self.stdin = MagicMock()
            self.stderr = MagicMock()
            self.stdout = MagicMock()

        def poll(self):
            return None

        def communicate(self, timeout=None):
            return ("", "FFmpeg encoding failed")

    with (
        patch("src.core.audio_visualizer.subprocess.run") as mock_run,
        patch("src.core.audio_visualizer.subprocess.Popen", return_value=FailedProcess()),
        patch("src.utils.file_monitor.FileMonitor") as mock_monitor_class,
        patch("src.utils.ram_monitor.RAMMonitor") as mock_ram_monitor_class,
    ):
        mock_run.return_value.stdout = "h264_nvenc"
        mock_monitor = MagicMock()
        mock_monitor_class.return_value = mock_monitor
        mock_ram_monitor = MagicMock()
        mock_ram_monitor.check_ram_limit.return_value = (False, None)
        mock_ram_monitor_class.return_value = mock_ram_monitor

        with pytest.raises(Exception, match="FFmpeg streaming failed"):
            viz._stream_frames_to_video(frame_generator(), audio_path, output_path, 1.0)
    # The basic randomization test above covers the main functionality


@pytest.mark.unit
def test_waveform_centered_no_samples_fallback(tmp_path, test_config_visualization):
    """Test centered waveform fallback when no samples."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    config["visualization"]["position"] = "middle"
    config["visualization"]["orientation_offset"] = 50  # Centered
    
    viz = AudioVisualizer(config)
    
    # Create empty audio chunk to trigger fallback
    empty_chunk = np.array([])
    sr = 22050
    duration = 0.1
    
    # This should not crash and should use fallback y_base = height // 2
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(empty_chunk, sr, duration))
    
    # Should generate at least one frame
    assert len(frames) > 0


@pytest.mark.unit
def test_waveform_centered_bottom_baseline(tmp_path, test_config_visualization):
    """Test centered waveform with bottom baseline (amplitude_middle_pixel > video_center)."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    config["visualization"]["position"] = "middle"
    config["visualization"]["orientation_offset"] = 50  # Centered
    
    viz = AudioVisualizer(config)
    
    # Create audio chunk with high amplitude (will trigger bottom baseline)
    # Use values that make amplitude_middle_pixel > video_center
    chunk = np.array([0.8, 0.9, 0.85, 0.9, 0.8] * 100)  # High amplitude
    
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
    
    # Should generate frames
    assert len(frames) > 0


@pytest.mark.unit
def test_waveform_centered_top_baseline(tmp_path, test_config_visualization):
    """Test centered waveform with top baseline (amplitude_middle_pixel <= video_center)."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    config["visualization"]["position"] = "middle"
    config["visualization"]["orientation_offset"] = 50  # Centered
    
    viz = AudioVisualizer(config)
    
    # Create audio chunk with low amplitude (will trigger top baseline)
    # Use values that make amplitude_middle_pixel <= video_center
    chunk = np.array([0.1, 0.2, 0.15, 0.2, 0.1] * 100)  # Low amplitude
    
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
    
    # Should generate frames
    assert len(frames) > 0


@pytest.mark.unit
def test_waveform_fixed_reference_zero_fallback(tmp_path, test_config_visualization):
    """Test waveform handles edge cases gracefully."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    
    viz = AudioVisualizer(config)
    
    # Create audio chunk with very small values that might trigger edge cases
    chunk = np.array([0.0001, 0.0002, 0.00015] * 50)
    
    # Should still generate frames even with very small values
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
    assert len(frames) > 0


@pytest.mark.unit
def test_waveform_scaled_normalized_zero_fallback(tmp_path, test_config_visualization):
    """Test waveform with scaled_normalized = 0 fallback."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    config["visualization"]["amplitude_multiplier"] = 0.0  # Zero multiplier
    
    viz = AudioVisualizer(config)
    
    # Create audio chunk
    chunk = np.array([0.1, 0.2, 0.15] * 50)
    
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
    
    # Should generate frames (with zero amplitude)
    assert len(frames) > 0


@pytest.mark.unit
def test_waveform_points_fallback(tmp_path, test_config_visualization):
    """Test waveform points fallback when len(base_points) == 0."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    
    viz = AudioVisualizer(config)
    
    # Create very small audio chunk that might result in empty base_points
    chunk = np.array([0.001] * 5)  # Very small values
    
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
    
    # Should generate frames even with fallback
    assert len(frames) > 0


@pytest.mark.unit
def test_vertical_waveform_sample_avg_fallback(tmp_path, test_config_visualization):
    """Test vertical waveform sample_avg fallback when sample_end <= sample_start."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    config["visualization"]["position"] = "left"  # Vertical waveform
    
    viz = AudioVisualizer(config)
    
    # Create very small audio chunk to trigger fallback
    chunk = np.array([0.1] * 100)  # Need enough samples for at least 1 frame
    
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
    
    # Should generate frames
    assert len(frames) > 0


@pytest.mark.unit
def test_pil_waveform_region_y_calculations(tmp_path, test_config_visualization):
    """Test PIL waveform region_y calculations for different positions."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    config["visualization"]["render_engine"] = "pil"  # Use PIL engine
    
    # Test different positions
    for position in ["top", "bottom", "middle", "other"]:
        config["visualization"]["position"] = position
        viz = AudioVisualizer(config)
        
        chunk = np.array([0.1, 0.2, 0.15] * 50)
        
        # This should not crash
        frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
        assert len(frames) > 0


@pytest.mark.unit
def test_waveform_draw_line_condition(tmp_path, test_config_visualization):
    """Test waveform draw line condition (len(points) > 1)."""
    from src.core.audio_visualizer import AudioVisualizer
    import numpy as np
    
    config = test_config_visualization.copy()
    config["visualization"]["style"] = "waveform"
    
    viz = AudioVisualizer(config)
    
    # Create audio chunk that will generate multiple points
    chunk = np.array([0.1, 0.2, 0.15, 0.3, 0.25] * 100)
    
    frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(chunk, 22050, 0.1))
    
    # Should generate frames with lines drawn
    assert len(frames) > 0
    # Verify frames are not empty
    assert frames[0].shape[0] > 0 and frames[0].shape[1] > 0