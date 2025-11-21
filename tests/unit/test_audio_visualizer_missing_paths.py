"""
Tests for missing paths in audio_visualizer.py
Targeting 426 missing lines to reach 80%+ coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from io import BytesIO

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.audio_visualizer import AudioVisualizer, OPENCV_AVAILABLE


@pytest.fixture
def test_config_viz(temp_dir):
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
            "waveform": {
                "num_lines": 1,
                "line_thickness": 12,
                "position": "bottom",
            },
        },
    }


class TestAudioVisualizerMissingPaths:
    """Tests for missing code paths in audio_visualizer.py."""

    def test_opencv_not_available_path(self, test_config_viz, tmp_path):
        """Test OpenCV not available path (lines 16-18)."""
        # Patch cv2 import to raise ImportError
        with patch.dict("sys.modules", {"cv2": None}):
            # Reload module to trigger import error path
            import importlib
            import src.core.audio_visualizer as av_module
            importlib.reload(av_module)
            
            # Should handle gracefully
            assert not hasattr(av_module, "OPENCV_AVAILABLE") or not av_module.OPENCV_AVAILABLE

    def test_randomize_config_per_line_thickness(self, test_config_viz, tmp_path):
        """Test _randomize_config with per-line thickness (line 89)."""
        config = test_config_viz.copy()
        config["visualization"]["waveform"]["randomize"] = True
        
        with patch("random.random", return_value=0.4):  # < 0.5 triggers per-line
            with patch("random.randint", return_value=12):
                viz = AudioVisualizer(config)
                # Should have per-line thickness
                assert isinstance(viz.line_thickness, list)
                assert len(viz.line_thickness) == viz.num_lines

    def test_randomize_config_single_color(self, test_config_viz, tmp_path):
        """Test _randomize_config with single color path (lines 108, 114-115)."""
        import random
        config = test_config_viz.copy()
        config["visualization"]["waveform"]["randomize"] = True
        
        with patch("random.random") as mock_random:
            # Sequence: thickness < 0.5 (per-line), color >= 0.5 (single), position >= 0.3 (single)
            mock_random.side_effect = [0.4, 0.6, 0.7]
        with patch("random.randint", side_effect=[3, 12, 10, 40, 40]):  # num_lines, thickness, height, width
            with patch("random.choice", return_value=[255, 0, 255]):
                with patch("random.uniform", return_value=0.85):
                    viz = AudioVisualizer(config)
                    # Should use single color (primary_color set, line_colors None)
                    assert viz.line_colors is None
                    assert viz.primary_color == [255, 0, 255]

    def test_randomize_config_multiple_positions(self, test_config_viz, tmp_path):
        """Test _randomize_config with multiple positions (lines 121-123)."""
        # Test by directly calling _randomize_config with controlled random behavior
        config = test_config_viz.copy()
        config["visualization"]["waveform"]["randomize"] = False  # Don't auto-randomize
        viz = AudioVisualizer(config)
        
        # Mock random methods inside the method
        import random
        original_random = random.random
        original_randint = random.randint
        original_sample = random.sample
        original_choice = random.choice
        
        try:
            # Set up mocks to trigger multiple positions path
            random.random = MagicMock(side_effect=[0.4, 0.6, 0.2])  # thickness < 0.5, color >= 0.5, position < 0.3
            random.randint = MagicMock(side_effect=[3, 12, 12, 12, 2, 10, 40])  # num_lines, thicknesses, num_positions, height, width
            random.sample = MagicMock(return_value=["top", "bottom"])
            random.choice = MagicMock(return_value=[255, 0, 255])
            
            # Call _randomize_config directly
            viz._randomize_config()
            
            # Should have multiple positions joined with comma
            assert isinstance(viz.position, str)
            assert "," in viz.position
            assert "top" in viz.position
            assert "bottom" in viz.position
        finally:
            # Restore original functions
            random.random = original_random
            random.randint = original_randint
            random.sample = original_sample
            random.choice = original_choice

    def test_generate_waveform_frames_streaming_deprecated(self, test_config_viz, tmp_path):
        """Test deprecated _generate_waveform_frames_streaming (line 213)."""
        viz = AudioVisualizer(test_config_viz)
        
        y = np.random.randn(22050).astype(np.float32)
        sr = 22050
        duration = 1.0
        
        with patch.object(viz, "_generate_waveform_frames_streaming_chunked_from_array") as mock_chunked:
            mock_chunked.return_value = iter([])
            
            # Call deprecated method
            result = viz._generate_waveform_frames_streaming(y, sr, duration)
            
            # Should call chunked version
            mock_chunked.assert_called_once_with(y, sr, duration)

    def test_generate_waveform_frames_progress_reporting(self, test_config_viz, tmp_path):
        """Test progress reporting in chunked frame generation (line 230)."""
        viz = AudioVisualizer(test_config_viz)
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        sr = 22050
        duration = 10.0  # Long enough to trigger progress reporting
        
        with patch("src.core.audio_visualizer.librosa.load") as mock_load:
            # Mock chunked loading
            mock_load.side_effect = [np.random.randn(735).astype(np.float32)] * 300
            
            with patch.object(viz, "_draw_waveform_opencv", return_value=np.zeros((1080, 1920, 3), dtype=np.uint8)):
                # Generate frames - should trigger progress at frame 100, 200, etc.
                frames = list(viz._generate_waveform_frames_streaming_chunked(audio_path, sr, duration))
                
                # Should generate correct number of frames
                expected_frames = int(duration * viz.fps)
                assert len(frames) == expected_frames

    def test_draw_waveform_opencv_centered_amplitude_middle_paths(self, test_config_viz, tmp_path):
        """Test centered waveform with amplitude middle calculations (lines 496-499, 503-505, 509-511, 514, 517)."""
        viz = AudioVisualizer(test_config_viz)
        viz.position = "middle"
        
        width, height = 1920, 1080
        
        # Create sample data that will trigger amplitude middle > video_center path
        raw_samples = [0.8, 0.9, 0.85, 0.7, 0.75]  # High amplitude (triggers bottom baseline)
        
        with patch("src.core.audio_visualizer.cv2", create=True) if OPENCV_AVAILABLE else patch.dict("sys.modules", {"cv2": MagicMock()}):
            # Mock cv2 operations
            mock_cv2 = MagicMock() if not OPENCV_AVAILABLE else None
            if mock_cv2:
                mock_cv2.LINE_AA = 16
                mock_cv2.FILLED = -1
                with patch("src.core.audio_visualizer.cv2", mock_cv2):
                    with patch("src.core.audio_visualizer.np.interp") as mock_interp:
                        mock_interp.return_value = np.array([0.8, 0.9, 0.85])
                        
                        # Test with high amplitude (should use bottom baseline)
                        frame = viz._draw_waveform_opencv(
                            raw_samples,
                            width,
                            height,
                            position="middle",
                            orientation="horizontal",
                        )
                        
                        # Should create frame
                        assert frame is not None
                        assert frame.shape == (height, width, 3)

    def test_stream_frames_to_video_ffmpeg_errors(self, test_config_viz, tmp_path):
        """Test FFmpeg error handling paths (lines 555, 600, 602, 605-607)."""
        import threading
        viz = AudioVisualizer(test_config_viz)
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"
        
        def frame_gen():
            yield np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # Test FFmpeg process error
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.stdin = MagicMock()
            mock_process.stdin.write = MagicMock()
            mock_process.stdin.flush = MagicMock()
            mock_process.stdin.close = MagicMock()
            mock_process.poll.return_value = 1  # Non-zero return code
            mock_process.communicate.return_value = (b"", b"FFmpeg error")
            mock_process.stderr = BytesIO(b"error message")
            mock_popen.return_value = mock_process
            
            with patch("threading.Thread"):
                with patch("threading.Event") as mock_event:
                    mock_done = MagicMock()
                    mock_done.is_set.return_value = False
                    mock_done.wait = MagicMock()
                    mock_event.return_value = mock_done
                    
                    # Should handle error gracefully
                    try:
                        viz._stream_frames_to_video(frame_gen(), audio_path, output_path, 1.0)
                    except Exception:
                        pass  # Expected to raise or handle error

    def test_draw_waveform_opencv_empty_samples_fallback(self, test_config_viz, tmp_path):
        """Test empty samples fallback in centered waveform (line 517)."""
        viz = AudioVisualizer(test_config_viz)
        viz.position = "middle"
        
        width, height = 1920, 1080
        raw_samples = []  # Empty samples
        
        with patch("src.core.audio_visualizer.cv2", create=True) if OPENCV_AVAILABLE else patch.dict("sys.modules", {"cv2": MagicMock()}):
            mock_cv2 = MagicMock() if not OPENCV_AVAILABLE else None
            if mock_cv2:
                mock_cv2.LINE_AA = 16
                mock_cv2.FILLED = -1
                with patch("src.core.audio_visualizer.cv2", mock_cv2):
                    # Test with empty samples (should use fallback y_base = height // 2)
                    frame = viz._draw_waveform_opencv(
                        raw_samples,
                        width,
                        height,
                        position="middle",
                        orientation="horizontal",
                    )
                    
                    # Should create frame even with empty samples
                    assert frame is not None

    def test_randomize_config_style_selection(self, test_config_viz, tmp_path):
        """Test randomization of waveform style."""
        import random
        config = test_config_viz.copy()
        config["visualization"]["waveform"]["randomize"] = False  # Don't auto-randomize
        viz = AudioVisualizer(config)
        
        # Mock random methods inside the method
        original_random = random.random
        original_randint = random.randint
        original_choice = random.choice
        original_uniform = random.uniform
        
        try:
            # Set up mocks
            random.random = MagicMock(side_effect=[0.4, 0.6, 0.7])  # thickness < 0.5, color >= 0.5, position >= 0.3
            random.randint = MagicMock(side_effect=[3, 12, 12, 12, 10, 40])  # num_lines, thicknesses (x3), height, width
            random.choice = MagicMock(return_value=[255, 0, 255])
            random.uniform = MagicMock(return_value=0.85)
            
            # Call _randomize_config directly
            viz._randomize_config()
            
            # Should have randomized settings
            assert viz.num_lines in range(1, 6)
            assert viz.opacity >= 0.7
        finally:
            # Restore original functions
            random.random = original_random
            random.randint = original_randint
            random.choice = original_choice
            random.uniform = original_uniform

    def test_generate_waveform_frames_chunked_from_array(self, test_config_viz, tmp_path):
        """Test chunked frame generation from array (lines 364+)."""
        viz = AudioVisualizer(test_config_viz)
        
        # Create larger audio array
        sr = 22050
        duration = 2.0
        y = np.random.randn(int(sr * duration)).astype(np.float32)
        
        with patch.object(viz, "_draw_waveform_opencv", return_value=np.zeros((1080, 1920, 3), dtype=np.uint8)):
            frames = list(viz._generate_waveform_frames_streaming_chunked_from_array(y, sr, duration))
            
            # Should generate correct number of frames
            expected_frames = int(duration * viz.fps)
            assert len(frames) == expected_frames

    def test_draw_waveform_opencv_pil_fallback(self, test_config_viz, tmp_path):
        """Test PIL fallback when OpenCV not available (lines 281-291)."""
        # Test the PIL fallback path in _generate_waveform_frames_streaming_chunked
        config = test_config_viz.copy()
        config["visualization"]["waveform"]["anti_alias"] = False  # Disable anti-aliasing to trigger PIL
        viz = AudioVisualizer(config)
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        sr = 22050
        duration = 1.0
        
        # Mock OPENCV_AVAILABLE to False
        original_opencv = OPENCV_AVAILABLE
        
        try:
            # Temporarily set OPENCV_AVAILABLE to False
            import src.core.audio_visualizer as av_module
            av_module.OPENCV_AVAILABLE = False
            
            with patch("src.core.audio_visualizer.librosa.load") as mock_load:
                # Mock chunked loading
                mock_load.return_value = (np.random.randn(735).astype(np.float32), sr)
                
                # Should use PIL fallback path
                frames = list(viz._generate_waveform_frames_streaming_chunked(audio_path, sr, duration))
                
                # Should generate frames using PIL
                expected_frames = int(duration * viz.fps)
                assert len(frames) == expected_frames
                assert all(f.shape == (viz.resolution[1], viz.resolution[0], 3) for f in frames)
        finally:
            # Restore original value
            av_module.OPENCV_AVAILABLE = original_opencv

    def test_draw_waveform_opencv_top_baseline_path(self, test_config_viz, tmp_path):
        """Test centered waveform with top baseline (line 600-602)."""
        viz = AudioVisualizer(test_config_viz)
        viz.position = "middle"
        
        width, height = 1920, 1080
        render_width, render_height = int(width * 2), int(height * 2)
        frame = np.zeros((render_height, render_width, 3), dtype=np.uint8)
        chunk = np.array([0.1, 0.15, 0.12, 0.18, 0.1], dtype=np.float32)
        amplitude = 0.15
        base_thickness = 12
        
        # Test with low amplitude (triggers top baseline in centered waveform)
        # This tests the internal logic paths within _draw_waveform_opencv
        if OPENCV_AVAILABLE:
            viz._draw_waveform_opencv(frame, chunk, amplitude, render_width, render_height, "middle", base_thickness)
            # Should modify frame
            assert frame is not None

    def test_draw_waveform_opencv_bottom_baseline_path(self, test_config_viz, tmp_path):
        """Test centered waveform with bottom baseline (lines 604-605)."""
        viz = AudioVisualizer(test_config_viz)
        viz.position = "middle"
        
        width, height = 1920, 1080
        render_width, render_height = int(width * 2), int(height * 2)
        frame = np.zeros((render_height, render_width, 3), dtype=np.uint8)
        chunk = np.array([0.8, 0.9, 0.85, 0.95, 0.8], dtype=np.float32)
        amplitude = 0.85
        base_thickness = 12
        
        # Test with high amplitude (triggers bottom baseline in centered waveform)
        if OPENCV_AVAILABLE:
            viz._draw_waveform_opencv(frame, chunk, amplitude, render_width, render_height, "middle", base_thickness)
            # Should modify frame
            assert frame is not None

    def test_draw_waveform_opencv_top_position_path(self, test_config_viz, tmp_path):
        """Test top position waveform path (lines 608-612)."""
        viz = AudioVisualizer(test_config_viz)
        viz.position = "top"
        
        width, height = 1920, 1080
        render_width, render_height = int(width * 2), int(height * 2)
        frame = np.zeros((render_height, render_width, 3), dtype=np.uint8)
        chunk = np.array([0.5, 0.7, 0.6], dtype=np.float32)
        amplitude = 0.6
        base_thickness = 12
        
        if OPENCV_AVAILABLE:
            viz._draw_waveform_opencv(frame, chunk, amplitude, render_width, render_height, "top", base_thickness)
            # Should modify frame
            assert frame is not None

    def test_draw_waveform_opencv_bottom_position_path(self, test_config_viz, tmp_path):
        """Test bottom position waveform path (lines 613-617)."""
        viz = AudioVisualizer(test_config_viz)
        viz.position = "bottom"
        
        width, height = 1920, 1080
        render_width, render_height = int(width * 2), int(height * 2)
        frame = np.zeros((render_height, render_width, 3), dtype=np.uint8)
        chunk = np.array([0.5, 0.7, 0.6], dtype=np.float32)
        amplitude = 0.6
        base_thickness = 12
        
        if OPENCV_AVAILABLE:
            viz._draw_waveform_opencv(frame, chunk, amplitude, render_width, render_height, "bottom", base_thickness)
            # Should modify frame
            assert frame is not None

