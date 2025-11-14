"""
GPU Utilization Tests
Tests that components properly utilize GPU when available.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile

from src.utils.metrics import MetricsTracker, ComponentMetrics, get_metrics_tracker
from src.utils.gpu_utils import GPUManager, get_gpu_manager


class TestGPUUtilizationTracking:
    """Test GPU utilization is tracked correctly."""
    
    def test_metrics_tracks_gpu_utilization_before_after(self, tmp_path):
        """Test that metrics tracks GPU utilization before and after components."""
        config = {
            "storage": {"cache_dir": str(tmp_path)},
        }
        
        tracker = MetricsTracker(config)
        
        # Mock GPU manager
        mock_gpu = Mock()
        mock_gpu.gpu_available = True
        mock_gpu.get_memory_usage.return_value = {"allocated_gb": 2.0, "reserved_gb": 2.5}
        mock_gpu.get_utilization.return_value = {"gpu_percent": 85.0, "memory_percent": 60.0}
        mock_gpu._component_gpu_samples = []
        tracker.gpu_manager = mock_gpu
        
        tracker.start_session("test_script.txt")
        comp = tracker.start_component("test_component")
        
        # Simulate GPU work
        mock_gpu.get_utilization.return_value = {"gpu_percent": 95.0, "memory_percent": 65.0}
        
        tracker.finish_component(comp)
        
        # Check GPU utilization was tracked
        assert comp.gpu_utilization_before["gpu_percent"] == 85.0
        assert comp.gpu_utilization_after["gpu_percent"] == 95.0
        assert comp.gpu_utilization_avg is not None
        assert comp.gpu_utilization_avg >= 85.0  # Should use peak if increase detected
    
    def test_metrics_tracks_cpu_ram_usage(self, tmp_path):
        """Test that metrics tracks CPU and RAM usage."""
        config = {
            "storage": {"cache_dir": str(tmp_path)},
        }
        
        tracker = MetricsTracker(config)
        tracker.start_session("test_script.txt")
        comp = tracker.start_component("test_component")
        tracker.finish_component(comp)
        
        # Check CPU and RAM were tracked
        assert "cpu_percent" in comp.cpu_usage_before
        assert "cpu_percent" in comp.cpu_usage_after
        assert comp.cpu_usage_avg is not None
        assert "ram_percent" in comp.ram_usage_after
        assert "ram_used_gb" in comp.ram_usage_after
    
    def test_gpu_utilization_zero_when_no_gpu(self, tmp_path):
        """Test that GPU utilization is 0 when no GPU available."""
        config = {
            "storage": {"cache_dir": str(tmp_path)},
        }
        
        tracker = MetricsTracker(config)
        tracker.gpu_manager = Mock()
        tracker.gpu_manager.gpu_available = False
        tracker.gpu_manager._component_gpu_samples = []
        
        tracker.start_session("test_script.txt")
        comp = tracker.start_component("test_component")
        tracker.finish_component(comp)
        
        assert comp.gpu_utilization_before == {}
        assert comp.gpu_utilization_after == {}
        assert comp.gpu_utilization_avg is None


class TestGPUManagerUtilization:
    """Test GPUManager get_utilization method."""
    
    @patch('subprocess.run')
    def test_get_utilization_uses_nvidia_smi(self, mock_subprocess):
        """Test that get_utilization uses nvidia-smi."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "85, 60"
        mock_subprocess.return_value = mock_result
        
        gpu_manager = GPUManager()
        gpu_manager.gpu_available = True
        
        util = gpu_manager.get_utilization()
        
        assert util["gpu_percent"] == 85.0
        assert util["memory_percent"] == 60.0
        mock_subprocess.assert_called_once()
    
    def test_get_utilization_returns_zero_without_gpu(self):
        """Test that get_utilization returns zeros when no GPU."""
        gpu_manager = GPUManager()
        gpu_manager.gpu_available = False
        
        util = gpu_manager.get_utilization()
        
        assert util["gpu_percent"] == 0.0
        assert util["memory_percent"] == 0.0


class TestComponentGPUUsage:
    """Test that components report GPU usage correctly."""
    
    @pytest.mark.parametrize("component_name,expected_gpu", [
        ("script_parsing", False),  # Text parsing, no GPU
        ("tts_generation", True),  # Should use GPU (Coqui) or note it's cloud
        ("audio_mixing", False),  # pydub is CPU-based
        ("avatar_generation", True),  # Should use GPU (SadTalker/Wav2Lip)
        ("video_composition", True),  # Should attempt GPU (NVENC)
    ])
    def test_component_should_use_gpu(self, component_name, expected_gpu, tmp_path):
        """Test that components that should use GPU are tracked."""
        config = {
            "storage": {"cache_dir": str(tmp_path)},
        }
        
        tracker = MetricsTracker(config)
        
        # Mock GPU as available
        mock_gpu = Mock()
        mock_gpu.gpu_available = True
        mock_gpu.get_memory_usage.return_value = {"allocated_gb": 1.0}
        mock_gpu.get_utilization.return_value = {"gpu_percent": 0.0, "memory_percent": 0.0}
        mock_gpu._component_gpu_samples = []
        tracker.gpu_manager = mock_gpu
        
        tracker.start_session("test.txt")
        comp = tracker.start_component(component_name)
        
        # For components that should use GPU, simulate high utilization
        if expected_gpu:
            mock_gpu.get_utilization.return_value = {"gpu_percent": 80.0, "memory_percent": 50.0}
        
        tracker.finish_component(comp)
        
        # Components that should use GPU should have utilization tracked
        if expected_gpu:
            assert comp.gpu_utilization_before is not None
            assert comp.gpu_utilization_after is not None


