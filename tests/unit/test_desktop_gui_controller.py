"""
Unit Tests for Desktop GUI Controller
Tests business logic separated from GUI components.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.gui.desktop_gui_controller import PodcastCreatorController


def make_controller_config(base_dir: Path) -> dict:
    """Create test configuration for controller."""
    return {
        "app": {"name": "AI Podcast Creator", "version": "1.0.0"},
        "tts": {"engine": "gtts"},
        "video": {"resolution": [1920, 1080], "fps": 30},
        "storage": {
            "output_dir": str(base_dir / "outputs"),
            "outputs_dir": str(base_dir / "outputs"),
            "cache_dir": str(base_dir / "cache"),
        },
        "music": {"engine": "library"},
        "character": {"name": "QA Bot", "voice_type": "gtts"},
    }


class TestPodcastCreatorControllerValidation:
    """Test input validation logic."""

    def test_validate_inputs_no_script_file(self, tmp_path):
        """Test validation fails when no script file is set."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        
        is_valid, error_msg = controller.validate_inputs()
        
        assert is_valid is False
        assert "script file" in error_msg.lower()

    def test_validate_inputs_script_file_not_exists(self, tmp_path):
        """Test validation fails when script file doesn't exist."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        controller.script_file = str(tmp_path / "nonexistent.txt")
        
        is_valid, error_msg = controller.validate_inputs()
        
        assert is_valid is False
        assert "not found" in error_msg.lower()

    def test_validate_inputs_script_file_is_directory(self, tmp_path):
        """Test validation fails when script path is a directory."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_dir = tmp_path / "script_dir"
        script_dir.mkdir()
        controller.script_file = str(script_dir)
        
        is_valid, error_msg = controller.validate_inputs()
        
        assert is_valid is False
        assert "not a file" in error_msg.lower()

    def test_validate_inputs_valid(self, tmp_path):
        """Test validation succeeds with valid script file."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test script", encoding="utf-8")
        controller.script_file = str(script_path)
        
        is_valid, error_msg = controller.validate_inputs()
        
        assert is_valid is True
        assert error_msg is None


class TestPodcastCreatorControllerQualityMapping:
    """Test quality string mapping logic."""

    def test_map_quality_string_fastest(self, tmp_path):
        """Test mapping 'Fastest (Testing)' to 'fastest'."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        
        result = controller.map_quality_string("Fastest (Testing)")
        
        assert result == "fastest"

    def test_map_quality_string_legacy_high(self, tmp_path):
        """Test mapping legacy 'High (1080p)' format."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        
        result = controller.map_quality_string("High (1080p)")
        
        assert result == "high"

    def test_map_quality_string_legacy_medium(self, tmp_path):
        """Test mapping legacy 'Medium (720p)' format."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        
        result = controller.map_quality_string("Medium (720p)")
        
        assert result == "medium"

    def test_map_quality_string_legacy_fast(self, tmp_path):
        """Test mapping legacy 'Fast (720p)' format."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        
        result = controller.map_quality_string("Fast (720p)")
        
        assert result == "fast"

    def test_map_quality_string_unknown_defaults_to_fastest(self, tmp_path):
        """Test unknown quality string defaults to 'fastest'."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        
        result = controller.map_quality_string("Unknown Quality")
        
        assert result == "fastest"


class TestPodcastCreatorControllerPrepareParams:
    """Test parameter preparation logic."""

    def test_prepare_params_with_all_options(self, tmp_path):
        """Test preparing parameters with all options set."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        controller.script_file = str(script_path)
        controller.music_file = str(tmp_path / "music.mp3")
        controller.music_description = "calm ambient"
        controller.output_name = "my_podcast"
        controller.video_quality = "High (1080p)"
        controller.visualize = True
        controller.background = True
        controller.avatar = True
        
        params = controller.prepare_podcast_creation_params()
        
        assert params["script_path"] == script_path
        assert params["music_file"] == tmp_path / "music.mp3"
        assert params["music_description"] == "calm ambient"
        assert params["output_name"] == "my_podcast"
        assert params["quality"] == "high"
        assert params["use_visualization"] is True
        assert params["use_background"] is True
        assert params["use_avatar"] is True

    def test_prepare_params_output_name_defaults_to_script_stem(self, tmp_path):
        """Test output name defaults to script stem when not provided."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "my_script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        controller.script_file = str(script_path)
        controller.output_name = None
        
        params = controller.prepare_podcast_creation_params()
        
        assert params["output_name"] == "my_script"


