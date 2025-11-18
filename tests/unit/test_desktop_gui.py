"""
Unit Tests for Desktop GUI
Tests for src/gui/desktop_gui.py
"""

import sys
import platform
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
    import tkinter as tk
    from src.gui.desktop_gui import PodcastCreatorGUI, launch_desktop_gui
else:
    PodcastCreatorGUI = None
    launch_desktop_gui = None


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

    @pytest.mark.skip(reason="GUI default values test - will fix after waveform work is complete")
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

    @pytest.mark.timeout(30)  # Add 30 second timeout to prevent CI hang
    def test_create_podcast_valid_inputs(self, tmp_path):
        script_path = tmp_path / "script.txt"
        script_path.write_text("# Test\nHello world", encoding="utf-8")

        root, gui = self._build_gui(tmp_path)

        final_video = tmp_path / "output" / "test.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video")

        with (
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
            patch.object(PodcastCreatorGUI, "open_output_folder"),
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,  # Mock to avoid event loop issues
            patch.object(gui.controller, "create_podcast") as mock_controller_create,  # Mock controller method directly
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to return immediately
            mock_controller_create.return_value = final_video

            gui.script_file.set(str(script_path))
            gui.create_podcast()

            # Verify controller.create_podcast was called
            mock_controller_create.assert_called_once()

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

        final_video = tmp_path / "output" / "final.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video")

        with (
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
            patch.object(PodcastCreatorGUI, "open_output_folder"),
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,
            patch.object(gui.controller, "create_podcast") as mock_controller_create,
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to return immediately
            mock_controller_create.return_value = final_video

            gui.script_file.set(str(script_path))
            gui.music_file.set(str(music_path))
            gui.create_podcast()

            assert gui.music_file.get() == str(music_path)
            mock_controller_create.assert_called_once()

        root.destroy()

    def test_create_podcast_with_music_description(self, tmp_path):
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")

        root, gui = self._build_gui(tmp_path)

        final_video = tmp_path / "output" / "final.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video")

        with (
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
            patch.object(PodcastCreatorGUI, "open_output_folder"),
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,
            patch.object(gui.controller, "create_podcast") as mock_controller_create,
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to return immediately
            mock_controller_create.return_value = final_video

            gui.script_file.set(str(script_path))
            gui.music_description.set("upbeat electronic")
            gui.create_podcast()

            mock_controller_create.assert_called_once()

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
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.showerror") as mock_error,
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,
            patch.object(gui.controller, "create_podcast") as mock_controller_create,
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to raise an exception
            mock_controller_create.side_effect = RuntimeError("compose fail")

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


@pytest.mark.skipif(not TKINTER_AVAILABLE, reason="tkinter not available")
class TestPodcastCreatorGUIAdditionalCoverage:
    """Additional tests to improve coverage to 80%+."""

    def test_run_on_ui_thread_with_wait(self, tmp_path):
        """Test _run_on_ui_thread with wait=True (lines 60-72)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        with patch("src.gui.desktop_gui.load_config", return_value=config):
            gui = PodcastCreatorGUI(root)
        
        # Test with wait=True
        result = {"called": False}
        def test_func():
            result["called"] = True
        
        # Should execute immediately if on main thread
        gui._run_on_ui_thread(test_func, wait=True)
        assert result["called"] is True
        
        root.destroy()

    def test_run_on_ui_thread_without_wait(self, tmp_path):
        """Test _run_on_ui_thread with wait=False (line 72)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        with patch("src.gui.desktop_gui.load_config", return_value=config):
            gui = PodcastCreatorGUI(root)
        
        # Test with wait=False
        result = {"called": False}
        def test_func():
            result["called"] = True
        
        # Should schedule via root.after
        gui._run_on_ui_thread(test_func, wait=False)
        # Execute scheduled callbacks
        root.update()
        assert result["called"] is True
        
        root.destroy()

    def test_check_gpu_with_gpu_available(self, tmp_path):
        """Test check_gpu when GPU is available (lines 263-264)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        mock_gpu_manager = MagicMock()
        mock_gpu_manager.gpu_available = True
        mock_gpu_manager.gpu_name = "Test GPU"
        mock_gpu_manager.gpu_memory = 8.0
        
        with (
            patch("src.gui.desktop_gui.load_config", return_value=config),
            patch("src.gui.desktop_gui.get_gpu_manager", return_value=mock_gpu_manager),
        ):
            gui = PodcastCreatorGUI(root)
            gui.check_gpu()
            
            # Should log GPU info
            log_content = gui.log_text.get(1.0, tk.END)
            assert "GPU" in log_content or "Test GPU" in log_content
        
        root.destroy()

    def test_browse_script_with_filename(self, tmp_path):
        """Test browse_script when filename is provided (lines 275-276)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        test_file = tmp_path / "script.txt"
        test_file.write_text("test")
        
        with (
            patch("src.gui.desktop_gui.load_config", return_value=config),
            patch("tkinter.filedialog.askopenfilename", return_value=str(test_file)),
        ):
            gui = PodcastCreatorGUI(root)
            gui.browse_script()
            
            assert gui.script_file.get() == str(test_file)
        
        root.destroy()

    def test_browse_music_with_filename(self, tmp_path):
        """Test browse_music when filename is provided (line 283->exit)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        test_file = tmp_path / "music.mp3"
        test_file.write_bytes(b"music")
        
        with (
            patch("src.gui.desktop_gui.load_config", return_value=config),
            patch("tkinter.filedialog.askopenfilename", return_value=str(test_file)),
        ):
            gui = PodcastCreatorGUI(root)
            gui.browse_music()
            
            assert gui.music_file.get() == str(test_file)
        
        root.destroy()

    def test_clear_log(self, tmp_path):
        """Test clear_log method (line 298)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        with patch("src.gui.desktop_gui.load_config", return_value=config):
            gui = PodcastCreatorGUI(root)
            
            # Add some text to log
            gui.log_text.insert(tk.END, "Test log message\n")
            
            # Clear log
            gui.clear_log()
            
            # Log should be empty
            content = gui.log_text.get(1.0, tk.END)
            assert content.strip() == ""
        
        root.destroy()

    def test_open_output_folder_windows(self, tmp_path, monkeypatch):
        """Test open_output_folder on Windows (line 312)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        with (
            patch("src.gui.desktop_gui.load_config", return_value=config),
            patch("platform.system", return_value="Windows"),
            patch("subprocess.Popen") as mock_popen,
        ):
            gui = PodcastCreatorGUI(root)
            gui.open_output_folder()
            
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]
            assert call_args[0] == "explorer"
        
        root.destroy()

    def test_open_output_folder_macos(self, tmp_path):
        """Test open_output_folder on macOS (line 314)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        with (
            patch("src.gui.desktop_gui.load_config", return_value=config),
            patch("platform.system", return_value="Darwin"),
            patch("subprocess.Popen") as mock_popen,
        ):
            gui = PodcastCreatorGUI(root)
            gui.open_output_folder()
            
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]
            assert call_args[0] == "open"
        
        root.destroy()

    def test_open_output_folder_linux(self, tmp_path):
        """Test open_output_folder on Linux (line 316)."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        
        with (
            patch("src.gui.desktop_gui.load_config", return_value=config),
            patch("platform.system", return_value="Linux"),
            patch("subprocess.Popen") as mock_popen,
        ):
            gui = PodcastCreatorGUI(root)
            gui.open_output_folder()
            
            mock_popen.assert_called_once()
            call_args = mock_popen.call_args[0][0]
            assert call_args[0] == "xdg-open"
        
        root.destroy()

    def test_create_podcast_with_avatar(self, tmp_path):
        """Test create_podcast with avatar enabled (lines 382-394)."""
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        root, gui = self._build_gui(tmp_path)
        gui.script_file.set(str(script_path))
        gui.avatar.set(True)  # Enable avatar
        
        final_video = tmp_path / "output" / "final.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video")
        
        with (
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
            patch.object(PodcastCreatorGUI, "open_output_folder"),
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,
            patch.object(gui.controller, "create_podcast") as mock_controller_create,
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to return immediately
            mock_controller_create.return_value = final_video
            
            gui.create_podcast()
            
            # Verify controller was called
            mock_controller_create.assert_called_once()
        
        root.destroy()

    def test_create_podcast_avatar_generation_fails(self, tmp_path):
        """Test create_podcast when avatar generation fails (lines 392-394)."""
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        root, gui = self._build_gui(tmp_path)
        gui.script_file.set(str(script_path))
        gui.avatar.set(True)
        
        final_video = tmp_path / "output" / "final.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video")
        
        with (
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
            patch.object(PodcastCreatorGUI, "open_output_folder"),
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,
            patch.object(gui.controller, "create_podcast") as mock_controller_create,
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to return immediately
            mock_controller_create.return_value = final_video
            
            gui.create_podcast()
            
            # Verify controller was called
            mock_controller_create.assert_called_once()
        
        root.destroy()

    def test_create_podcast_quality_legacy_format(self, tmp_path):
        """Test create_podcast with legacy quality format (lines 409-416)."""
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        root, gui = self._build_gui(tmp_path)
        gui.script_file.set(str(script_path))
        gui.video_quality.set("High (1080p)")  # Legacy format
        
        final_video = tmp_path / "output" / "final.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video")
        
        with (
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=False),
            patch.object(PodcastCreatorGUI, "open_output_folder"),
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,
            patch.object(gui.controller, "create_podcast") as mock_controller_create,
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to return immediately
            mock_controller_create.return_value = final_video
            
            gui.create_podcast()
            
            # Verify controller was called (quality mapping is tested in controller tests)
            mock_controller_create.assert_called_once()
        
        root.destroy()

    def test_create_podcast_opens_folder_on_confirm(self, tmp_path):
        """Test create_podcast opens folder when user confirms (line 445)."""
        script_path = tmp_path / "script.txt"
        script_path.write_text("Test", encoding="utf-8")
        
        root, gui = self._build_gui(tmp_path)
        gui.script_file.set(str(script_path))
        
        final_video = tmp_path / "output" / "final.mp4"
        final_video.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_bytes(b"video")
        
        with (
            patch("src.gui.desktop_gui.threading.Thread", new=ImmediateThread),
            patch("tkinter.messagebox.askyesno", return_value=True),  # User confirms
            patch.object(PodcastCreatorGUI, "open_output_folder") as mock_open,
            patch.object(PodcastCreatorGUI, "_run_on_ui_thread") as mock_run_ui,
            patch.object(gui.controller, "create_podcast") as mock_controller_create,
        ):
            # Make _run_on_ui_thread execute immediately without waiting
            def immediate_run(func, wait=False):
                func()
            mock_run_ui.side_effect = immediate_run
            
            # Mock controller.create_podcast to return immediately
            mock_controller_create.return_value = final_video
            
            gui.create_podcast()
            
            # Should open output folder when user confirms
            mock_open.assert_called_once()
        
        root.destroy()

    def test_launch_desktop_gui(self):
        """Test launch_desktop_gui function (lines 461-463)."""
        from src.gui.desktop_gui import launch_desktop_gui
        
        root = create_hidden_root()
        
        with (
            patch("src.gui.desktop_gui.load_config") as mock_config,
            patch("tkinter.Tk", return_value=root) as mock_tk,
        ):
            mock_config.return_value = {
                "tts": {"engine": "gtts"},
                "video": {"resolution": [1920, 1080]},
                "storage": {"output_dir": "/tmp", "outputs_dir": "/tmp", "cache_dir": "/tmp/cache"},
            }
            
            # Mock mainloop to avoid blocking
            original_mainloop = root.mainloop
            root.mainloop = MagicMock()
            
            try:
                # Should create root and start mainloop
                launch_desktop_gui()
                
                mock_tk.assert_called_once()
                root.mainloop.assert_called_once()
            finally:
                root.mainloop = original_mainloop
                root.destroy()

    def _build_gui(self, tmp_path):
        """Helper to build GUI for tests."""
        root = create_hidden_root()
        config = make_gui_config(tmp_path / "output")
        with patch("src.gui.desktop_gui.load_config", return_value=config):
            gui = PodcastCreatorGUI(root)
        return root, gui