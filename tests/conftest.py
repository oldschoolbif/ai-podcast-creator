"""Deterministic pytest configuration and fixtures."""

from __future__ import annotations

import array
import base64
import contextlib
import math
import os
import random
import shutil
import socket
import subprocess
import sys
import wave
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterator
from unittest.mock import MagicMock

import pytest

try:  # Optional dependency for time freezing.
    from freezegun import freeze_time as _freeze_time  # type: ignore
except (ImportError, AttributeError):  # pragma: no cover - freezegun is optional or incompatible.
    _freeze_time = None  # type: ignore


TEST_SEED_ENV = "TEST_SEED"
DEFAULT_TEST_SEED = 1337

_NETWORK_ALLOWED = False
_NETWORK_ERROR = RuntimeError(
    "Network access is disallowed for this test. Use @pytest.mark.network to opt-in."
)

GPU_ENV = "PY_ENABLE_GPU_TESTS"
GPU_SKIP_MESSAGE = "GPU quarantine: set PY_ENABLE_GPU_TESTS=1 to enable GPU tests."
_FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None
_SILENCE_MP3_BASE64 = (
    "SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYyLjMuMTAwAAAAAAAAAAAAAAD/+0DAAAAAAAAAAAAAAAAAAAAAAABJbmZvAAAADwAAACgAABD2"
    "ABAQFhYdHR0jIykpKS8vNTU1OztBQUFISE5OTlRUWlpaYGBmZmZsbHJycnl5f39/hYWLi4uRkZeXl52dpKSkqqqwsLC2try8vMLCyMjIzs7V"
    "1dXb2+Hh4efn7e3t8/P5+fn//wAAAABMYXZjNjIuMTEAAAAAAAAAAAAAAAAkBXwAAAAAAAAQ9in4ddEAAAAAAP/7EMQAA8AAAaQAAAAgAAA0"
    "gAAABExBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy4xM"
    "DBVVVVV//sQxCmDwAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVMQU1FMy4xMDBVVVVX/+xDEUwPAAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMuMTAwVVVVVf/7EMR8g8AAAaQAAAAgAAA0gAAABFVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy4xMDBVVVVV//sQxKYDwAABpAAAACAAADSAA"
    "AAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMF"
    "VVVVX/+xDEz4PAAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVTEFNRTMuMTAwVVVVVf/7EMTWA8AAAaQAAAAgAAA0gAAABFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy4xMDBVVVVV//sQxNYDwAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVX/+xDE1gPAAAGkAAAAIA"
    "AA0gAAABFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1FMy"
    "4xMDBVVVVV//sQxNYDwAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVX/+xDE1gPAAAGkAA"
    "AAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVMQU1"
    "FMy4xMDBVVVVV//sQxNYDwAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAARVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVUxBTUUzLjEwMFVVVVX/+xDE1gP"
    "AAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/7EMTWA8AAAaQAAAAgAAA0gAAABFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//sQxNYDwAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAAR"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "f/7EMTWA8AAAaQAAAAgAAA0gAAABFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/7EMTWA8AAAaQAAAAgAAA0gAAABFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/+xDE1gPAAAGkAAAAIAAANIAAAARVVVVVVVVVVV"
    "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/+xDE1gPAAAGkAAAAI"
    "AAANIAAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    "VVVVVVVVV"
)


def _ensure_network_allowed() -> None:
    if not _NETWORK_ALLOWED:
        raise _NETWORK_ERROR


@pytest.fixture(scope="session", autouse=True)
def fixed_seed() -> int:
    """Seed Python's RNG (and numpy if installed) for deterministic tests."""
    seed = int(os.environ.get(TEST_SEED_ENV, DEFAULT_TEST_SEED))
    random.seed(seed)
    os.environ.setdefault("PYTHONHASHSEED", str(seed))

    try:
        import numpy as np  # type: ignore
    except ImportError:  # pragma: no cover - numpy optional.
        np = None

    if np is not None:
        np.random.seed(seed)

    return seed


@pytest.fixture(scope="session", autouse=True)
def _no_network_by_default() -> Iterator[None]:
    """Block outbound network access unless a test opts-in via @pytest.mark.network."""
    original_create_connection = socket.create_connection
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex

    def guarded_create_connection(*args, **kwargs):
        _ensure_network_allowed()
        return original_create_connection(*args, **kwargs)

    def guarded_connect(self, *args, **kwargs):
        _ensure_network_allowed()
        return original_connect(self, *args, **kwargs)

    def guarded_connect_ex(self, *args, **kwargs):
        _ensure_network_allowed()
        return original_connect_ex(self, *args, **kwargs)

    socket.create_connection = guarded_create_connection
    socket.socket.connect = guarded_connect  # type: ignore[assignment]
    socket.socket.connect_ex = guarded_connect_ex  # type: ignore[assignment]

    try:
        yield
    finally:
        socket.create_connection = original_create_connection
        socket.socket.connect = original_connect  # type: ignore[assignment]
        socket.socket.connect_ex = original_connect_ex  # type: ignore[assignment]


