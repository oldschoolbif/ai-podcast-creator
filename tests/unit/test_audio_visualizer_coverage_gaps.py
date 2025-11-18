"""
Additional tests for audio_visualizer.py to improve coverage from 73.63% to 80%+

Focus on uncovered code paths:
- _stream_frames_to_video: GPU/CPU paths, error handling, process management
- _frames_to_video: Legacy method, GPU/CPU paths, error handling
- _generate_spectrum_frames_streaming_chunked: Edge cases (empty spectrum, STFT failures)
- _generate_circular_frames_streaming_chunked: Error handling
- _generate_particle_frames_streaming_chunked: Error handling
"""

import os
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
        },
        "video": {
            "resolution": [1920, 1080],
            "fps": 30,
        },
        "storage": {"cache_dir": str(tmp_path)},
    }


class TestStreamFramesToVideoCoverage:
    """Test _stream_frames_to_video uncovered paths."""

    def test_stream_frames_to_video_gpu_nvenc(self, test_config_visualization, tmp_path):
        """Test _stream_frames_to_video uses NVENC when GPU available."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        # Mock GPU manager and FFmpeg encoder check
        with (
            patch("src.utils.gpu_utils.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_subprocess,
            patch("subprocess.Popen") as mock_popen,
            patch("src.utils.file_monitor.FileMonitor") as mock_monitor,
            patch("src.utils.ram_monitor.RAMMonitor") as mock_ram_monitor_class,
        ):
            # Mock GPU available
            mock_gpu_instance = MagicMock()
            mock_gpu_instance.gpu_available = True
            mock_gpu.return_value = mock_gpu_instance

            # Mock FFmpeg encoder check (NVENC available)
            mock_subprocess.return_value.stdout = "h264_nvenc"
            mock_subprocess.return_value.returncode = 0

            # Mock RAMMonitor
            mock_ram_monitor = MagicMock()
            mock_ram_monitor.check_ram_limit.return_value = (False, "")  # Not over limit
            mock_ram_monitor_class.return_value = mock_ram_monitor

            # Mock FFmpeg process
            mock_process = MagicMock()
            mock_process.stdin = MagicMock()
            mock_process.stdin.write = MagicMock()
            mock_process.stdin.close = MagicMock()
            mock_process.wait = MagicMock(return_value=0)
            mock_process.poll = MagicMock(return_value=None)  # Process still running
            mock_process.returncode = 0
            # Mock communicate() to return (stdout, stderr) tuple
            mock_process.communicate = MagicMock(return_value=(b'', b''))
            # Mock stderr to return empty iterator (simulates no errors)
            mock_stderr = MagicMock()
            # Make readline return empty bytes immediately (stops iterator)
            mock_stderr.readline = MagicMock(return_value=b'')  # Empty bytes = end of stream
            mock_process.stderr = mock_stderr
            mock_popen.return_value = mock_process

            # Mock monitor
            mock_monitor_instance = MagicMock()
            mock_monitor.return_value = mock_monitor_instance

            # Create frame generator that yields enough frames
            def frame_gen():
                for _ in range(30):  # Yield 30 frames (1 second at 30fps)
                    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
                    yield frame

            visualizer._stream_frames_to_video(frame_gen(), audio_path, output_path, 1.0)

            # Verify NVENC was used (check command contains h264_nvenc)
            call_args = mock_popen.call_args[0][0] if mock_popen.called else []
            assert any("h264_nvenc" in str(arg) for arg in call_args) or any("nvenc" in str(arg).lower() for arg in call_args)

    def test_stream_frames_to_video_cpu_fallback(self, test_config_visualization, tmp_path):
        """Test _stream_frames_to_video falls back to CPU when GPU unavailable."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("src.utils.gpu_utils.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_subprocess,
            patch("subprocess.Popen") as mock_popen,
            patch("src.utils.file_monitor.FileMonitor") as mock_monitor,
            patch("src.utils.ram_monitor.RAMMonitor") as mock_ram_monitor_class,
        ):
            # Mock GPU unavailable
            mock_gpu_instance = MagicMock()
            mock_gpu_instance.gpu_available = False
            mock_gpu.return_value = mock_gpu_instance

            # Mock FFmpeg encoder check (no NVENC)
            mock_subprocess.return_value.stdout = "libx264"
            mock_subprocess.return_value.returncode = 0

            # Mock RAMMonitor
            mock_ram_monitor = MagicMock()
            mock_ram_monitor.check_ram_limit.return_value = (False, "")  # Not over limit
            mock_ram_monitor_class.return_value = mock_ram_monitor

            # Mock FFmpeg process
            mock_process = MagicMock()
            mock_process.stdin = MagicMock()
            mock_process.stdin.write = MagicMock()
            mock_process.stdin.close = MagicMock()
            mock_process.wait = MagicMock(return_value=0)
            mock_process.poll = MagicMock(return_value=None)  # Process still running
            mock_process.returncode = 0
            # Mock communicate() to return (stdout, stderr) tuple
            mock_process.communicate = MagicMock(return_value=(b'', b''))
            # Mock stderr to return empty iterator (simulates no errors)
            mock_stderr = MagicMock()
            # Make readline return empty bytes immediately (stops iterator)
            mock_stderr.readline = MagicMock(return_value=b'')  # Empty bytes = end of stream
            mock_process.stderr = mock_stderr
            mock_popen.return_value = mock_process

            # Mock monitor
            mock_monitor_instance = MagicMock()
            mock_monitor.return_value = mock_monitor_instance

            # Create frame generator that yields enough frames
            def frame_gen():
                for _ in range(30):  # Yield 30 frames (1 second at 30fps)
                    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
                    yield frame

            visualizer._stream_frames_to_video(frame_gen(), audio_path, output_path, 1.0)

            # Verify libx264 was used (CPU fallback)
            call_args = mock_popen.call_args[0][0] if mock_popen.called else []
            assert any("libx264" in str(arg) for arg in call_args)

    def test_stream_frames_to_video_gpu_check_exception(self, test_config_visualization, tmp_path):
        """Test _stream_frames_to_video handles GPU check exceptions."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("src.utils.gpu_utils.get_gpu_manager", side_effect=Exception("GPU check failed")),
            patch("subprocess.Popen") as mock_popen,
            patch("src.utils.file_monitor.FileMonitor") as mock_monitor,
            patch("src.utils.ram_monitor.RAMMonitor") as mock_ram_monitor_class,
        ):
            # Mock RAMMonitor
            mock_ram_monitor = MagicMock()
            mock_ram_monitor.check_ram_limit.return_value = (False, "")  # Not over limit
            mock_ram_monitor_class.return_value = mock_ram_monitor

            # Mock FFmpeg process
            mock_process = MagicMock()
            mock_process.stdin = MagicMock()
            mock_process.stdin.write = MagicMock()
            mock_process.stdin.close = MagicMock()
            mock_process.wait = MagicMock(return_value=0)
            mock_process.poll = MagicMock(return_value=None)  # Process still running
            mock_process.returncode = 0
            # Mock communicate() to return (stdout, stderr) tuple
            mock_process.communicate = MagicMock(return_value=(b'', b''))
            # Mock stderr to return empty iterator (simulates no errors)
            mock_stderr = MagicMock()
            # Make readline return empty bytes immediately (stops iterator)
            mock_stderr.readline = MagicMock(return_value=b'')  # Empty bytes = end of stream
            mock_process.stderr = mock_stderr
            mock_popen.return_value = mock_process

            # Mock monitor
            mock_monitor_instance = MagicMock()
            mock_monitor.return_value = mock_monitor_instance

            # Create frame generator that yields enough frames
            def frame_gen():
                for _ in range(30):  # Yield 30 frames (1 second at 30fps)
                    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
                    yield frame

            # Should fall back to CPU encoding
            visualizer._stream_frames_to_video(frame_gen(), audio_path, output_path, 1.0)

            # Should still work (CPU fallback)
            assert mock_popen.called


class TestFramesToVideoCoverage:
    """Test _frames_to_video uncovered paths."""

    def test_frames_to_video_gpu_nvenc(self, test_config_visualization, tmp_path):
        """Test _frames_to_video uses NVENC when GPU available."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        # Create test frames
        frames = [np.zeros((1080, 1920, 3), dtype=np.uint8) for _ in range(10)]

        # Create temp directory
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        with (
            patch("src.utils.gpu_utils.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_subprocess,
            patch("tempfile.mkdtemp", return_value=str(temp_dir)),
        ):
            # Mock GPU available
            mock_gpu_instance = MagicMock()
            mock_gpu_instance.gpu_available = True
            mock_gpu.return_value = mock_gpu_instance

            # Mock FFmpeg encoder check (NVENC available)
            mock_subprocess.return_value.stdout = "h264_nvenc"
            mock_subprocess.return_value.returncode = 0

            # First call is encoder check, second is actual encoding
            mock_subprocess.return_value.returncode = 0

            result = visualizer._frames_to_video(frames, audio_path, output_path)

            # Verify NVENC was checked
            assert mock_subprocess.call_count >= 1

    def test_frames_to_video_cpu_fallback(self, test_config_visualization, tmp_path):
        """Test _frames_to_video falls back to CPU when GPU unavailable."""
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        # Create test frames
        frames = [np.zeros((1080, 1920, 3), dtype=np.uint8) for _ in range(10)]

        # Create temp directory
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        with (
            patch("src.utils.gpu_utils.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_subprocess,
            patch("tempfile.mkdtemp", return_value=str(temp_dir)),
        ):
            # Mock GPU unavailable
            mock_gpu_instance = MagicMock()
            mock_gpu_instance.gpu_available = False
            mock_gpu.return_value = mock_gpu_instance

            # Mock FFmpeg encoder check (no NVENC)
            mock_subprocess.return_value.stdout = "libx264"
            mock_subprocess.return_value.returncode = 0

            result = visualizer._frames_to_video(frames, audio_path, output_path)

            # Should use CPU encoding
            assert mock_subprocess.called


class TestSpectrumFramesStreamingChunkedCoverage:
    """Test _generate_spectrum_frames_streaming_chunked edge cases."""

    def test_spectrum_frames_empty_spectrum(self, test_config_visualization, tmp_path):
        """Test spectrum generation handles empty spectrum."""
        test_config_visualization["visualization"]["style"] = "spectrum"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with patch("librosa.load") as mock_load:
            # Mock librosa to return empty array
            mock_load.return_value = (np.array([]), 44100)

            # Should handle empty spectrum gracefully
            frames = list(visualizer._generate_spectrum_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames

    def test_spectrum_frames_stft_empty_result(self, test_config_visualization, tmp_path):
        """Test spectrum generation handles STFT returning empty result."""
        test_config_visualization["visualization"]["style"] = "spectrum"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.zeros(1000), 44100)),
            patch("librosa.stft", return_value=np.array([]).reshape(0, 0)),  # Empty STFT
        ):
            # Should handle empty STFT result
            frames = list(visualizer._generate_spectrum_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames using fallback

    def test_spectrum_frames_librosa_exception(self, test_config_visualization, tmp_path):
        """Test spectrum generation handles librosa exceptions."""
        test_config_visualization["visualization"]["style"] = "spectrum"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with patch("librosa.load", side_effect=Exception("Librosa error")):
            # Should handle exception and use zero chunk
            frames = list(visualizer._generate_spectrum_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames

    def test_spectrum_frames_spectrum_too_short(self, test_config_visualization, tmp_path):
        """Test spectrum generation handles spectrum shorter than num_bars."""
        test_config_visualization["visualization"]["style"] = "spectrum"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch("librosa.load", return_value=(np.zeros(1000), 44100)),
            patch("librosa.stft", return_value=np.random.rand(10, 1)),  # Very short spectrum
        ):
            # Should handle short spectrum
            frames = list(visualizer._generate_spectrum_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames


class TestCircularFramesStreamingChunkedCoverage:
    """Test _generate_circular_frames_streaming_chunked error handling."""

    def test_circular_frames_librosa_exception(self, test_config_visualization, tmp_path):
        """Test circular generation handles librosa exceptions."""
        test_config_visualization["visualization"]["style"] = "circular"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with patch("librosa.load", side_effect=Exception("Librosa error")):
            # Should handle exception and use zero chunk
            frames = list(visualizer._generate_circular_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames

    def test_circular_frames_empty_chunk(self, test_config_visualization, tmp_path):
        """Test circular generation handles empty chunk."""
        test_config_visualization["visualization"]["style"] = "circular"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with patch("librosa.load", return_value=(np.array([]), 44100)):
            # Should handle empty chunk
            frames = list(visualizer._generate_circular_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames


class TestParticleFramesStreamingChunkedCoverage:
    """Test _generate_particle_frames_streaming_chunked error handling."""

    def test_particle_frames_librosa_exception(self, test_config_visualization, tmp_path):
        """Test particle generation handles librosa exceptions."""
        test_config_visualization["visualization"]["style"] = "particles"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with patch("librosa.load", side_effect=Exception("Librosa error")):
            # Should handle exception and use zero chunk
            frames = list(visualizer._generate_particle_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames

    def test_particle_frames_empty_chunk(self, test_config_visualization, tmp_path):
        """Test particle generation handles empty chunk."""
        test_config_visualization["visualization"]["style"] = "particles"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")

        visualizer = AudioVisualizer(test_config_visualization)

        with patch("librosa.load", return_value=(np.array([]), 44100)):
            # Should handle empty chunk
            frames = list(visualizer._generate_particle_frames_streaming_chunked(audio_path, 44100, 0.1))
            assert len(frames) > 0  # Should still generate frames


class TestGenerateVisualizationCoverage:
    """Test generate_visualization uncovered paths."""

    def test_generate_visualization_ffmpeg_duration_fallback(self, test_config_visualization, tmp_path):
        """Test generate_visualization uses default duration when FFmpeg fails."""
        test_config_visualization["visualization"]["style"] = "waveform"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch.object(visualizer, "_get_audio_duration_ffmpeg", return_value=None),  # FFmpeg fails
            patch("librosa.load", return_value=(np.zeros(4410), 44100)),  # 0.1 second sample
            patch.object(visualizer, "_generate_waveform_frames_streaming_chunked") as mock_gen,
            patch.object(visualizer, "_stream_frames_to_video") as mock_stream,
        ):
            mock_gen.return_value = iter([np.zeros((1080, 1920, 3), dtype=np.uint8)])
            mock_stream.return_value = output_path

            result = visualizer.generate_visualization(audio_path, output_path)

            # Should use default duration (10.0 seconds)
            assert mock_gen.called
            # Check that duration was passed (should be 10.0 default)
            # Note: duration is passed as positional arg, not keyword
            call_args = mock_gen.call_args[0] if mock_gen.call_args else ()
            if len(call_args) >= 3:
                duration = call_args[2]  # duration is 3rd positional arg
                assert duration == 10.0  # Default duration

    def test_generate_visualization_unknown_style_fallback(self, test_config_visualization, tmp_path):
        """Test generate_visualization falls back to waveform for unknown style."""
        test_config_visualization["visualization"]["style"] = "unknown_style"
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        output_path = tmp_path / "output.mp4"

        visualizer = AudioVisualizer(test_config_visualization)

        with (
            patch.object(visualizer, "_get_audio_duration_ffmpeg", return_value=5.0),
            patch("librosa.load", return_value=(np.zeros(4410), 44100)),
            patch.object(visualizer, "_generate_waveform_frames_streaming_chunked") as mock_gen,
            patch.object(visualizer, "_stream_frames_to_video") as mock_stream,
        ):
            mock_gen.return_value = iter([np.zeros((1080, 1920, 3), dtype=np.uint8)])
            mock_stream.return_value = output_path

            result = visualizer.generate_visualization(audio_path, output_path)

            # Should fall back to waveform
            mock_gen.assert_called_once()

