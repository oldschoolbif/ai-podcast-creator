"""
Widget interaction tests for Desktop GUI using tkinter mocks (no real display).
"""

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.unit.mocks.tkinter_mock import create_mock_tkinter_module


class TestDesktopGUIWithMocks:
    def setup_method(self):
        # Inject mocked tkinter before importing GUI module
        self.mock_tk = create_mock_tkinter_module()
        self.patcher = patch.dict(sys.modules, {"tkinter": self.mock_tk})
        self.patcher.start()
        # Reload module to bind to mocked tkinter
        from src.gui import desktop_gui as dg

        importlib.reload(dg)
        self.dg = dg

    def teardown_method(self):
        self.patcher.stop()

    def test_gui_initialization_sets_title_and_geometry(self):
        root = self.mock_tk.Tk()
        gui = self.dg.PodcastCreatorGUI(root)

        assert root.title_called is True
        assert root.geometry_called is True
        assert isinstance(gui.log_text, self.mock_tk.Text)

    def test_browse_script_selects_file_and_logs(self, tmp_path):
        # Configure filedialog to return a script path
        script_path = tmp_path / "script.txt"
        script_path.write_text("Hello", encoding="utf-8")
        self.mock_tk.filedialog.askopenfilename = MagicMock(return_value=str(script_path))

        root = self.mock_tk.Tk()
        gui = self.dg.PodcastCreatorGUI(root)

        gui.browse_script()

        assert gui.script_file.get() == str(script_path)
        log_content = gui.log_text.get(1.0, "end")
        assert "Script selected" in log_content

    def test_update_status_updates_status_label(self):
        root = self.mock_tk.Tk()
        gui = self.dg.PodcastCreatorGUI(root)

        gui.update_status("Working", "blue")
        # Verify last config call updated text/fg
        assert gui.status_label.config_calls[-1]["text"] == "Working"
        assert gui.status_label.config_calls[-1]["fg"] == "blue"

    def test_create_podcast_shows_error_without_script(self):
        # Track messagebox.showerror calls
        calls = {"count": 0}

        def showerror(title, message):
            calls["count"] += 1
            calls["title"] = title
            calls["message"] = message

        self.mock_tk.messagebox.showerror = showerror

        root = self.mock_tk.Tk()
        gui = self.dg.PodcastCreatorGUI(root)

        # Ensure no script selected
        gui.script_file.set("")
        gui.create_podcast()

        assert calls["count"] == 1
        assert "Please select a script file" in calls["message"]

    def test_log_appends_text_to_scrolled_text(self):
        root = self.mock_tk.Tk()
        gui = self.dg.PodcastCreatorGUI(root)

        gui.log("Test message")
        content = gui.log_text.get(1.0, "end")
        assert "Test message" in content
