"""
Tests for missing paths in avatar_generator.py
Targeting missing lines to reach 80%+ coverage
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from io import BytesIO

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.avatar_generator import AvatarGenerator


@pytest.fixture
def test_config_avatar(temp_dir):
    """Create test config with avatar settings."""
    return {
        "storage": {
            "cache_dir": str(temp_dir / "cache"),
        },
        "avatar": {
            "engine": "wav2lip",
            "source_image": str(temp_dir / "face.jpg"),
        },
    }


class TestAvatarGeneratorMissingPaths:
    """Tests for missing code paths in avatar_generator.py."""

    def test_init_absolute_path_source_image(self, test_config_avatar, tmp_path):
        """Test __init__ with absolute path for source_image (line 35-36)."""
        config = test_config_avatar.copy()
        abs_path = tmp_path / "absolute_face.jpg"
        abs_path.write_bytes(b"fake image")
        config["avatar"]["source_image"] = str(abs_path.absolute())
        
        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            viz = AvatarGenerator(config)
            
            # Should use absolute path directly
            assert viz.source_image == abs_path.absolute()

    def test_init_relative_path_source_image(self, test_config_avatar, tmp_path):
        """Test __init__ with relative path for source_image (lines 37-40)."""
        config = test_config_avatar.copy()
        relative_path = "src/assets/avatars/default_female.jpg"
        config["avatar"]["source_image"] = relative_path
        
        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            # Create the file in expected location
            project_root = Path(__file__).parent.parent.parent
            expected_path = (project_root / relative_path)
            expected_path.parent.mkdir(parents=True, exist_ok=True)
            expected_path.write_bytes(b"fake image")
            
            viz = AvatarGenerator(config)
            
            # Should resolve relative path from project root
            assert viz.source_image == expected_path.resolve()

    def test_generate_unknown_engine_fallback(self, test_config_avatar, tmp_path):
        """Test generate with unknown engine type uses fallback (lines 192-194)."""
        config = test_config_avatar.copy()
        config["avatar"]["engine"] = "unknown_engine"
        
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            with patch.object(AvatarGenerator, "_create_fallback_video") as mock_fallback:
                mock_fallback.return_value = tmp_path / "fallback.mp4"
                
                viz = AvatarGenerator(config)
                result = viz.generate(audio_path)
                
                # Should call fallback method
                mock_fallback.assert_called_once()
                assert result == tmp_path / "fallback.mp4"

    def test_get_audio_duration_ffmpeg_success(self, test_config_avatar, tmp_path):
        """Test _get_audio_duration_ffmpeg successful path (lines 68-91)."""
        config = test_config_avatar.copy()
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_run,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            # Mock successful ffprobe result
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "120.5\n"  # Duration in seconds
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            viz = AvatarGenerator(config)
            duration = viz._get_audio_duration_ffmpeg(audio_path)
            
            # Should return duration
            assert duration == 120.5
            mock_run.assert_called_once()

    def test_get_audio_duration_ffmpeg_timeout(self, test_config_avatar, tmp_path):
        """Test _get_audio_duration_ffmpeg timeout path (line 88)."""
        config = test_config_avatar.copy()
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_run,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            # Mock timeout
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired(cmd=["ffprobe"], timeout=10)
            
            viz = AvatarGenerator(config)
            duration = viz._get_audio_duration_ffmpeg(audio_path)
            
            # Should return None on timeout
            assert duration is None

    def test_get_audio_duration_ffmpeg_file_not_found(self, test_config_avatar, tmp_path):
        """Test _get_audio_duration_ffmpeg FileNotFoundError path (line 88)."""
        config = test_config_avatar.copy()
        audio_path = tmp_path / "nonexistent.mp3"
        
        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_run,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            # Mock FileNotFoundError
            mock_run.side_effect = FileNotFoundError("ffprobe not found")
            
            viz = AvatarGenerator(config)
            duration = viz._get_audio_duration_ffmpeg(audio_path)
            
            # Should return None on error
            assert duration is None

    def test_get_audio_duration_ffmpeg_value_error(self, test_config_avatar, tmp_path):
        """Test _get_audio_duration_ffmpeg ValueError path (line 88)."""
        config = test_config_avatar.copy()
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_run,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            # Mock result with invalid output
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "invalid\n"  # Invalid duration string
            mock_run.return_value = mock_result
            
            viz = AvatarGenerator(config)
            
            # Should handle ValueError gracefully
            duration = viz._get_audio_duration_ffmpeg(audio_path)
            
            # Should return None on ValueError
            assert duration is None

    def test_get_audio_duration_ffmpeg_non_zero_returncode(self, test_config_avatar, tmp_path):
        """Test _get_audio_duration_ffmpeg non-zero returncode path (lines 86-87)."""
        config = test_config_avatar.copy()
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_run,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            # Mock non-zero returncode
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Error"
            mock_run.return_value = mock_result
            
            viz = AvatarGenerator(config)
            duration = viz._get_audio_duration_ffmpeg(audio_path)
            
            # Should return None on non-zero returncode
            assert duration is None

    def test_get_audio_duration_ffmpeg_empty_stdout(self, test_config_avatar, tmp_path):
        """Test _get_audio_duration_ffmpeg empty stdout path (line 86)."""
        config = test_config_avatar.copy()
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"fake audio")
        
        with (
            patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu,
            patch("subprocess.run") as mock_run,
        ):
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            # Mock empty stdout
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""  # Empty stdout
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            viz = AvatarGenerator(config)
            duration = viz._get_audio_duration_ffmpeg(audio_path)
            
            # Should return None on empty stdout
            assert duration is None

    def test_get_file_monitor_returns_last_monitor(self, test_config_avatar, tmp_path):
        """Test get_file_monitor returns last file monitor (lines 64-66)."""
        config = test_config_avatar.copy()
        
        with patch("src.core.avatar_generator.get_gpu_manager") as mock_gpu:
            mock_gpu.return_value.gpu_available = False
            mock_gpu.return_value.get_device.return_value = "cpu"
            
            viz = AvatarGenerator(config)
            
            # Initially should be None
            assert viz.get_file_monitor() is None
            
            # Set a mock file monitor
            mock_monitor = MagicMock()
            viz.last_file_monitor = mock_monitor
            
            # Should return the last monitor
            assert viz.get_file_monitor() == mock_monitor

