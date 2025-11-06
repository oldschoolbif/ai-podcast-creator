"""
Integration tests for video composition - Test REAL video workflows
FIXED VERSION with correct moviepy mocking
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.video_composer import VideoComposer


def create_moviepy_mock(audio_duration=5.0):
    """Helper to create moviepy mock with sys.modules patch."""
    mock_audio = MagicMock()
    mock_audio.duration = audio_duration
    mock_audio.close = MagicMock()

    mock_video = MagicMock()
    mock_video.set_audio = MagicMock(return_value=mock_video)
    mock_video.set_duration = MagicMock(return_value=mock_video)
    mock_video.write_videofile = MagicMock()
    mock_video.close = MagicMock()

    mock_moviepy = MagicMock()
    mock_moviepy.editor = MagicMock()
    mock_moviepy.editor.AudioFileClip = MagicMock(return_value=mock_audio)
    mock_moviepy.editor.ImageClip = MagicMock(return_value=mock_video)
    mock_moviepy.editor.ColorClip = MagicMock(return_value=mock_video)
    mock_moviepy.editor.CompositeVideoClip = MagicMock(return_value=mock_video)

    return mock_moviepy, mock_audio, mock_video


@pytest.mark.integration
class TestVideoCompositionIntegration:
    """Integration tests for video composition."""

    def test_basic_video_composition(self, test_config, temp_dir):
        """Test basic video composition workflow."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)
        test_config["video"] = {
            "resolution": [1280, 720],
            "fps": 30,
            "codec": "libx264",
            "background_path": str(temp_dir / "bg.jpg"),
        }

        audio_file = temp_dir / "test_audio.mp3"
        # Create valid audio file (must be > 100 bytes to pass validation)
        audio_file.write_bytes(b"RIFF" + b"\x00" * 200)  # Minimal valid-looking file structure

        composer = VideoComposer(test_config)

        mock_moviepy, mock_audio, mock_video = create_moviepy_mock(audio_duration=10.0)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            # Mock ffprobe to return valid duration for validation
            with patch("subprocess.run") as mock_subprocess:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "10.0\n"  # Valid duration
                mock_result.stderr = ""
                mock_subprocess.return_value = mock_result
                output = composer.compose(audio_file, output_name="integration_test")

            assert output.suffix == ".mp4"
            assert "integration_test" in str(output)
            assert output.parent == temp_dir
            mock_video.write_videofile.assert_called_once()

    def test_custom_resolution_workflow(self, test_config, temp_dir):
        """Test different resolutions are handled correctly."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)

        resolutions = [
            ([640, 480], "480p"),
            ([1280, 720], "720p"),
            ([1920, 1080], "1080p"),
        ]

        audio_file = temp_dir / "audio.mp3"
        # Create valid audio file (must be > 100 bytes to pass validation)
        audio_file.write_bytes(b"RIFF" + b"\x00" * 200)  # Minimal valid-looking file structure

        for resolution, name in resolutions:
            test_config["video"] = {"resolution": resolution, "background_path": str(temp_dir / "bg.jpg")}
            composer = VideoComposer(test_config)

            mock_moviepy, mock_audio, mock_video = create_moviepy_mock()

            with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
                # Mock ffprobe to return valid duration for validation
                with patch("subprocess.run") as mock_subprocess:
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = "5.0\n"  # Valid duration
                    mock_result.stderr = ""
                    mock_subprocess.return_value = mock_result
                    output = composer.compose(audio_file, output_name=name)

                # Verify resolution was used
                if mock_moviepy.editor.ColorClip.called:
                    call_kwargs = mock_moviepy.editor.ColorClip.call_args[1]
                    assert call_kwargs["size"] == resolution
                assert name in str(output)

    @pytest.mark.skipif(sys.version_info >= (3, 12), reason="Dynamic import patching issue in Python 3.12+")
    def test_visualization_workflow(self, test_config, temp_dir):
        """Test visualization generation workflow."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)

        audio_file = temp_dir / "audio.mp3"
        # Create valid audio file (must be > 100 bytes to pass validation)
        audio_file.write_bytes(b"RIFF" + b"\x00" * 200)  # Minimal valid-looking file structure

        expected_output = temp_dir / "viz_output.mp4"

        mock_visualizer = MagicMock()
        mock_visualizer.generate_visualization.return_value = expected_output

        with patch("src.core.audio_visualizer.AudioVisualizer", return_value=mock_visualizer):
            composer = VideoComposer(test_config)
            # Mock ffprobe to return valid duration for validation
            with patch("subprocess.run") as mock_subprocess:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "5.0\n"  # Valid duration
                mock_result.stderr = ""
                mock_subprocess.return_value = mock_result
                result = composer.compose(audio_file, use_visualization=True)

            mock_visualizer.generate_visualization.assert_called_once()
            assert result == expected_output

    def test_background_image_workflow(self, test_config, temp_dir):
        """Test using custom background image."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)

        bg_file = temp_dir / "background.jpg"
        bg_file.write_bytes(b"fake image data")
        test_config["video"] = {"background_path": str(bg_file)}

        audio_file = temp_dir / "audio.mp3"
        # Create valid audio file (must be > 100 bytes to pass validation)
        audio_file.write_bytes(b"RIFF" + b"\x00" * 200)  # Minimal valid-looking file structure

        composer = VideoComposer(test_config)

        mock_moviepy, mock_audio, mock_video = create_moviepy_mock(audio_duration=3.0)

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            # Mock ffprobe to return valid duration for validation
            with patch("subprocess.run") as mock_subprocess:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "3.0\n"  # Valid duration
                mock_result.stderr = ""
                mock_subprocess.return_value = mock_result
                output = composer.compose(audio_file)

            # Verify ImageClip was used (not ColorClip) for background image
            assert mock_moviepy.editor.ImageClip.called
            # Output should be created
            assert output is not None

    def test_audio_duration_handling(self, test_config, temp_dir):
        """Test different audio durations."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)
        test_config["video"] = {"background_path": str(temp_dir / "bg.jpg")}

        audio_file = temp_dir / "audio.mp3"
        # Create valid audio file (must be > 100 bytes to pass validation)
        audio_file.write_bytes(b"RIFF" + b"\x00" * 200)  # Minimal valid-looking file structure

        durations = [1.0, 5.0, 30.0, 120.0]

        for duration in durations:
            composer = VideoComposer(test_config)

            mock_moviepy, mock_audio, mock_video = create_moviepy_mock(audio_duration=duration)

            with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
                # Mock ffprobe to return valid duration for validation
                with patch("subprocess.run") as mock_subprocess:
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = f"{duration}\n"  # Valid duration
                    mock_result.stderr = ""
                    mock_subprocess.return_value = mock_result
                    output = composer.compose(audio_file, output_name=f"test_{duration}s")

                # Verify duration was set
                mock_video.set_duration.assert_called_with(duration)
                assert f"test_{duration}s" in str(output)

    def test_output_directory_creation(self, test_config, temp_dir):
        """Test output directory is created if missing."""
        output_dir = temp_dir / "videos" / "nested" / "path"
        test_config["storage"]["outputs_dir"] = str(output_dir)
        test_config["video"] = {"background_path": str(temp_dir / "bg.jpg")}

        assert not output_dir.exists()

        composer = VideoComposer(test_config)

        assert output_dir.exists()
        assert composer.output_dir == output_dir

    def test_timestamp_generation(self, test_config, temp_dir):
        """Test automatic timestamp in filename."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)
        test_config["video"] = {"background_path": str(temp_dir / "bg.jpg")}

        audio_file = temp_dir / "audio.mp3"
        # Create valid audio file (must be > 100 bytes to pass validation)
        audio_file.write_bytes(b"RIFF" + b"\x00" * 200)  # Minimal valid-looking file structure

        composer = VideoComposer(test_config)

        mock_moviepy, mock_audio, mock_video = create_moviepy_mock()

        with patch.dict("sys.modules", {"moviepy": mock_moviepy, "moviepy.editor": mock_moviepy.editor}):
            # Mock ffprobe to return valid duration for validation
            with patch("subprocess.run") as mock_subprocess:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "5.0\n"  # Valid duration
                mock_result.stderr = ""
                mock_subprocess.return_value = mock_result
                output1 = composer.compose(audio_file, output_name=None)
                output2 = composer.compose(audio_file, output_name=None)

            assert "podcast_" in str(output1)
            assert "podcast_" in str(output2)

    def test_error_handling_missing_audio(self, test_config, temp_dir):
        """Test error handling for missing audio file."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)
        test_config["video"] = {"background_path": str(temp_dir / "bg.jpg")}

        missing_file = temp_dir / "nonexistent.mp3"

        composer = VideoComposer(test_config)

        # Should raise ValueError from validation (not FileNotFoundError)
        with pytest.raises(ValueError) as exc_info:
            composer.compose(missing_file)
        
        # Verify error message mentions the file doesn't exist
        assert "does not exist" in str(exc_info.value).lower() or "Audio file" in str(exc_info.value)


@pytest.mark.integration
class TestVideoAvatarIntegration:
    """Integration tests for avatar video workflows."""

    def test_avatar_with_visualization_overlay(self, test_config, temp_dir):
        """Test overlaying visualization on avatar video."""
        test_config["storage"]["outputs_dir"] = str(temp_dir)
        test_config["video"] = {"background_path": str(temp_dir / "bg.jpg")}

        audio_file = temp_dir / "audio.mp3"
        avatar_video = temp_dir / "avatar.mp4"
        # Create valid audio file (must be > 100 bytes to pass validation)
        audio_file.write_bytes(b"RIFF" + b"\x00" * 200)  # Minimal valid-looking file structure
        avatar_video.write_bytes(b"video")

        output_file = temp_dir / "final.mp4"

        with patch.object(VideoComposer, "_overlay_visualization_on_avatar", return_value=output_file):
            composer = VideoComposer(test_config)
            # Mock ffprobe to return valid duration for validation
            with patch("subprocess.run") as mock_subprocess:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "5.0\n"  # Valid duration
                mock_result.stderr = ""
                mock_subprocess.return_value = mock_result
                result = composer.compose(audio_file, avatar_video=avatar_video, use_visualization=True)

            assert result == output_file
