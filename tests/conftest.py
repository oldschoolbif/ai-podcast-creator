"""
Pytest Configuration and Fixtures
Shared fixtures and configuration for all tests
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Get test data directory."""
    data_dir = project_root / "tests" / "test_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_config(temp_dir):
    """Create a minimal test configuration."""
    config = {
        "app": {"name": "AI Podcast Creator", "version": "1.0.0", "debug": True},
        "tts": {"engine": "gtts", "gtts_tld": "com", "sample_rate": 24000, "output_format": "wav"},
        "music": {"engine": "library", "enabled": False},
        "avatar": {"engine": "none", "enabled": False},
        "storage": {
            "cache_dir": str(temp_dir / "cache"),
            "output_dir": str(temp_dir / "output"),
            "outputs_dir": str(temp_dir / "output"),  # Added for VideoComposer
            "models_dir": str(temp_dir / "models"),
        },
        "video": {
            "fps": 30,
            "resolution": [1920, 1080],
            "codec": "libx264",
            "background_path": str(temp_dir / "background.jpg"),
            "bitrate": "5000k",
        },
        "processing": {"audio_format": "wav", "sample_rate": 24000, "normalize_audio": True},
    }

    # Create directories
    for dir_key in ["cache_dir", "output_dir", "outputs_dir", "models_dir"]:
        Path(config["storage"][dir_key]).mkdir(parents=True, exist_ok=True)

    # Create dummy background image
    background_path = Path(config["video"]["background_path"])
    background_path.touch()

    return config


@pytest.fixture
def test_config_visualization(temp_dir):
    """Create a configuration tailored for visualization tests."""
    config = {
        "visualization": {
            "style": "waveform",
            "resolution": [1280, 720],
            "fps": 30,
            "color_primary": [255, 255, 255],
            "color_secondary": [0, 0, 0],
            "background_color": [0, 0, 0],
            "blur": 2,
            "sensitivity": 1.0,
        },
        "video": {
            "resolution": [1280, 720],
            "fps": 30,
        },
        "storage": {
            "output_dir": str(temp_dir / "output"),
            "cache_dir": str(temp_dir / "cache"),
            "outputs_dir": str(temp_dir / "output"),
        },
        "audio": {
            "sample_rate": 24000,
            "duration": 1.0,
        },
    }

    for path_key in ["output_dir", "cache_dir", "outputs_dir"]:
        Path(config["storage"][path_key]).mkdir(parents=True, exist_ok=True)

    return config


@pytest.fixture
def test_config_file(test_config, temp_dir):
    """Create a temporary config file."""
    config_path = temp_dir / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(test_config, f)
    return config_path


@pytest.fixture
def sample_script_text():
    """Sample podcast script for testing."""
    return """[SPEAKER: Host]
Hello and welcome to this test podcast.

This is a sample script for testing purposes.

[MUSIC: calm background music]

Thank you for listening!

[END]"""


@pytest.fixture
def sample_script_file(temp_dir, sample_script_text):
    """Create a sample script file."""
    script_path = temp_dir / "test_script.txt"
    script_path.write_text(sample_script_text)
    return script_path


@pytest.fixture
def mock_audio_file(temp_dir):
    """Create a mock audio file for testing."""
    import numpy as np
    import soundfile as sf

    # Generate 1 second of silence
    sample_rate = 24000
    duration = 1.0
    samples = int(sample_rate * duration)
    audio_data = np.zeros(samples, dtype=np.float32)

    audio_path = temp_dir / "test_audio.wav"
    sf.write(str(audio_path), audio_data, sample_rate)

    return audio_path


@pytest.fixture
def mock_audio_data():
    """Return synthetic audio data (y, sample_rate, duration)."""
    import numpy as np

    sample_rate = 24000
    duration = 1.0
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 440 * t)

    return y.astype(np.float32), sample_rate, duration


@pytest.fixture
def gpu_available():
    """Check if GPU is available for testing."""
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


@pytest.fixture
def skip_if_no_gpu(gpu_available):
    """Skip test if GPU not available."""
    if not gpu_available:
        pytest.skip("GPU not available")


@pytest.fixture
def skip_if_no_internet():
    """Skip test if no internet connection."""
    import socket

    try:
        # Try to connect to Google DNS
        socket.create_connection(("8.8.8.8", 53), timeout=3)
    except OSError:
        pytest.skip("No internet connection")


# Pytest hooks


def pytest_configure(config):
    """Configure pytest."""
    # Register custom markers
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "gpu: mark test as requiring GPU")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    # Add markers based on test names
    for item in items:
        # Mark slow tests
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)

        # Mark GPU tests
        if "gpu" in item.nodeid.lower():
            item.add_marker(pytest.mark.gpu)

        # Mark network tests
        if "network" in item.nodeid.lower() or "api" in item.nodeid.lower():
            item.add_marker(pytest.mark.network)


def pytest_runtest_setup(item):
    """Setup for each test."""
    # Skip GPU tests if GPU not available
    if "gpu" in [marker.name for marker in item.iter_markers()]:
        try:
            import torch

            if not torch.cuda.is_available():
                pytest.skip("GPU not available")
        except ImportError:
            pytest.skip("PyTorch not installed")

    # Skip network tests if requested
    if "network" in [marker.name for marker in item.iter_markers()]:
        if item.config.getoption("--skip-network", default=False):
            pytest.skip("Skipping network tests")