@contextlib.contextmanager
def _frozen_time_cm(target: str):
    """Context manager that freezes time using freezegun if available."""
    if _freeze_time is None:
        raise RuntimeError("freezegun is not installed; install it to use frozen_time.")
    with _freeze_time(target):
        yield


@pytest.fixture
def frozen_time() -> Callable[[str], contextlib.AbstractContextManager[None]]:
    """Fixture returning a callable to freeze time within tests."""
    if _freeze_time is None:
        pytest.skip("freezegun is not installed.")

    def _freezer(target: str):
        return _frozen_time_cm(target)

    return _freezer


def write_sine_wav(
    output_path: Path,
    seconds: float,
    rate: int = 44_100,
    frequency: float = 440.0,
    amplitude: float = 0.5,
) -> Path:
    """Write a deterministic sine wave to a WAV file."""
    amplitude = max(0.0, min(amplitude, 1.0))
    frames = int(rate * seconds)
    data = array.array("h")
    max_amplitude = int(amplitude * 32767)

    for i in range(frames):
        sample = int(max_amplitude * math.sin(2 * math.pi * frequency * i / rate))
        data.append(sample)

    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(data.tobytes())

    return output_path


def create_valid_mp3_file(output_path: Path, duration_seconds: float = 1.0) -> Path:
    """Create a lightweight MP3 file for tests.

    Attempts to use ffmpeg when available; otherwise falls back to a bundled silent MP3.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if _FFMPEG_AVAILABLE:
        duration = max(float(duration_seconds), 0.1)
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=44100:cl=mono",
            "-t",
            f"{duration:.2f}",
            "-q:a",
            "9",
            str(output_path),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        except Exception:  # pragma: no cover - fallback handles environments without ffmpeg.
            pass

    data = base64.b64decode(_SILENCE_MP3_BASE64)
    repeats = max(1, int(math.ceil(max(duration_seconds, 0.1))))
    output_path.write_bytes(data * repeats)
    return output_path


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Enable network access for tests marked with @pytest.mark.network."""
    if item.get_closest_marker("gpu") is not None:
        _handle_gpu_quarantine()

    global _NETWORK_ALLOWED  # noqa: PLW0603
    _NETWORK_ALLOWED = item.get_closest_marker("network") is not None


def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item | None) -> None:
    """Disable network access after every test."""
    del item, nextitem
    global _NETWORK_ALLOWED  # noqa: PLW0603
    _NETWORK_ALLOWED = False


def _gpu_tests_enabled() -> bool:
    return os.getenv(GPU_ENV, "0") == "1"


@lru_cache(maxsize=1)
def _torch_module():
    try:
        import torch  # type: ignore
    except ImportError:  # pragma: no cover - torch optional
        return None
    return torch


def _handle_gpu_quarantine() -> None:
    if not _gpu_tests_enabled():
        pytest.skip(GPU_SKIP_MESSAGE)

    torch = _torch_module()
    if torch is not None and not torch.cuda.is_available():
        pytest.skip("GPU tests enabled but no CUDA device available.")


def _make_multiprocessing_idempotent() -> None:
    """Ensure multiprocessing.set_start_method ignores redundant calls."""
    try:
        import multiprocessing as mp
    except ImportError:  # pragma: no cover - multiprocessing always present.
        return

    original = mp.set_start_method

    def safe_set_start_method(method: str, *args, **kwargs):
        try:
            return original(method, *args, **kwargs)
        except RuntimeError as exc:  # pragma: no cover - only during mutmut
            if "context has already been set" in str(exc):
                return None
            raise

    mp.set_start_method = safe_set_start_method  # type: ignore[assignment]


_make_multiprocessing_idempotent()


def _patch_mutmut_trampoline() -> None:
    """Allow mutmut trampoline to accept module names with src. prefix."""
    try:
        from mutmut import __main__ as mutmut_main  # type: ignore
    except ImportError:  # pragma: no cover - only during mutmut runs.
        return

    original = getattr(mutmut_main, "record_trampoline_hit", None)
    if original is None:
        return

    def safe_record_trampoline_hit(name: str) -> None:
        if name.startswith("src."):
            name = name[len("src.") :]
        try:
            original(name)
        except AssertionError as exc:
            if "Failed trampoline hit" in str(exc) and name.startswith("tests."):
                return
            raise

    mutmut_main.record_trampoline_hit = safe_record_trampoline_hit  # type: ignore[attr-defined]