class TestPodcastCreatorControllerCreatePodcast:
    """Test podcast creation logic."""

    def test_create_podcast_validates_inputs(self, tmp_path):
        """Test create_podcast validates inputs first."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        controller.script_file = None  # Invalid
        
        with pytest.raises(ValueError, match="script file"):
            controller.create_podcast()

    def test_create_podcast_success_path(self, tmp_path):
        """Test successful podcast creation path."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("# Title\nHello world", encoding="utf-8")
        controller.script_file = str(script_path)
        
        log_messages = []
        progress_updates = []
        
        def log_callback(msg, color="black"):
            log_messages.append((msg, color))
        
        def progress_callback(msg, status="info"):
            progress_updates.append((msg, status))
        
        with (
            patch("src.gui.desktop_gui_controller.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui_controller.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui_controller.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui_controller.VideoComposer") as mock_composer,
        ):
            mock_parser.return_value.parse.return_value = {"text": "Hello world", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            final_video = tmp_path / "outputs" / "script.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer.return_value.compose.return_value = final_video
            
            result = controller.create_podcast(
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            
            assert result == final_video
            assert len(log_messages) > 0
            assert any("Starting podcast creation" in msg for msg, _ in log_messages)

    def test_create_podcast_with_music_file(self, tmp_path):
        """Test podcast creation with music file."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        music_path = tmp_path / "music.mp3"
        music_path.write_bytes(b"music")
        
        controller.script_file = str(script_path)
        controller.music_file = str(music_path)
        
        with (
            patch("src.gui.desktop_gui_controller.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui_controller.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui_controller.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui_controller.VideoComposer") as mock_composer,
        ):
            mock_parser.return_value.parse.return_value = {"text": "Test", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            final_video = tmp_path / "outputs" / "script.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer.return_value.compose.return_value = final_video
            
            result = controller.create_podcast()
            
            # Should use music file
            assert result == final_video
            mock_mixer.return_value.mix.assert_called_once()

    def test_create_podcast_with_music_description(self, tmp_path):
        """Test podcast creation with music description."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        controller.script_file = str(script_path)
        controller.music_description = "calm ambient"
        
        with (
            patch("src.gui.desktop_gui_controller.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui_controller.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui_controller.MusicGenerator") as mock_music,
            patch("src.gui.desktop_gui_controller.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui_controller.VideoComposer") as mock_composer,
        ):
            mock_parser.return_value.parse.return_value = {"text": "Test", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            generated_music = tmp_path / "generated_music.mp3"
            generated_music.write_bytes(b"music")
            mock_music.return_value.generate.return_value = generated_music
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            final_video = tmp_path / "outputs" / "script.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer.return_value.compose.return_value = final_video
            
            result = controller.create_podcast()
            
            # Should generate music
            assert result == final_video
            mock_music.return_value.generate.assert_called_once_with("calm ambient")

    def test_create_podcast_with_avatar(self, tmp_path):
        """Test podcast creation with avatar enabled."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        controller.script_file = str(script_path)
        controller.avatar = True
        
        avatar_video = tmp_path / "avatar.mp4"
        avatar_video.write_bytes(b"video")
        
        with (
            patch("src.gui.desktop_gui_controller.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui_controller.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui_controller.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui_controller.VideoComposer") as mock_composer,
            patch("src.core.avatar_generator.AvatarGenerator") as mock_avatar,
        ):
            mock_parser.return_value.parse.return_value = {"text": "Test", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            mock_avatar.return_value.generate.return_value = avatar_video
            final_video = tmp_path / "outputs" / "script.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer.return_value.compose.return_value = final_video
            
            result = controller.create_podcast()
            
            # Should generate avatar
            assert result == final_video
            mock_avatar.return_value.generate.assert_called_once()

    def test_create_podcast_avatar_failure_continues(self, tmp_path):
        """Test podcast creation continues when avatar generation fails."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        controller.script_file = str(script_path)
        controller.avatar = True
        
        with (
            patch("src.gui.desktop_gui_controller.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui_controller.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui_controller.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui_controller.VideoComposer") as mock_composer,
            patch("src.core.avatar_generator.AvatarGenerator") as mock_avatar,
        ):
            mock_parser.return_value.parse.return_value = {"text": "Test", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            # Avatar generation fails
            mock_avatar.return_value.generate.side_effect = Exception("Avatar error")
            final_video = tmp_path / "outputs" / "script.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer.return_value.compose.return_value = final_video
            
            result = controller.create_podcast()
            
            # Should continue without avatar
            assert result == final_video
            mock_composer.return_value.compose.assert_called_once()

    def test_create_podcast_handles_exceptions(self, tmp_path):
        """Test podcast creation handles exceptions properly."""
        config = make_controller_config(tmp_path)
        controller = PodcastCreatorController(config)
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        controller.script_file = str(script_path)
        
        with (
            patch("src.gui.desktop_gui_controller.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui_controller.TTSEngine") as mock_tts,
        ):
            mock_parser.return_value.parse.return_value = {"text": "Test", "music_cues": []}
            mock_tts.return_value.generate.side_effect = Exception("TTS error")
            
            with pytest.raises(RuntimeError, match="Failed to create podcast"):
                controller.create_podcast()

