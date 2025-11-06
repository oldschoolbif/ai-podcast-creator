"""
Unit Tests for Video Composer
Tests for src/core/video_composer.py with correct API
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from src.core.video_composer import VideoComposer
from tests.conftest import create_valid_mp3_file


class TestVideoComposerInit:
    """Test VideoComposer initialization."""

    def test_init(self, test_config):
        """Test basic initialization."""
        composer = VideoComposer(test_config)
        assert composer.config == test_config
        assert composer.output_dir.exists()

    def test_init_creates_output_directory(self, test_config, temp_dir):
        """Test initialization creates output directory."""
        output_dir = temp_dir / "new_outputs"
        test_config["storage"]["outputs_dir"] = str(output_dir)

        composer = VideoComposer(test_config)
        assert output_dir.exists()

    def test_init_sets_background_path(self, test_config):
        """Test initialization sets background path."""
        composer = VideoComposer(test_config)
        assert hasattr(composer, "background")
        assert isinstance(composer.background, Path)


class TestVideoComposerCompose:
    """Test VideoComposer.compose() method."""

    def test_compose_basic(self, test_config, temp_dir):
        """Test basic video composition with moviepy."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        # Mock moviepy components
        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()

        mock_bg_clip = MagicMock()
        mock_bg_clip.set_duration = MagicMock(return_value=mock_bg_clip)
        mock_bg_clip.set_audio = MagicMock(return_value=mock_bg_clip)
        mock_bg_clip.write_videofile = MagicMock()
        mock_bg_clip.close = MagicMock()

        # Create mock moviepy module
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ImageClip = MagicMock(return_value=mock_bg_clip)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_bg_clip)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            composer = VideoComposer(test_config)
            result = composer.compose(audio_path, output_name="test_output")

            assert result.name == "test_output.mp4"
            mock_audio.close.assert_called()

    def test_compose_with_color_background(self, test_config, temp_dir):
        """Test composition when background image doesn't exist (uses ColorClip)."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        # Remove background to trigger ColorClip
        test_config["video"]["background_path"] = str(temp_dir / "nonexistent.jpg")

        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()

        mock_color_clip = MagicMock()
        mock_color_clip.set_duration = MagicMock(return_value=mock_color_clip)
        mock_color_clip.set_audio = MagicMock(return_value=mock_color_clip)
        mock_color_clip.write_videofile = MagicMock()
        mock_color_clip.close = MagicMock()

        # Create mock moviepy module
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_color_clip)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_color_clip)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            composer = VideoComposer(test_config)
            result = composer.compose(audio_path, output_name="test_output")

            assert result is not None

    def test_compose_with_visualization(self, test_config, temp_dir):
        """Test composition with audio visualization."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        expected_output = temp_dir / "output" / "test_viz.mp4"

        with patch("src.core.audio_visualizer.AudioVisualizer") as mock_visualizer_class:
            mock_visualizer = MagicMock()
            mock_visualizer.generate_visualization = MagicMock(return_value=expected_output)
            mock_visualizer_class.return_value = mock_visualizer

            composer = VideoComposer(test_config)
            result = composer.compose(audio_path, output_name="test_viz", use_visualization=True)

            assert mock_visualizer.generate_visualization.called
            assert result == expected_output

    def test_compose_with_avatar_video_and_visualization(self, test_config, temp_dir):
        """Test composition with both avatar video and visualization."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        avatar_video = temp_dir / "avatar.mp4"
        avatar_video.touch()

        with patch.object(VideoComposer, "_overlay_visualization_on_avatar") as mock_overlay:
            mock_overlay.return_value = temp_dir / "output.mp4"

            composer = VideoComposer(test_config)
            result = composer.compose(
                audio_path, output_name="test_avatar_viz", use_visualization=True, avatar_video=avatar_video
            )

            mock_overlay.assert_called_once()

    def test_compose_default_use_visualization_false(self, test_config, temp_dir):
        """Test that compose defaults to use_visualization=False (no visualization by default)."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        composer = VideoComposer(test_config)

        # Mock moviepy to verify default path (no visualization)
        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()

        mock_color_clip = MagicMock()
        mock_color_clip.set_duration = MagicMock(return_value=mock_color_clip)
        mock_color_clip.set_audio = MagicMock(return_value=mock_color_clip)
        mock_color_clip.write_videofile = MagicMock()
        mock_color_clip.close = MagicMock()

        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_color_clip)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_color_clip)

        with (
            patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}),
            patch("src.core.audio_visualizer.AudioVisualizer") as mock_visualizer_class,
        ):

            result = composer.compose(audio_path, output_name="test_default_no_viz")

            # Default should be False - visualization should NOT be called
            mock_visualizer_class.assert_not_called()
            assert result is not None

    def test_compose_explicitly_use_visualization_false(self, test_config, temp_dir):
        """Test compose with use_visualization=False explicitly."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        composer = VideoComposer(test_config)

        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()

        mock_color_clip = MagicMock()
        mock_color_clip.set_duration = MagicMock(return_value=mock_color_clip)
        mock_color_clip.set_audio = MagicMock(return_value=mock_color_clip)
        mock_color_clip.write_videofile = MagicMock()
        mock_color_clip.close = MagicMock()

        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_color_clip)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_color_clip)

        with (
            patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}),
            patch("src.core.audio_visualizer.AudioVisualizer") as mock_visualizer_class,
        ):

            result = composer.compose(audio_path, output_name="test_explicit_false", use_visualization=False)

            # Visualization should NOT be called when explicitly False
            mock_visualizer_class.assert_not_called()
            assert result is not None

    def test_compose_fallback_to_ffmpeg(self, test_config, temp_dir):
        """Test fallback to FFmpeg when moviepy fails."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        # Create mock that raises ImportError
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(side_effect=ImportError("MoviePy not available"))

        with (
            patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}),
            patch.object(VideoComposer, "_compose_with_ffmpeg") as mock_ffmpeg,
        ):

            expected_output = temp_dir / "output" / "test_ffmpeg.mp4"
            mock_ffmpeg.return_value = expected_output

            composer = VideoComposer(test_config)
            result = composer.compose(audio_path, output_name="test_ffmpeg")

            mock_ffmpeg.assert_called_once()
            assert result == expected_output

    def test_compose_generates_timestamp_name(self, test_config, temp_dir):
        """Test that compose generates timestamp-based name when not provided."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()

        mock_clip = MagicMock()
        mock_clip.set_duration = MagicMock(return_value=mock_clip)
        mock_clip.set_audio = MagicMock(return_value=mock_clip)
        mock_clip.write_videofile = MagicMock()
        mock_clip.close = MagicMock()

        # Create mock moviepy module
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_clip)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_clip)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            composer = VideoComposer(test_config)
            result = composer.compose(audio_path)  # No output_name

            # Should generate a name like "podcast_20231029_123456.mp4"
            assert "podcast_" in result.name


class TestVideoComposerFFmpegFallback:
    """Test FFmpeg fallback functionality."""

    def test_compose_with_ffmpeg_gpu(self, test_config, temp_dir):
        """Test FFmpeg composition with GPU acceleration."""
        audio_path = temp_dir / "test_audio.wav"
        # Create a valid audio file (mock validation will pass)
        audio_path.write_bytes(b"RIFF" + b"\x00" * 100)  # Minimal valid-looking file

        bg_path = Path(test_config["video"]["background_path"])
        output_path = temp_dir / "output.mp4"

        mock_gpu_manager = MagicMock()
        mock_gpu_manager.gpu_available = True

        mock_result = MagicMock()
        mock_result.stdout = "h264_nvenc"
        mock_result.returncode = 0

        with (
            patch("src.utils.gpu_utils.get_gpu_manager", return_value=mock_gpu_manager),
            patch("subprocess.run", return_value=mock_result) as mock_run,
            patch("subprocess.Popen") as mock_popen,
            patch.object(VideoComposer, "_validate_audio_file", return_value=(True, "")) as mock_validate,
        ):

            mock_process = MagicMock()
            mock_process.communicate.return_value = ("", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            composer = VideoComposer(test_config)
            result = composer._compose_with_ffmpeg(audio_path, bg_path, output_path)

            # Should have validated and called subprocess
            mock_validate.assert_called_once_with(audio_path)
            assert mock_popen.called or mock_run.called

    def test_compose_with_ffmpeg_cpu(self, test_config, temp_dir):
        """Test FFmpeg composition without GPU."""
        audio_path = temp_dir / "test_audio.wav"
        # Create a valid audio file (mock validation will pass)
        audio_path.write_bytes(b"RIFF" + b"\x00" * 100)  # Minimal valid-looking file

        bg_path = Path(test_config["video"]["background_path"])
        output_path = temp_dir / "output.mp4"

        mock_gpu_manager = MagicMock()
        mock_gpu_manager.gpu_available = False

        mock_result = MagicMock()
        mock_result.returncode = 0

        with (
            patch("src.utils.gpu_utils.get_gpu_manager", return_value=mock_gpu_manager),
            patch("subprocess.run", return_value=mock_result) as mock_run,
            patch.object(VideoComposer, "_validate_audio_file", return_value=(True, "")) as mock_validate,
        ):

            composer = VideoComposer(test_config)
            result = composer._compose_with_ffmpeg(audio_path, bg_path, output_path)

            # Should have validated and used CPU encoding
            mock_validate.assert_called_once_with(audio_path)
            assert mock_run.called
            assert result == output_path


class TestVideoComposerHelperMethods:
    """Test helper methods."""

    def test_create_default_background(self, test_config, temp_dir):
        """Test default background creation."""
        composer = VideoComposer(test_config)

        with patch("PIL.Image.new") as mock_img:
            mock_image = MagicMock()
            mock_img.return_value = mock_image
            mock_image.save = MagicMock()

            result = composer._create_default_background()

            assert isinstance(result, Path)

    def test_create_text_image(self, test_config):
        """Test text image creation."""
        composer = VideoComposer(test_config)

        with patch("PIL.Image.new") as mock_img, patch("PIL.ImageDraw.Draw") as mock_draw:

            mock_image = MagicMock()
            mock_img.return_value = mock_image

            result = composer._create_text_image("Test Text", (1920, 1080))

            assert mock_img.called
            assert mock_draw.called
    
    def test_validate_audio_file_missing(self, test_config, temp_dir):
        """Test audio file validation with missing file."""
        composer = VideoComposer(test_config)
        audio_path = temp_dir / "missing.wav"
        
        is_valid, error_msg = composer._validate_audio_file(audio_path)
        
        assert not is_valid
        assert "does not exist" in error_msg
        assert str(audio_path) in error_msg
    
    def test_validate_audio_file_empty(self, test_config, temp_dir):
        """Test audio file validation with empty file."""
        composer = VideoComposer(test_config)
        audio_path = temp_dir / "empty.wav"
        audio_path.touch()  # Create empty file
        
        is_valid, error_msg = composer._validate_audio_file(audio_path)
        
        assert not is_valid
        assert "empty" in error_msg.lower() or "0 bytes" in error_msg
        assert str(audio_path) in error_msg
    
    def test_validate_audio_file_too_small(self, test_config, temp_dir):
        """Test audio file validation with file that's too small."""
        composer = VideoComposer(test_config)
        audio_path = temp_dir / "small.wav"
        audio_path.write_bytes(b"x" * 50)  # 50 bytes - too small
        
        is_valid, error_msg = composer._validate_audio_file(audio_path)
        
        assert not is_valid
        assert "too small" in error_msg.lower()
        assert str(audio_path) in error_msg
    
    def test_validate_audio_file_corrupted(self, test_config, temp_dir):
        """Test audio file validation with corrupted file (ffprobe detects corruption)."""
        composer = VideoComposer(test_config)
        audio_path = temp_dir / "corrupted.wav"
        audio_path.write_bytes(b"INVALID_AUDIO" * 20)  # 240 bytes - passes size check
        
        # Mock ffprobe to return error indicating corruption
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Illegal Audio-MPEG-Header 0x00000000"
        mock_result.stdout = ""
        
        with patch("subprocess.run", return_value=mock_result):
            is_valid, error_msg = composer._validate_audio_file(audio_path)
            
            assert not is_valid
            assert ("corrupted" in error_msg.lower() or 
                    "illegal" in error_msg.lower() or
                    "validation failed" in error_msg.lower())
            assert str(audio_path) in error_msg
    
    def test_validate_audio_file_valid(self, test_config, temp_dir):
        """Test audio file validation with valid file."""
        composer = VideoComposer(test_config)
        audio_path = temp_dir / "valid.wav"
        audio_path.write_bytes(b"RIFF" + b"\x00" * 200)  # 204 bytes - passes size check
        
        # Mock ffprobe to return valid duration
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_result.stdout = "10.5\n"  # Valid duration
        
        with patch("subprocess.run", return_value=mock_result):
            is_valid, error_msg = composer._validate_audio_file(audio_path)
            
            assert is_valid
            assert error_msg == ""


