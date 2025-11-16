"""
Comprehensive tkinter mocks for testing GUI components without display server.
"""

from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock


class MockTk:
    """Mock Tk root window."""

    def __init__(self):
        self.title_called = False
        self.title_text = None
        self.geometry_called = False
        self.geometry_size = None
        self.after_calls: List[tuple] = []
        self.withdraw_called = False
        self.mainloop_called = False
        self.destroy_called = False

    def title(self, text: str):
        """Set window title."""
        self.title_called = True
        self.title_text = text

    def geometry(self, size: str):
        """Set window geometry."""
        self.geometry_called = True
        self.geometry_size = size

    def after(self, delay: int, func: Callable, *args):
        """Schedule function to run after delay."""
        self.after_calls.append((delay, func, args))
        # Execute immediately in tests
        func(*args)

    def withdraw(self):
        """Hide window."""
        self.withdraw_called = True

    def mainloop(self):
        """Start main event loop."""
        self.mainloop_called = True

    def destroy(self):
        """Destroy window."""
        self.destroy_called = True


class MockStringVar:
    """Mock StringVar for tkinter variables."""

    def __init__(self, value: str = ""):
        self._value = value
        self.trace_calls: List[tuple] = []

    def get(self) -> str:
        """Get variable value."""
        return self._value

    def set(self, value: str):
        """Set variable value."""
        self._value = value

    def trace(self, mode: str, callback: Callable):
        """Trace variable changes."""
        self.trace_calls.append((mode, callback))


class MockBooleanVar:
    """Mock BooleanVar for tkinter boolean variables."""

    def __init__(self, value: bool = False):
        self._value = value
        self.trace_calls: List[tuple] = []

    def get(self) -> bool:
        """Get variable value."""
        return self._value

    def set(self, value: bool):
        """Set variable value."""
        self._value = value

    def trace(self, mode: str, callback: Callable):
        """Trace variable changes."""
        self.trace_calls.append((mode, callback))


class MockWidget:
    """Mock base widget class."""

    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.config_calls: List[Dict] = []
        self.pack_called = False
        self.grid_called = False
        self.state = "normal"
        self.text = kwargs.get("text", "")
        self.bg = kwargs.get("bg", "")
        self.fg = kwargs.get("fg", "")
        self.font = kwargs.get("font", "")
        self.command = kwargs.get("command")

    def config(self, **kwargs):
        """Configure widget."""
        self.config_calls.append(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def pack(self, **kwargs):
        """Pack widget."""
        self.pack_called = True

    def grid(self, **kwargs):
        """Grid widget."""
        self.grid_called = True

    def invoke(self):
        """Invoke widget command."""
        if self.command:
            self.command()


class MockEntry(MockWidget):
    """Mock Entry widget."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.textvariable = kwargs.get("textvariable")
        self.state = kwargs.get("state", "normal")
        self._content = ""

    def insert(self, index: str, text: str):
        """Insert text at index."""
        self._content += text

    def delete(self, start: str, end: str = None):
        """Delete text from start to end."""
        if end is None or end == "end":
            self._content = ""

    def get(self) -> str:
        """Get entry content."""
        if self.textvariable:
            return self.textvariable.get()
        return self._content


class MockText(MockWidget):
    """Mock Text widget (for ScrolledText)."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._content: List[str] = []
        self.see_called = False

    def insert(self, index: str, text: str):
        """Insert text at index."""
        self._content.append(text)

    def delete(self, start: str, end: str):
        """Delete text from start to end."""
        self._content = []

    def see(self, index: str):
        """Scroll to index."""
        self.see_called = True

    def get(self, start: str, end: str) -> str:
        """Get text from start to end."""
        return "\n".join(self._content)


class MockButton(MockWidget):
    """Mock Button widget."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = kwargs.get("command")


class MockLabel(MockWidget):
    """Mock Label widget."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.text = kwargs.get("text", "")


class MockFrame(MockWidget):
    """Mock Frame widget."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack_propagate_called = False

    def pack_propagate(self, value: bool):
        """Set pack propagate."""
        self.pack_propagate_called = True


class MockLabelFrame(MockFrame):
    """Mock LabelFrame widget."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.text = kwargs.get("text", "")


class MockFileDialog:
    """Mock filedialog module."""

    @staticmethod
    def askopenfilename(**kwargs) -> str:
        """Mock askopenfilename."""
        # Return empty string to simulate cancel
        return ""


class MockMessageBox:
    """Mock messagebox module."""

    @staticmethod
    def showerror(title: str, message: str):
        """Mock showerror."""
        pass

    @staticmethod
    def askyesno(title: str, message: str) -> bool:
        """Mock askyesno."""
        return False


def create_mock_tkinter_module():
    """Create a complete mock tkinter module."""
    mock_module = MagicMock()
    
    # Mock classes
    mock_module.Tk = MockTk
    mock_module.StringVar = MockStringVar
    mock_module.BooleanVar = MockBooleanVar
    mock_module.Entry = MockEntry
    mock_module.Text = MockText
    mock_module.Button = MockButton
    mock_module.Label = MockLabel
    mock_module.Frame = MockFrame
    mock_module.LabelFrame = MockLabelFrame
    
    # Mock modules
    mock_module.filedialog = MagicMock()
    mock_module.filedialog.askopenfilename = MockFileDialog.askopenfilename
    
    mock_module.messagebox = MagicMock()
    mock_module.messagebox.showerror = MockMessageBox.showerror
    mock_module.messagebox.askyesno = MockMessageBox.askyesno
    
    mock_module.scrolledtext = MagicMock()
    mock_module.scrolledtext.ScrolledText = MockText
    
    mock_module.ttk = MagicMock()
    
    return mock_module

