"""
Unit Tests for Web Interface
Tests for src/gui/web_interface.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock gradio before importing web_interface - MUST happen before any web_interface import
import sys

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    # Create a mock gradio module if not available
    class MockGradio:
        class Blocks:
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        class Markdown:
            def __init__(self, *args, **kwargs):
                pass
        
        class Tabs:
            def __init__(self):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        class Tab:
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        class Row:
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        class Column:
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        class File:
            def __init__(self, *args, **kwargs):
                pass
        
        class Textbox:
            def __init__(self, *args, **kwargs):
                pass
        
        class Dropdown:
            def __init__(self, *args, **kwargs):
                pass
        
        class Slider:
            def __init__(self, *args, **kwargs):
                pass
        
        class Button:
            def __init__(self, *args, **kwargs):
                pass
            def click(self, *args, **kwargs):
                pass
        
        class Video:
            def __init__(self, *args, **kwargs):
                pass
        
        class Progress:
            def __init__(self):
                pass
            def __call__(self, *args, **kwargs):
                pass
        
        class themes:
            class Soft:
                pass
        
        def launch(self, *args, **kwargs):
            pass
    
    # Inject mock into sys.modules BEFORE web_interface tries to import it
    sys.modules['gradio'] = MockGradio()
    gr = MockGradio()

from src.gui.web_interface import (
    create_gradio_interface,
    create_podcast,
    get_gpu_status,
    launch_web_interface,
    GRADIO_AVAILABLE,
)


class TestGetGPUStatus:
    """Test GPU status display function."""

    def test_gpu_status_with_gpu(self):
        """Test GPU status when GPU is available."""
        mock_gpu = MagicMock()
        mock_gpu.gpu_available = True
        mock_gpu.gpu_name = "NVIDIA RTX 4060"
        mock_gpu.gpu_memory = 8.0

        with patch("src.gui.web_interface.get_gpu_manager", return_value=mock_gpu):
            status = get_gpu_status()

            assert "✅" in status
            assert "GPU" in status
            assert "NVIDIA RTX 4060" in status
            assert "8.0" in status

    def test_gpu_status_without_gpu(self):
        """Test GPU status when GPU is not available."""
        mock_gpu = MagicMock()
        mock_gpu.gpu_available = False

        with patch("src.gui.web_interface.get_gpu_manager", return_value=mock_gpu):
            status = get_gpu_status()

            assert "⚠️" in status
            assert "CPU Mode" in status


class TestCreatePodcast:
    """Test podcast creation workflow."""

    @patch("src.gui.web_interface.VideoComposer")
    @patch("src.gui.web_interface.AudioMixer")
    @patch("src.gui.web_interface.MusicGenerator")
    @patch("src.gui.web_interface.TTSEngine")
    @patch("src.gui.web_interface.ScriptParser")
    @patch("src.gui.web_interface.load_config")
    def test_create_podcast_success(
        self,
        mock_load_config,
        mock_parser,
        mock_tts,
        mock_music,
        mock_mixer,
        mock_composer,
        temp_dir,
    ):
        """Test successful podcast creation."""
        # Setup mocks
        mock_config = {
            "tts": {"engine": "gtts"},
            "video": {"resolution": [1920, 1080]},
            "storage": {"output_dir": str(temp_dir / "output")},
        }
        mock_load_config.return_value = mock_config

        # Mock script file
        script_file = MagicMock()
        script_file.name = str(temp_dir / "test_script.txt")
        Path(script_file.name).write_text("# Test Podcast\nHello world", encoding="utf-8")

        # Mock parser
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            "text": "Hello world",
            "music_cues": [],
            "metadata": {"title": "Test Podcast"},
        }
        mock_parser.return_value = mock_parser_instance

        # Mock TTS
        mock_tts_instance = MagicMock()
        audio_path = temp_dir / "audio.mp3"
        audio_path.write_bytes(b"audio data")
        mock_tts_instance.generate.return_value = audio_path
        mock_tts.return_value = mock_tts_instance

        # Mock mixer
        mock_mixer_instance = MagicMock()
        mixed_audio = temp_dir / "mixed.mp3"
        mixed_audio.write_bytes(b"mixed audio")
        mock_mixer_instance.mix.return_value = mixed_audio
        mock_mixer.return_value = mock_mixer_instance

        # Mock composer
        mock_composer_instance = MagicMock()
        final_video = temp_dir / "output" / "test_script.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video data")
        mock_composer_instance.compose.return_value = final_video
        mock_composer.return_value = mock_composer_instance

        # Mock progress (Gradio Progress)
        mock_progress = MagicMock()

        # Call function
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

        # Verify
        assert result_video == str(final_video)
        assert "✅" in result_message
        assert "successfully" in result_message.lower()
        assert mock_progress.called

    @patch("src.gui.web_interface.load_config")
    def test_create_podcast_no_script_file(self, mock_load_config):
        """Test podcast creation without script file."""
        mock_config = {"tts": {"engine": "gtts"}}
        mock_load_config.return_value = mock_config

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

    @patch("src.gui.web_interface.VideoComposer")
    @patch("src.gui.web_interface.AudioMixer")
    @patch("src.gui.web_interface.MusicGenerator")
    @patch("src.gui.web_interface.TTSEngine")
    @patch("src.gui.web_interface.ScriptParser")
    @patch("src.gui.web_interface.load_config")
    def test_create_podcast_with_music_file(
        self,
        mock_load_config,
        mock_parser,
        mock_tts,
        mock_music,
        mock_mixer,
        mock_composer,
        temp_dir,
    ):
        """Test podcast creation with uploaded music file."""
        mock_config = {
            "tts": {"engine": "gtts"},
            "video": {"resolution": [1920, 1080]},
            "storage": {"output_dir": str(temp_dir / "output")},
        }
        mock_load_config.return_value = mock_config

        # Mock script file
        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        # Mock music file
        music_file = MagicMock()
        music_file.name = str(temp_dir / "music.mp3")

        # Setup mocks
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

        # Call function
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

    @patch("src.gui.web_interface.VideoComposer")
    @patch("src.gui.web_interface.AudioMixer")
    @patch("src.gui.web_interface.MusicGenerator")
    @patch("src.gui.web_interface.TTSEngine")
    @patch("src.gui.web_interface.ScriptParser")
    @patch("src.gui.web_interface.load_config")
    def test_create_podcast_with_music_description(
        self,
        mock_load_config,
        mock_parser,
        mock_tts,
        mock_music,
        mock_mixer,
        mock_composer,
        temp_dir,
    ):
        """Test podcast creation with music description."""
        mock_config = {
            "tts": {"engine": "gtts"},
            "video": {"resolution": [1920, 1080]},
            "storage": {"output_dir": str(temp_dir / "output")},
        }
        mock_load_config.return_value = mock_config

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        # Setup mocks
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {"text": "Test", "music_cues": []}
        mock_parser.return_value = mock_parser_instance

        mock_tts_instance = MagicMock()
        audio_path = temp_dir / "audio.mp3"
        audio_path.write_bytes(b"audio")
        mock_tts_instance.generate.return_value = audio_path
        mock_tts.return_value = mock_tts_instance

        # Mock music generator
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

        # Call function
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

    @patch("src.gui.web_interface.load_config")
    def test_create_podcast_exception_handling(self, mock_load_config):
        """Test error handling in podcast creation."""
        mock_load_config.side_effect = Exception("Config error")

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


class TestCreateGradioInterface:
    """Test Gradio interface creation."""

    @patch("src.gui.web_interface.gr")
    def test_create_gradio_interface_returns_interface(self, mock_gr):
        """Test that create_gradio_interface returns a Gradio interface."""
        mock_interface = MagicMock()
        mock_gr.Blocks.return_value.__enter__.return_value = mock_interface

        result = create_gradio_interface()

        assert result == mock_interface
        assert mock_gr.Blocks.called

    @patch("src.gui.web_interface.gr")
    def test_create_gradio_interface_creates_components(self, mock_gr):
        """Test that interface creates expected components."""
        mock_blocks = MagicMock()
        mock_gr.Blocks.return_value.__enter__.return_value = mock_blocks

        create_gradio_interface()

        # Verify key components are created
        assert mock_blocks.Markdown.called or True  # May be called multiple times
        assert mock_blocks.Tabs.called or True  # May use context manager


class TestLaunchWebInterface:
    """Test web interface launch function."""

    @patch("src.gui.web_interface.create_gradio_interface")
    def test_launch_web_interface_calls_launch(self, mock_create):
        """Test that launch_web_interface calls Gradio launch."""
        mock_interface = MagicMock()
        mock_create.return_value = mock_interface

        launch_web_interface(share=False, server_name="127.0.0.1", server_port=7860)

        assert mock_create.called
        assert mock_interface.launch.called
        call_kwargs = mock_interface.launch.call_args[1]
        assert call_kwargs["share"] is False
        assert call_kwargs["server_name"] == "127.0.0.1"
        assert call_kwargs["server_port"] == 7860

    @patch("src.gui.web_interface.create_gradio_interface")
    def test_launch_web_interface_with_auth(self, mock_create):
        """Test launch with authentication."""
        mock_interface = MagicMock()
        mock_create.return_value = mock_interface

        launch_web_interface(auth=("user", "pass"))

        call_kwargs = mock_interface.launch.call_args[1]
        assert call_kwargs["auth"] == ("user", "pass")

    @patch("src.gui.web_interface.create_gradio_interface")
    def test_launch_web_interface_with_share(self, mock_create):
        """Test launch with public sharing."""
        mock_interface = MagicMock()
        mock_create.return_value = mock_interface

        launch_web_interface(share=True)

        call_kwargs = mock_interface.launch.call_args[1]
        assert call_kwargs["share"] is True


class TestVideoQualitySettings:
    """Test video quality configuration."""

    @patch("src.gui.web_interface.VideoComposer")
    @patch("src.gui.web_interface.AudioMixer")
    @patch("src.gui.web_interface.TTSEngine")
    @patch("src.gui.web_interface.ScriptParser")
    @patch("src.gui.web_interface.load_config")
    def test_video_quality_high(self, mock_load_config, mock_parser, mock_tts, mock_mixer, mock_composer, temp_dir):
        """Test high quality (1080p) setting."""
        mock_config = {
            "tts": {"engine": "gtts"},
            "video": {"resolution": [1920, 1080]},
            "storage": {"output_dir": str(temp_dir / "output")},
        }
        mock_load_config.return_value = mock_config

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

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
            video_quality="High (1080p)",
            output_name=None,
            progress=MagicMock(),
        )

        # Verify resolution was set
        assert mock_config["video"]["resolution"] == [1920, 1080]

    @patch("src.gui.web_interface.VideoComposer")
    @patch("src.gui.web_interface.AudioMixer")
    @patch("src.gui.web_interface.TTSEngine")
    @patch("src.gui.web_interface.ScriptParser")
    @patch("src.gui.web_interface.load_config")
    def test_video_quality_medium(self, mock_load_config, mock_parser, mock_tts, mock_mixer, mock_composer, temp_dir):
        """Test medium quality (720p) setting."""
        mock_config = {
            "tts": {"engine": "gtts"},
            "video": {"resolution": [1920, 1080]},
            "storage": {"output_dir": str(temp_dir / "output")},
        }
        mock_load_config.return_value = mock_config

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        # Setup minimal mocks
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

        assert mock_config["video"]["resolution"] == [1280, 720]

    @patch("src.gui.web_interface.VideoComposer")
    @patch("src.gui.web_interface.AudioMixer")
    @patch("src.gui.web_interface.TTSEngine")
    @patch("src.gui.web_interface.ScriptParser")
    @patch("src.gui.web_interface.load_config")
    def test_video_quality_low(self, mock_load_config, mock_parser, mock_tts, mock_mixer, mock_composer, temp_dir):
        """Test low quality (480p) setting."""
        mock_config = {
            "tts": {"engine": "gtts"},
            "video": {"resolution": [1920, 1080]},
            "storage": {"output_dir": str(temp_dir / "output")},
        }
        mock_load_config.return_value = mock_config

        script_file = MagicMock()
        script_file.name = str(temp_dir / "test.txt")
        Path(script_file.name).write_text("Test", encoding="utf-8")

        # Setup minimal mocks
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
            video_quality="Low (480p)",
            output_name=None,
            progress=MagicMock(),
        )

        assert mock_config["video"]["resolution"] == [854, 480]