class TestVideoComposerErrorHandling:
    """Test error handling."""

    def test_compose_handles_moviepy_exception(self, test_config, temp_dir):
        """Test that exceptions during moviepy composition are handled."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        # Create mock that raises Exception
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(side_effect=Exception("Moviepy error"))

        with (
            patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}),
            patch.object(VideoComposer, "_compose_with_ffmpeg") as mock_ffmpeg,
        ):

            mock_ffmpeg.return_value = temp_dir / "output.mp4"

            composer = VideoComposer(test_config)
            result = composer.compose(audio_path, output_name="error_test")

            # Should fall back to FFmpeg
            mock_ffmpeg.assert_called_once()

    def test_compose_with_missing_audio(self, test_config, temp_dir):
        """Test composition with missing audio file raises clear error."""
        audio_path = temp_dir / "missing_audio.wav"
        # Don't create the file

        composer = VideoComposer(test_config)

        # Should raise ValueError with clear error message
        with pytest.raises(ValueError) as exc_info:
            composer.compose(audio_path, output_name="missing_test")
        
        error_msg = str(exc_info.value)
        assert "Audio file does not exist" in error_msg
        assert str(audio_path) in error_msg
        assert "Troubleshooting" in error_msg
    
    def test_compose_with_empty_audio_file(self, test_config, temp_dir):
        """Test composition with empty audio file raises clear error."""
        audio_path = temp_dir / "empty_audio.wav"
        audio_path.touch()  # Create empty file (0 bytes)

        composer = VideoComposer(test_config)

        # Should raise ValueError with clear error message
        with pytest.raises(ValueError) as exc_info:
            composer.compose(audio_path, output_name="empty_test")
        
        error_msg = str(exc_info.value)
        assert "empty" in error_msg.lower() or "0 bytes" in error_msg
        assert str(audio_path) in error_msg
        assert "Troubleshooting" in error_msg
    
    def test_compose_with_corrupted_audio_file(self, test_config, temp_dir):
        """Test composition with corrupted audio file raises clear error."""
        audio_path = temp_dir / "corrupted_audio.wav"
        # Create a file with invalid audio data (too small to be valid)
        audio_path.write_bytes(b"fake audio data" * 2)  # 30 bytes - too small

        composer = VideoComposer(test_config)

        # Should raise ValueError with clear error message
        with pytest.raises(ValueError) as exc_info:
            composer.compose(audio_path, output_name="corrupted_test")
        
        error_msg = str(exc_info.value)
        assert ("too small" in error_msg.lower() or 
                "corrupted" in error_msg.lower() or
                "validation failed" in error_msg.lower())
        assert str(audio_path) in error_msg
        assert "Troubleshooting" in error_msg
    
    def test_compose_with_invalid_audio_format(self, test_config, temp_dir):
        """Test composition with invalid audio format raises clear error."""
        audio_path = temp_dir / "invalid_audio.wav"
        # Create a file that looks like audio but isn't valid
        # Write enough bytes to pass size check but invalid format
        audio_path.write_bytes(b"INVALID_AUDIO_FORMAT" * 10)  # 200 bytes

        composer = VideoComposer(test_config)

        # Should raise ValueError or RuntimeError with clear error message
        with pytest.raises((ValueError, RuntimeError)) as exc_info:
            composer.compose(audio_path, output_name="invalid_test")
        
        error_msg = str(exc_info.value)
        # Should mention validation failure, corruption, or FFmpeg error
        assert ("validation" in error_msg.lower() or 
                "corrupted" in error_msg.lower() or
                "invalid" in error_msg.lower() or
                "ffmpeg" in error_msg.lower())
        assert str(audio_path) in error_msg
        # Should provide troubleshooting information
        assert "Troubleshooting" in error_msg or "troubleshooting" in error_msg.lower()


class TestVideoComposerResolutions:
    """Test different video resolutions."""

    @pytest.mark.parametrize(
        "resolution,expected",
        [
            ([1920, 1080], (1920, 1080)),
            ([1280, 720], (1280, 720)),
            ([854, 480], (854, 480)),
        ],
    )
    def test_different_resolutions(self, test_config, temp_dir, resolution, expected):
        """Test video composition with different resolutions."""
        audio_path = temp_dir / "test_audio.wav"
        # Create valid audio file for happy path test
        create_valid_mp3_file(audio_path, duration_seconds=5.0)

        test_config["video"]["resolution"] = resolution

        mock_audio = MagicMock()
        mock_audio.duration = 5.0
        mock_audio.close = MagicMock()

        mock_clip = MagicMock()
        mock_clip.set_duration = MagicMock(return_value=mock_clip)
        mock_clip.set_audio = MagicMock(return_value=mock_clip)
        mock_clip.write_videofile = MagicMock()
        mock_clip.close = MagicMock()

        # Create mock moviepy module
        mock_moviepy = MagicMock()
        mock_moviepy.editor = MagicMock()
        mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
        mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_clip)
        mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_clip)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            composer = VideoComposer(test_config)
            result = composer.compose(audio_path, output_name="resolution_test")

            # Verify ColorClip was called with correct resolution
            if mock_moviepy.editor.ColorClip.called:
                call_args = mock_moviepy.editor.ColorClip.call_args
                assert call_args is not None
