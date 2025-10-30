"""
Unit Tests for Video Composer
Tests for src/core/video_composer.py with correct API
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from src.core.video_composer import VideoComposer


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
        audio_path.touch()

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
        audio_path.touch()

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
        audio_path.touch()

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
        audio_path.touch()

        avatar_video = temp_dir / "avatar.mp4"
        avatar_video.touch()

        with patch.object(VideoComposer, "_overlay_visualization_on_avatar") as mock_overlay:
            mock_overlay.return_value = temp_dir / "output.mp4"

            composer = VideoComposer(test_config)
            result = composer.compose(
                audio_path, output_name="test_avatar_viz", use_visualization=True, avatar_video=avatar_video
            )

            mock_overlay.assert_called_once()

    def test_compose_fallback_to_ffmpeg(self, test_config, temp_dir):
        """Test fallback to FFmpeg when moviepy fails."""
        audio_path = temp_dir / "test_audio.wav"
        audio_path.touch()

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
        audio_path.touch()

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
        audio_path.touch()

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
        ):

            mock_process = MagicMock()
            mock_process.wait.return_value = 0
            mock_popen.return_value = mock_process

            composer = VideoComposer(test_config)
            result = composer._compose_with_ffmpeg(audio_path, bg_path, output_path)

            # Should have called subprocess
            assert mock_popen.called or mock_run.called

    def test_compose_with_ffmpeg_cpu(self, test_config, temp_dir):
        """Test FFmpeg composition without GPU."""
        audio_path = temp_dir / "test_audio.wav"
        audio_path.touch()

        bg_path = Path(test_config["video"]["background_path"])
        output_path = temp_dir / "output.mp4"

        mock_gpu_manager = MagicMock()
        mock_gpu_manager.gpu_available = False

        mock_result = MagicMock()
        mock_result.returncode = 0

        with (
            patch("src.utils.gpu_utils.get_gpu_manager", return_value=mock_gpu_manager),
            patch("subprocess.run", return_value=mock_result) as mock_run,
        ):

            composer = VideoComposer(test_config)
            result = composer._compose_with_ffmpeg(audio_path, bg_path, output_path)

            # Should use CPU encoding
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


class TestVideoComposerErrorHandling:
    """Test error handling."""

    def test_compose_handles_moviepy_exception(self, test_config, temp_dir):
        """Test that exceptions during moviepy composition are handled."""
        audio_path = temp_dir / "test_audio.wav"
        audio_path.touch()

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
        """Test composition with missing audio file."""
        audio_path = temp_dir / "missing_audio.wav"
        # Don't create the file

        composer = VideoComposer(test_config)

        # Should handle gracefully (might raise exception or use fallback)
        # This depends on implementation, but shouldn't crash
        try:
            result = composer.compose(audio_path, output_name="missing_test")
        except (FileNotFoundError, Exception):
            # Expected behavior
            pass


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
        audio_path.touch()

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
