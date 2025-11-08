"""
Tests for advanced waveform features:
- Orientation offset
- Rotation
- Amplitude multiplier
- Multiple instances
- Instance spacing and intersection
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def test_config_waveform(temp_dir):
    """Create test config with waveform settings."""
    return {
        "video": {
            "resolution": [1920, 1080],
            "fps": 30,
        },
        "visualization": {
            "style": "waveform",
            "primary_color": [0, 255, 0],
            "secondary_color": [0, 255, 100],
            "background_color": [0, 0, 0],
            "sensitivity": 1.0,
            "waveform": {
                "position": "bottom",
                "num_lines": 1,
                "line_thickness": 2,
                "orientation_offset": None,
                "rotation": 0,
                "amplitude_multiplier": 1.0,
                "num_instances": 1,
                "instances_offset": 0,
                "instances_intersect": False,
            },
        },
    }


@pytest.fixture
def mock_audio_data():
    """Create mock audio data."""
    sr = 22050
    duration = 2.0
    samples = int(sr * duration)
    y = np.random.randn(samples).astype(np.float32) * 0.3
    return y, sr, duration


class TestWaveformOrientationOffset:
    """Test orientation offset feature."""

    def test_init_with_orientation_offset(self, test_config_waveform):
        """Test initialization with orientation offset."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["orientation_offset"] = 50.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.orientation_offset == 50.0

    def test_orientation_offset_bottom(self, test_config_waveform):
        """Test orientation offset at bottom (0)."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["orientation_offset"] = 0.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.orientation_offset == 0.0

    def test_orientation_offset_top(self, test_config_waveform):
        """Test orientation offset at top (100)."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["orientation_offset"] = 100.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.orientation_offset == 100.0


class TestWaveformRotation:
    """Test rotation feature."""

    def test_init_with_rotation(self, test_config_waveform):
        """Test initialization with rotation."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["rotation"] = 45.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.rotation == 45.0

    def test_rotation_zero(self, test_config_waveform):
        """Test rotation at zero (no rotation)."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["rotation"] = 0.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.rotation == 0.0

    def test_rotation_90_degrees(self, test_config_waveform):
        """Test rotation at 90 degrees."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["rotation"] = 90.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.rotation == 90.0


class TestWaveformAmplitudeMultiplier:
    """Test amplitude multiplier feature."""

    def test_init_with_amplitude_multiplier(self, test_config_waveform):
        """Test initialization with amplitude multiplier."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["amplitude_multiplier"] = 2.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.amplitude_multiplier == 2.0

    def test_amplitude_multiplier_low(self, test_config_waveform):
        """Test low amplitude multiplier."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["amplitude_multiplier"] = 0.1
        viz = AudioVisualizer(test_config_waveform)

        assert viz.amplitude_multiplier == 0.1

    def test_amplitude_multiplier_high(self, test_config_waveform):
        """Test high amplitude multiplier."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["amplitude_multiplier"] = 3.0
        viz = AudioVisualizer(test_config_waveform)

        assert viz.amplitude_multiplier == 3.0


class TestWaveformMultipleInstances:
    """Test multiple instances feature."""

    def test_init_with_multiple_instances(self, test_config_waveform):
        """Test initialization with multiple instances."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["num_instances"] = 3
        viz = AudioVisualizer(test_config_waveform)

        assert viz.num_instances == 3

    def test_instances_offset(self, test_config_waveform):
        """Test instance spacing offset."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["num_instances"] = 2
        test_config_waveform["visualization"]["waveform"]["instances_offset"] = 20
        viz = AudioVisualizer(test_config_waveform)

        assert viz.num_instances == 2
        assert viz.instances_offset == 20

    def test_instances_intersect(self, test_config_waveform):
        """Test instance intersection flag."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"]["instances_intersect"] = True
        viz = AudioVisualizer(test_config_waveform)

        assert viz.instances_intersect is True


class TestWaveformCombinedFeatures:
    """Test combined advanced features."""

    def test_all_features_combined(self, test_config_waveform):
        """Test all advanced features together."""
        from src.core.audio_visualizer import AudioVisualizer

        test_config_waveform["visualization"]["waveform"].update({
            "orientation_offset": 50.0,
            "rotation": 30.0,
            "amplitude_multiplier": 2.0,
            "num_instances": 3,
            "instances_offset": 15,
            "instances_intersect": True,
        })
        viz = AudioVisualizer(test_config_waveform)

        assert viz.orientation_offset == 50.0
        assert viz.rotation == 30.0
        assert viz.amplitude_multiplier == 2.0
        assert viz.num_instances == 3
        assert viz.instances_offset == 15
        assert viz.instances_intersect is True