_patch_mutmut_trampoline()


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Alias for tmp_path fixture for backward compatibility."""
    return tmp_path


@pytest.fixture
def test_config(temp_dir: Path) -> dict:
    """Create a test configuration dictionary."""
    return {
        "storage": {
            "cache_dir": str(temp_dir / "cache"),
            "outputs_dir": str(temp_dir / "outputs"),
        },
        "video": {
            "background_path": str(temp_dir / "background.jpg"),
            "quality": "fastest",
        },
        "tts": {
            "engine": "gtts",
        },
        "music": {
            "engine": "placeholder",
            "musicgen": {
                "model": "small",
                "duration": 10,
            },
        },
        "avatar": {
            "engine": "sadtalker",
            "sadtalker": {
                "checkpoint_dir": str(temp_dir / "sadtalker"),
            },
        },
    }


@pytest.fixture
def test_config_visualization(temp_dir: Path) -> dict:
    """Create test config with visualization settings."""
    return {
        "video": {
            "resolution": [1920, 1080],
            "fps": 30,
        },
        "visualization": {
            "style": "waveform",
            "primary_color": [0, 150, 255],
            "secondary_color": [255, 100, 200],
            "background_color": [10, 10, 20],
            "blur": 3,
            "sensitivity": 1.0,
        },
    }


@pytest.fixture
def sample_script_text() -> str:
    """Sample script text for testing."""
    return """# Introduction
Welcome to today's podcast episode.

## Main Content
Today we're discussing the importance of software testing.

## Conclusion
Thank you for listening!"""


@pytest.fixture
def sample_script_file(temp_dir: Path, sample_script_text: str) -> Path:
    """Create a sample script file for testing."""
    script_file = temp_dir / "sample_script.txt"
    script_file.write_text(sample_script_text)
    return script_file


@pytest.fixture
def mock_audio_data():
    """Create mock audio data for testing."""
    try:
        import numpy as np
    except ImportError:
        pytest.skip("numpy not installed")
    
    # Simulate 2 seconds of audio at 22050 Hz
    sr = 22050
    duration = 2.0
    samples = int(sr * duration)
    y = np.random.randn(samples).astype(np.float32) * 0.3
    return y, sr, duration


@pytest.fixture
def skip_if_no_internet():
    """Fixture to skip tests if network is not available (for e2e tests that require internet)."""
    # In mutation testing, network is disabled by default
    # Tests using this fixture will be skipped unless @pytest.mark.network is also present
    if not os.getenv("PY_ENABLE_NETWORK_TESTS", "0") == "1":
        pytest.skip("Network tests disabled (set PY_ENABLE_NETWORK_TESTS=1 to enable)")


@pytest.fixture
def skip_if_no_gpu():
    """Fixture to skip tests if GPU is not available."""
    # Check if GPU tests are enabled
    if not _gpu_tests_enabled():
        pytest.skip("GPU tests disabled (set PY_ENABLE_GPU_TESTS=1 to enable)")
    
    # Check if CUDA is actually available
    torch = _torch_module()
    if torch is None:
        pytest.skip("PyTorch not installed")
    
    if not torch.cuda.is_available():
        pytest.skip("CUDA GPU not available")


@pytest.fixture
def stub_audiocraft(monkeypatch):
    """Stub audiocraft module if not available to allow tests with mocks to run."""
    if "audiocraft" not in sys.modules:
        # Create a minimal stub for audiocraft
        stub_audiocraft_module = MagicMock()
        stub_audiocraft_module.models = MagicMock()
        stub_audiocraft_module.models.MusicGen = MagicMock()
        monkeypatch.setitem(sys.modules, "audiocraft", stub_audiocraft_module)
    yield


@pytest.fixture
def stub_tts(monkeypatch):
    """Stub TTS (Coqui) module if not available to allow tests with mocks to run."""
    if "TTS" not in sys.modules:
        # Create a minimal stub for TTS
        stub_tts_module = MagicMock()
        stub_tts_module.api = MagicMock()
        stub_tts_module.api.TTS = MagicMock()
        monkeypatch.setitem(sys.modules, "TTS", stub_tts_module)
    yield


@pytest.fixture
def test_config_file(tmp_path: Path) -> Path:
    """Create a temporary test configuration YAML file."""
    config_path = tmp_path / "test_config.yaml"
    config_content = """tts:
  engine: gtts
storage:
  cache_dir: {cache_dir}
  outputs_dir: {outputs_dir}
video:
  quality: fastest
music:
  engine: placeholder
""".format(
        cache_dir=str(tmp_path / "cache"),
        outputs_dir=str(tmp_path / "outputs"),
    )
    config_path.write_text(config_content)
    return config_path