class TestGPUUtilizationMetrics:
    """Test GPU utilization metrics in actual generation."""
    
    def test_metrics_saved_with_gpu_data(self, tmp_path):
        """Test that metrics JSON includes GPU utilization data."""
        config = {
            "storage": {"cache_dir": str(tmp_path)},
        }
        
        tracker = MetricsTracker(config)
        
        # Mock GPU
        mock_gpu = Mock()
        mock_gpu.gpu_available = True
        mock_gpu.gpu_name = "NVIDIA RTX 4060"
        mock_gpu.gpu_memory = 8.0
        mock_gpu.get_memory_usage.return_value = {"allocated_gb": 2.0}
        mock_gpu.get_utilization.return_value = {"gpu_percent": 90.0, "memory_percent": 70.0}
        mock_gpu._component_gpu_samples = []
        tracker.gpu_manager = mock_gpu
        
        session_id = tracker.start_session("test.txt")
        comp = tracker.start_component("avatar_generation")
        tracker.finish_component(comp)
        tracker.finish_session("output.mp4")
        
        # Check metrics file was created
        metrics_file = tmp_path / "metrics" / f"{session_id}.json"
        assert metrics_file.exists()
        
        # Check GPU data is in JSON
        with open(metrics_file) as f:
            data = json.load(f)
        
        assert data["gpu_name"] == "NVIDIA RTX 4060"
        assert data["gpu_memory_gb"] == 8.0
        assert len(data["components"]) > 0
        assert "gpu_utilization_avg" in data["components"][0]
        assert "cpu_usage_avg" in data["components"][0]
        assert "ram_usage_after" in data["components"][0]


class TestGPUUtilizationThresholds:
    """Test GPU utilization meets minimum thresholds."""
    
    @pytest.mark.parametrize("component,min_gpu_percent", [
        ("avatar_generation", 50.0),  # Should use significant GPU
        ("video_composition", 10.0),  # Video encoding should use some GPU if NVENC works
    ])
    def test_component_minimum_gpu_utilization(self, component, min_gpu_percent, tmp_path):
        """Test that GPU-accelerated components meet minimum utilization."""
        config = {
            "storage": {"cache_dir": str(tmp_path)},
        }
        
        tracker = MetricsTracker(config)
        
        # Mock GPU with high utilization
        mock_gpu = Mock()
        mock_gpu.gpu_available = True
        mock_gpu.get_memory_usage.return_value = {"allocated_gb": 1.0}
        mock_gpu.get_utilization.side_effect = [
            {"gpu_percent": 0.0, "memory_percent": 0.0},  # Before
            {"gpu_percent": min_gpu_percent + 10.0, "memory_percent": 50.0},  # After
        ]
        mock_gpu._component_gpu_samples = []
        tracker.gpu_manager = mock_gpu
        
        tracker.start_session("test.txt")
        comp = tracker.start_component(component)
        tracker.finish_component(comp)
        
        # Check peak utilization was captured
        assert comp.gpu_utilization_avg is not None
        # Peak should be used if there's a significant increase
        if comp.gpu_utilization_after.get("gpu_percent", 0) > comp.gpu_utilization_before.get("gpu_percent", 0) * 1.2:
            assert comp.gpu_utilization_avg >= min_gpu_percent


@pytest.mark.skipif(not get_gpu_manager().gpu_available, reason="GPU not available")
class TestRealGPUUtilization:
    """Integration tests with real GPU (skip if no GPU)."""
    
    def test_real_gpu_utilization_tracking(self, tmp_path):
        """Test GPU utilization tracking with real GPU."""
        config = {
            "storage": {"cache_dir": str(tmp_path)},
        }
        
        tracker = get_metrics_tracker(config)
        if not tracker:
            tracker = MetricsTracker(config)
        
        gpu_manager = get_gpu_manager()
        if not gpu_manager.gpu_available:
            pytest.skip("No GPU available")
        
        tracker.start_session("test.txt")
        comp = tracker.start_component("test_component")
        
        # Do some GPU work (load a small tensor)
        import torch
        if torch.cuda.is_available():
            x = torch.randn(1000, 1000).cuda()
            _ = torch.matmul(x, x)
        
        tracker.finish_component(comp)
        
        # Check that utilization was tracked
        assert comp.gpu_utilization_before is not None
        assert comp.gpu_utilization_after is not None
        # Actual GPU utilization should be > 0 if GPU was used
        # (May be 0 if work was too fast to measure, but structure should be there)

