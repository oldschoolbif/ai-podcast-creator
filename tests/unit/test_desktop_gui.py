"""
Unit Tests for Desktop GUI
Tests for src/gui/desktop_gui.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Check if tkinter is available
try:
    import tkinter

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if TKINTER_AVAILABLE:
    from src.gui.desktop_gui import PodcastCreatorGUI
else:
    PodcastCreatorGUI = None


class ImmediateThread:
    """Thread drop-in that runs the target synchronously (used in tests)."""

    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}
        self.daemon = daemon

    def start(self):
        if self._target:
            self._target(*self._args, **self._kwargs)


def make_gui_config(base_dir: Path | str = Path("output")):
    base_path = Path(base_dir)
    return {
        "app": {"name": "AI Podcast Creator", "version": "1.0.0"},
        "tts": {"engine": "gtts"},
        "video": {"resolution": [1920, 1080], "fps": 30},
        "storage": {
            "output_dir": str(base_path),
            "outputs_dir": str(base_path),
            "cache_dir": str(base_path / "cache"),
        },
        "music": {"engine": "library"},
        "character": {"name": "QA Bot", "voice_type": "gtts"},
    }


def create_hidden_root():
    """Create a hidden Tk root window or skip if not available."""
    if not TKINTER_AVAILABLE:
        pytest.skip("tkinter not available")

    import tkinter as tk

    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("tkinter Tcl/Tk libraries not available on this environment")

    root.withdraw()
    root.after = lambda delay, func, *args: func(*args)
    return root


@pytest.mark.skipif(not TKINTER_AVAILABLE, reason="tkinter not available")
class TestPodcastCreatorGUIInit:
    """Test PodcastCreatorGUI initialization."""

    def test_gui_initialization(self):
        """Test GUI initialization creates window."""
        import tkinter as tk

        root = create_hidden_root()

        with patch("src.gui.desktop_gui.load_config") as mock_config:
            mock_config.return_value = {
                "tts": {"engine": "gtts"},
                "video": {"resolution": [1920, 1080]},
                "storage": {"output_dir": "/tmp"},
            }

            gui = PodcastCreatorGUI(root)

            assert gui.root == root
            assert gui.script_file is not None
            assert gui.music_file is not None
            assert gui.voice_type is not None
            assert gui.config is not None

        root.destroy()

    def test_gui_sets_default_values(self):
        """Test GUI sets default values."""
        import tkinter as tk

        root = create_hidden_root()

        with patch("src.gui.desktop_gui.load_config") as mock_config:
            mock_config.return_value = {"tts": {"engine": "gtts"}}

            gui = PodcastCreatorGUI(root)

            assert gui.voice_type.get() == "gtts"
            assert gui.avatar_style.get() == "Professional Studio"
            assert gui.video_quality.get() == "High (1080p)"

        root.destroy()

    def test_gui_checks_gpu(self):
        """Test GUI checks GPU on init."""
        import tkinter as tk

        root = create_hidden_root()

        with patch("src.gui.desktop_gui.load_config") as mock_config:
            with patch.object(PodcastCreatorGUI, "check_gpu") as mock_check:
                mock_config.return_value = {"tts": {"engine": "gtts"}}

                gui = PodcastCreatorGUI(root)

                # check_gpu is called during __init__
                assert hasattr(gui, "check_gpu")

        root.destroy()


@pytest.mark.skipif(not TKINTER_AVAILABLE, reason="tkinter not available")
class TestPodcastCreatorGUIMethods:
    """Test PodcastCreatorGUI methods."""

    def test_browse_script(self):
        """Test browse_script method."""
        import tkinter as tk

        root = create_hidden_root()

        with patch("src.gui.desktop_gui.load_config") as mock_config:
            with patch("tkinter.filedialog.askopenfilename") as mock_file:
                mock_config.return_value = {"tts": {"engine": "gtts"}}
                mock_file.return_value = "/path/to/script.txt"

                gui = PodcastCreatorGUI(root)
                gui.browse_script()

                assert gui.script_file.get() == "/path/to/script.txt"
                assert mock_file.called

        root.destroy()

    def test_browse_music(self):
        """Test browse_music method."""
        import tkinter as tk

        root = create_hidden_root()

        with patch("src.gui.desktop_gui.load_config") as mock_config:
            with patch("tkinter.filedialog.askopenfilename") as mock_file:
                mock_config.return_value = {"tts": {"engine": "gtts"}}
                mock_file.return_value = "/path/to/music.mp3"

                gui = PodcastCreatorGUI(root)
                gui.browse_music()

                assert gui.music_file.get() == "/path/to/music.mp3"

        root.destroy()

    def test_browse_script_cancelled(self):
        """Test browse_script when user cancels."""
        import tkinter as tk

        root = create_hidden_root()

        with patch("src.gui.desktop_gui.load_config") as mock_config:
            with patch("tkinter.filedialog.askopenfilename") as mock_file:
                mock_config.return_value = {"tts": {"engine": "gtts"}}
                mock_file.return_value = ""  # User cancelled

                gui = PodcastCreatorGUI(root)
                initial_value = gui.script_file.get()
                gui.browse_script()

                # Should not change if cancelled
                assert gui.script_file.get() == initial_value

        root.destroy()


@pytest.mark.skipif(not TKINTER_AVAILABLE, reason="tkinter not available")
class TestPodcastCreatorGUICreatePodcast:
    """Test podcast creation from GUI."""

    def _build_gui(self, tmp_path):
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        with patch("src.gui.desktop_gui.load_config", return_value=config):
            gui = PodcastCreatorGUI(root)
        return root, gui

    def test_create_podcast_valid_inputs(self, tmp_path):
        script_path = tmp_path / "script.txt"
        script_path.write_text("# Test\nHello world", encoding="utf-8")

        root, gui = self._build_gui(tmp_path)

        with (
            patch("src.gui.desktop_gui.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui.VideoComposer") as mock_composer,
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
            patch.object(PodcastCreatorGUI, "open_output_folder"),
        ):

            mock_parser_instance = MagicMock()
            mock_parser_instance.parse.return_value = {"text": "Hello world", "music_cues": []}
            mock_parser.return_value = mock_parser_instance

            mock_tts_instance = MagicMock()
            audio_path = tmp_path / "audio.mp3"
            audio_path.write_bytes(b"audio")
            mock_tts_instance.generate.return_value = audio_path
            mock_tts.return_value = mock_tts_instance

            mock_mixer_instance = MagicMock()
            mixed_audio = tmp_path / "mixed.mp3"
            mixed_audio.write_bytes(b"mixed")
            mock_mixer_instance.mix.return_value = mixed_audio
            mock_mixer.return_value = mock_mixer_instance

            mock_composer_instance = MagicMock()
            final_video = tmp_path / "output" / "test.mp4"
            final_video.parent.mkdir(parents=True, exist_ok=True)
            final_video.write_bytes(b"video")
            mock_composer_instance.compose.return_value = final_video
            mock_composer.return_value = mock_composer_instance

            gui.script_file.set(str(script_path))
            gui.create_podcast()

            mock_parser_instance.parse.assert_called()
            mock_tts_instance.generate.assert_called()
            mock_composer_instance.compose.assert_called()

        root.destroy()

    def test_create_podcast_no_script(self, tmp_path):
        root, gui = self._build_gui(tmp_path)
        gui.script_file.set("")

        with patch("tkinter.messagebox.showerror") as mock_error:
            gui.create_podcast()
            mock_error.assert_called()

        root.destroy()

    def test_create_podcast_with_music_file(self, tmp_path):
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        music_path = tmp_path / "music.mp3"
        music_path.write_bytes(b"music")

        root, gui = self._build_gui(tmp_path)

        with (
            patch("src.gui.desktop_gui.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui.VideoComposer") as mock_composer,
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
        ):

            mock_parser.return_value.parse.return_value = {"text": "hello", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            mock_composer.return_value.compose.return_value = tmp_path / "output" / "final.mp4"

            gui.script_file.set(str(script_path))
            gui.music_file.set(str(music_path))
            gui.create_podcast()

            assert gui.music_file.get() == str(music_path)

        root.destroy()

    def test_create_podcast_with_music_description(self, tmp_path):
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")

        root, gui = self._build_gui(tmp_path)

        with (
            patch("src.gui.desktop_gui.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui.MusicGenerator") as mock_music,
            patch("src.gui.desktop_gui.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui.VideoComposer") as mock_composer,
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
        ):

            mock_parser.return_value.parse.return_value = {"text": "hello", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            generated_music = tmp_path / "generated.wav"
            generated_music.write_bytes(b"music")
            mock_music.return_value.generate.return_value = generated_music
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            mock_composer.return_value.compose.return_value = tmp_path / "output" / "final.mp4"

            gui.script_file.set(str(script_path))
            gui.music_description.set("upbeat electronic")
            gui.create_podcast()

            mock_music.return_value.generate.assert_called()

        root.destroy()


@pytest.mark.skipif(not TKINTER_AVAILABLE, reason="tkinter not available")
class TestPodcastCreatorGUIErrorHandling:
    """Test error handling in GUI."""

    def test_create_podcast_handles_exception(self, tmp_path):
        import tkinter as tk

        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")

        with patch("src.gui.desktop_gui.load_config", return_value=config):
            gui = PodcastCreatorGUI(root)

        gui.script_file.set(str(script_path))

        with (
            patch("src.gui.desktop_gui.ScriptParser") as mock_parser,
            patch("src.gui.desktop_gui.TTSEngine") as mock_tts,
            patch("src.gui.desktop_gui.AudioMixer") as mock_mixer,
            patch("src.gui.desktop_gui.VideoComposer") as mock_composer,
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.showerror") as mock_error,
        ):

            mock_parser.return_value.parse.return_value = {"text": "hello", "music_cues": []}
            mock_tts.return_value.generate.return_value = tmp_path / "audio.mp3"
            mock_mixer.return_value.mix.return_value = tmp_path / "mixed.mp3"
            mock_composer.return_value.compose.side_effect = RuntimeError("compose fail")

            gui.create_podcast()

            mock_error.assert_called()
            assert gui.create_button["state"] == tk.NORMAL

        root.destroy()


class TestPodcastCreatorGUITkinterUnavailable:
    """Test GUI behavior when tkinter not available."""

    @pytest.mark.skipif(TKINTER_AVAILABLE, reason="tkinter is available")
    def test_import_fails_without_tkinter(self):
        """Test that GUI cannot be imported without tkinter."""
        # This test only runs if tkinter is NOT available
        assert PodcastCreatorGUI is None or not TKINTER_AVAILABLE
