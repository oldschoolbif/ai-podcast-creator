"""
Integration tests for Web Interface - Test Gradio interface end-to-end
These tests exercise web interface code paths directly to improve coverage.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.integration
class TestWebInterfaceIntegration:
    """Integration tests for web interface - exercise full code paths."""

    def test_get_gpu_status_integration(self):
        """Test get_gpu_status function."""
        from src.gui.web_interface import get_gpu_status

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = True
        mock_gpu.gpu_name = "NVIDIA RTX 4060"
        mock_gpu.gpu_memory = 8.0

        with patch("src.gui.web_interface.get_gpu_manager", return_value=mock_gpu):
            status = get_gpu_status()
            assert "✅" in status
            assert "GPU" in status
            assert "NVIDIA RTX 4060" in status

    def test_get_gpu_status_no_gpu_integration(self):
        """Test get_gpu_status when GPU is not available."""
        from src.gui.web_interface import get_gpu_status

        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False

        with patch("src.gui.web_interface.get_gpu_manager", return_value=mock_gpu):
            status = get_gpu_status()
            assert "⚠️" in status
            assert "CPU Mode" in status

    def test_create_podcast_success_integration(self, test_config, temp_dir):
        """Test create_podcast function success path."""
        from src.gui.web_interface import create_podcast

        # Mock script file
        script_file = MagicMock()
        script_file.name = str(temp_dir / "test_script.txt")
        Path(script_file.name).write_text("# Test Podcast\nHello world", encoding="utf-8")

        # Setup mocks
        with (
            patch("src.gui.web_interface.load_config", return_value=test_config),
            patch("src.gui.web_interface.ScriptParser") as mock_parser,
            patch("src.gui.web_interface.TTSEngine") as mock_tts,
            patch("src.gui.web_interface.AudioMixer") as mock_mixer,
            patch("src.gui.web_interface.VideoComposer") as mock_composer,
        ):
            mock_parser_instance = MagicMock()
            mock_parser_instance.parse.return_value = {
                "text": "Hello world",
                "music_cues": [],
                "metadata": {"title": "Test Podcast"},
            }
            mock_parser.return_value = mock_parser_instance

            mock_tts_instance = MagicMock()
            audio_path = temp_dir / "audio.mp3"
            audio_path.write_bytes(b"audio data")
            mock_tts_instance.generate.return_value = audio_path
            mock_tts.return_value = mock_tts_instance

            mock_mixer_instance = MagicMock()
            mixed_audio = temp_dir / "mixed.mp3"
            mixed_audio.write_bytes(b"mixed audio")
            mock_mixer_instance.mix.return_value = mixed_audio
            mock_mixer.return_value = mock_mixer_instance

            mock_composer_instance = MagicMock()
            final_video = temp_dir / "output" / "test_script.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video data")
            mock_composer_instance.compose.return_value = final_video
            mock_composer.return_value = mock_composer_instance

            mock_progress = MagicMock()

            result_video, result_message = create_podcast(
                script_file=script_file,
                music_file=None,
                music_description=None,
                avatar_style="Professional Studio (Default)",
                voice_type="gtts (Free, Cloud-based)",
                voice_speed=1.0,
                video_quality="High (1080p)",
                output_name=None,
                progress=mock_progress,
            )

            assert result_video == str(final_video)
            assert "✅" in result_message
            assert mock_progress.called

    def test_create_podcast_no_script_file_integration(self, test_config):
        """Test create_podcast without script file."""
        from src.gui.web_interface import create_podcast

        with patch("src.gui.web_interface.load_config", return_value=test_config):
            mock_progress = MagicMock()

            result_video, result_message = create_podcast(
                script_file=None,
                music_file=None,
                music_description=None,
                avatar_style="Default",
                voice_type="gtts",
                voice_speed=1.0,
                video_quality="High (1080p)",
                output_name=None,
                progress=mock_progress,
            )

            assert result_video is None
            assert "❌" in result_message
            assert "upload" in result_message.lower()

    def test_create_podcast_with_music_file_integration(self, test_config, temp_dir):
        """Test create_podcast with uploaded music file."""
        from src.gui.web_interface import create_podcast

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        music_file = MagicMock()
        music_file.name = str(temp_dir / "music.mp3")

        with (
            patch("src.gui.web_interface.load_config", return_value=test_config),
            patch("src.gui.web_interface.ScriptParser") as mock_parser,
            patch("src.gui.web_interface.TTSEngine") as mock_tts,
            patch("src.gui.web_interface.AudioMixer") as mock_mixer,
            patch("src.gui.web_interface.VideoComposer") as mock_composer,
        ):
            mock_parser_instance = MagicMock()
            mock_parser_instance.parse.return_value = {"text": "Test", "music_cues": []}
            mock_parser.return_value = mock_parser_instance

            mock_tts_instance = MagicMock()
            audio_path = temp_dir / "audio.mp3"
            audio_path.write_bytes(b"audio")
            mock_tts_instance.generate.return_value = audio_path
            mock_tts.return_value = mock_tts_instance

            mock_mixer_instance = MagicMock()
            mixed_audio = temp_dir / "mixed.mp3"
            mixed_audio.write_bytes(b"mixed")
            mock_mixer_instance.mix.return_value = mixed_audio
            mock_mixer.return_value = mock_mixer_instance

            mock_composer_instance = MagicMock()
            final_video = temp_dir / "output" / "test.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer_instance.compose.return_value = final_video
            mock_composer.return_value = mock_composer_instance

            result_video, result_message = create_podcast(
                script_file=script_file,
                music_file=music_file,
                music_description=None,
                avatar_style="Default",
                voice_type="gtts",
                voice_speed=1.0,
                video_quality="Medium (720p)",
                output_name="custom_name",
                progress=MagicMock(),
            )

            assert result_video is not None
            assert "✅" in result_message

    def test_create_podcast_with_music_description_integration(self, test_config, temp_dir):
        """Test create_podcast with music description."""
        from src.gui.web_interface import create_podcast

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        with (
            patch("src.gui.web_interface.load_config", return_value=test_config),
            patch("src.gui.web_interface.ScriptParser") as mock_parser,
            patch("src.gui.web_interface.TTSEngine") as mock_tts,
            patch("src.gui.web_interface.MusicGenerator") as mock_music,
            patch("src.gui.web_interface.AudioMixer") as mock_mixer,
            patch("src.gui.web_interface.VideoComposer") as mock_composer,
        ):
            mock_parser_instance = MagicMock()
            mock_parser_instance.parse.return_value = {"text": "Test", "music_cues": []}
            mock_parser.return_value = mock_parser_instance

            mock_tts_instance = MagicMock()
            audio_path = temp_dir / "audio.mp3"
            audio_path.write_bytes(b"audio")
            mock_tts_instance.generate.return_value = audio_path
            mock_tts.return_value = mock_tts_instance

            mock_music_instance = MagicMock()
            music_path = temp_dir / "generated_music.wav"
            music_path.write_bytes(b"music")
            mock_music_instance.generate.return_value = music_path
            mock_music.return_value = mock_music_instance

            mock_mixer_instance = MagicMock()
            mixed_audio = temp_dir / "mixed.mp3"
            mixed_audio.write_bytes(b"mixed")
            mock_mixer_instance.mix.return_value = mixed_audio
            mock_mixer.return_value = mock_mixer_instance

            mock_composer_instance = MagicMock()
            final_video = temp_dir / "output" / "test.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer_instance.compose.return_value = final_video
            mock_composer.return_value = mock_composer_instance

            result_video, result_message = create_podcast(
                script_file=script_file,
                music_file=None,
                music_description="upbeat electronic",
                avatar_style="Default",
                voice_type="gtts",
                voice_speed=1.0,
                video_quality="Low (480p)",
                output_name=None,
                progress=MagicMock(),
            )

            assert result_video is not None
            assert mock_music_instance.generate.called

    def test_create_podcast_exception_handling_integration(self, temp_dir):
        """Test error handling in create_podcast."""
        from src.gui.web_interface import create_podcast

        with patch("src.gui.web_interface.load_config", side_effect=Exception("Config error")):
            result_video, result_message = create_podcast(
                script_file=MagicMock(),
                music_file=None,
                music_description=None,
                avatar_style="Default",
                voice_type="gtts",
                voice_speed=1.0,
                video_quality="High (1080p)",
                output_name=None,
                progress=MagicMock(),
            )

            assert result_video is None
            assert "❌" in result_message
            assert "Error" in result_message

    def test_create_gradio_interface_integration(self):
        """Test create_gradio_interface function."""
        from src.gui.web_interface import create_gradio_interface

        with patch("src.gui.web_interface.gr") as mock_gr:
            mock_interface = MagicMock()
            mock_blocks = MagicMock()
            mock_blocks.__enter__.return_value = mock_interface
            mock_blocks.__exit__.return_value = None
            mock_gr.Blocks.return_value = mock_blocks

            result = create_gradio_interface()

            assert result == mock_interface
            assert mock_gr.Blocks.called

    def test_launch_web_interface_integration(self):
        """Test launch_web_interface function."""
        from src.gui.web_interface import launch_web_interface

        mock_interface = MagicMock()

        with patch("src.gui.web_interface.create_gradio_interface", return_value=mock_interface):
            launch_web_interface(share=False, server_name="127.0.0.1", server_port=7860)

            assert mock_interface.launch.called
            call_kwargs = mock_interface.launch.call_args[1]
            assert call_kwargs["share"] is False
            assert call_kwargs["server_name"] == "127.0.0.1"
            assert call_kwargs["server_port"] == 7860

    def test_launch_web_interface_with_auth_integration(self):
        """Test launch with authentication."""
        from src.gui.web_interface import launch_web_interface

        mock_interface = MagicMock()

        with patch("src.gui.web_interface.create_gradio_interface", return_value=mock_interface):
            launch_web_interface(auth=("user", "pass"))

            call_kwargs = mock_interface.launch.call_args[1]
            assert call_kwargs["auth"] == ("user", "pass")

    def test_launch_web_interface_with_share_integration(self):
        """Test launch with public sharing."""
        from src.gui.web_interface import launch_web_interface

        mock_interface = MagicMock()

        with patch("src.gui.web_interface.create_gradio_interface", return_value=mock_interface):
            launch_web_interface(share=True)

            call_kwargs = mock_interface.launch.call_args[1]
            assert call_kwargs["share"] is True

    def test_video_quality_settings_integration(self, test_config, temp_dir):
        """Test video quality configuration in create_podcast."""
        from src.gui.web_interface import create_podcast

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        with (
            patch("src.gui.web_interface.load_config", return_value=test_config),
            patch("src.gui.web_interface.ScriptParser") as mock_parser,
            patch("src.gui.web_interface.TTSEngine") as mock_tts,
            patch("src.gui.web_interface.AudioMixer") as mock_mixer,
            patch("src.gui.web_interface.VideoComposer") as mock_composer,
        ):
            mock_parser_instance = MagicMock()
            mock_parser_instance.parse.return_value = {"text": "Test"}
            mock_parser.return_value = mock_parser_instance

            mock_tts_instance = MagicMock()
            audio_path = temp_dir / "audio.mp3"
            audio_path.write_bytes(b"audio")
            mock_tts_instance.generate.return_value = audio_path
            mock_tts.return_value = mock_tts_instance

            mock_mixer_instance = MagicMock()
            mixed_audio = temp_dir / "mixed.mp3"
            mixed_audio.write_bytes(b"mixed")
            mock_mixer_instance.mix.return_value = mixed_audio
            mock_mixer.return_value = mock_mixer_instance

            mock_composer_instance = MagicMock()
            final_video = temp_dir / "output" / "test.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer_instance.compose.return_value = final_video
            mock_composer.return_value = mock_composer_instance

            create_podcast(
                script_file=script_file,
                music_file=None,
                music_description=None,
                avatar_style="Default",
                voice_type="gtts",
                voice_speed=1.0,
                video_quality="Medium (720p)",
                output_name=None,
                progress=MagicMock(),
            )

            # Verify composer.compose was called with quality="medium"
            mock_composer_instance.compose.assert_called_once()
            call_kwargs = mock_composer_instance.compose.call_args[1]
            assert call_kwargs.get("quality") == "medium"

    def test_voice_type_configuration_integration(self, test_config, temp_dir):
        """Test voice type configuration in create_podcast."""
        from src.gui.web_interface import create_podcast

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        test_config["tts"] = {"engine": "gtts"}

        with (
            patch("src.gui.web_interface.load_config", return_value=test_config),
            patch("src.gui.web_interface.ScriptParser") as mock_parser,
            patch("src.gui.web_interface.TTSEngine") as mock_tts,
            patch("src.gui.web_interface.AudioMixer") as mock_mixer,
            patch("src.gui.web_interface.VideoComposer") as mock_composer,
        ):
            mock_parser_instance = MagicMock()
            mock_parser_instance.parse.return_value = {"text": "Test"}
            mock_parser.return_value = mock_parser_instance

            mock_tts_instance = MagicMock()
            audio_path = temp_dir / "audio.mp3"
            audio_path.write_bytes(b"audio")
            mock_tts_instance.generate.return_value = audio_path
            mock_tts.return_value = mock_tts_instance

            mock_mixer_instance = MagicMock()
            mixed_audio = temp_dir / "mixed.mp3"
            mixed_audio.write_bytes(b"mixed")
            mock_mixer_instance.mix.return_value = mixed_audio
            mock_mixer.return_value = mock_mixer_instance

            mock_composer_instance = MagicMock()
            final_video = temp_dir / "output" / "test.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer_instance.compose.return_value = final_video
            mock_composer.return_value = mock_composer_instance

            create_podcast(
                script_file=script_file,
                music_file=None,
                music_description=None,
                avatar_style="Default",
                voice_type="gtts (Free, Cloud-based)",
                voice_speed=1.0,
                video_quality="High (1080p)",
                output_name=None,
                progress=MagicMock(),
            )

            # Verify config was updated with voice type
            assert test_config["tts"]["engine"] == "gtts (Free, Cloud-based)"
            mock_tts.assert_called_once()

