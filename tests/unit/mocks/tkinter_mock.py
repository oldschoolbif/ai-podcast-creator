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
        self.title_called = True
        self.title_text = text

    def geometry(self, size: str):
        self.geometry_called = True
        self.geometry_size = size

    def after(self, delay: int, func: Callable, *args):
        self.after_calls.append((delay, func, args))
        func(*args)

    def withdraw(self):
        self.withdraw_called = True

    def mainloop(self):
        self.mainloop_called = True

    def destroy(self):
        self.destroy_called = True


class MockStringVar:
    def __init__(self, value: str = ""):
        self._value = value
        self.trace_calls: List[tuple] = []

    def get(self) -> str:
        return self._value

    def set(self, value: str):
        self._value = value

    def trace(self, mode: str, callback: Callable):
        self.trace_calls.append((mode, callback))


class MockBooleanVar:
    def __init__(self, value: bool = False):
        self._value = value
        self.trace_calls: List[tuple] = []

    def get(self) -> bool:
        return self._value

    def set(self, value: bool):
        self._value = value

    def trace(self, mode: str, callback: Callable):
        self.trace_calls.append((mode, callback))


class MockWidget:
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
        self.config_calls.append(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def pack(self, **kwargs):
        self.pack_called = True

    def grid(self, **kwargs):
        self.grid_called = True

    def invoke(self):
        if self.command:
            self.command()


class MockEntry(MockWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.textvariable = kwargs.get("textvariable")
        self.state = kwargs.get("state", "normal")
        self._content = ""

    def insert(self, index: str, text: str):
        self._content += text

    def delete(self, start: str, end: str = None):
        if end is None or end == "end":
            self._content = ""

    def get(self) -> str:
        if self.textvariable:
            return self.textvariable.get()
        return self._content


class MockText(MockWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._content: List[str] = []
        self.see_called = False

    def insert(self, index: str, text: str):
        self._content.append(text)

    def delete(self, start: str, end: str):
        self._content = []

    def see(self, index: str):
        self.see_called = True

    def get(self, start: str, end: str) -> str:
        return "\n".join(self._content)


class MockButton(MockWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = kwargs.get("command")


class MockLabel(MockWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.text = kwargs.get("text", "")


class MockFrame(MockWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack_propagate_called = False
        self.columns = {}
        self.rows = {}

    def pack_propagate(self, value: bool):
        self.pack_propagate_called = True

    def columnconfigure(self, idx: int, **kwargs):
        self.columns[idx] = kwargs

    def rowconfigure(self, idx: int, **kwargs):
        self.rows[idx] = kwargs


class MockLabelFrame(MockFrame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.text = kwargs.get("text", "")


class MockFileDialog:
    @staticmethod
    def askopenfilename(**kwargs) -> str:
        return ""


class MockMessageBox:
    @staticmethod
    def showerror(title: str, message: str):
        pass

    @staticmethod
    def askyesno(title: str, message: str) -> bool:
        return False


def create_mock_tkinter_module():
    mock_module = MagicMock()

    # Common constants used by tkinter code
    mock_module.BOTH = "both"
    mock_module.X = "x"
    mock_module.LEFT = "left"
    mock_module.END = "end"
    mock_module.NORMAL = "normal"
    mock_module.DISABLED = "disabled"

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

