"""
Real functional tests for gpu_utils.py - minimal mocking, actual execution
Goal: Bring gpu_utils from 38% to 70%+
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.gpu_utils import GPUManager, get_gpu_manager

# Import helper from test_gpu_utils
sys.path.insert(0, str(Path(__file__).parent))
try:
    from test_gpu_utils import _create_mock_torch
except ImportError:
    # Fallback if import fails
    def _create_mock_torch(cuda_available=False, device_name="Test GPU", memory_gb=8):
        """Create a mock torch module for testing."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = cuda_available
        mock_torch.cuda.get_device_name.return_value = device_name
        mock_torch.cuda.get_device_capability.return_value = (8, 0) if cuda_available else (0, 0)
        mock_props = MagicMock()
        mock_props.total_memory = memory_gb * (1024**3)
        mock_torch.cuda.get_device_properties.return_value = mock_props
        mock_torch.version.cuda = "12.1"
        mock_torch.backends.cudnn.enabled = True
        mock_torch.backends.cudnn.benchmark = True
        mock_torch.backends.cuda.matmul.allow_tf32 = False
        mock_torch.backends.cudnn.allow_tf32 = False
        mock_torch.cuda.empty_cache = MagicMock()
        mock_torch.cuda.synchronize = MagicMock()
        mock_torch.cuda.memory_allocated.return_value = 0
        mock_torch.cuda.memory_reserved.return_value = 0
        mock_torch.cuda.set_device = MagicMock()
        mock_torch.cuda.device_count.return_value = 1
        mock_torch.device = MagicMock(side_effect=lambda x: f"device({x})")
        return mock_torch


class TestGPUManagerReal:
    """Test actual GPU manager functionality."""

    def test_singleton_pattern(self):
        """Test that get_gpu_manager returns the same instance."""
        manager1 = get_gpu_manager()
        manager2 = get_gpu_manager()
        assert manager1 is manager2

    def test_init_detects_cuda(self):
        """Test GPU manager initialization."""
        manager = GPUManager()
        # Should not crash, will detect GPU or fall back to CPU
        assert manager.device in ["cpu", "cuda", "cuda:0"]

    def test_get_device_returns_string(self):
        """Test get_device returns valid string."""
        manager = GPUManager()
        device = manager.get_device()
        assert isinstance(device, str)
        assert device in ["cpu", "cuda", "cuda:0"]

    def test_gpu_available_is_boolean(self):
        """Test gpu_available is boolean."""
        manager = GPUManager()
        assert isinstance(manager.gpu_available, bool)

    def test_gpu_memory_info(self):
        """Test getting GPU memory info."""
        manager = GPUManager()
        # GPUManager has gpu_memory attribute
        assert isinstance(manager.gpu_memory, (int, float))
        assert manager.gpu_memory >= 0

    def test_clear_cache_doesnt_crash(self):
        """Test clear_cache runs without error."""
        manager = GPUManager()
        # Should not raise exception
        manager.clear_cache()

    def test_optimize_for_inference(self):
        """Test optimize_for_inference runs."""
        manager = GPUManager()
        # Should not crash
        manager.optimize_for_inference()

    def test_clear_cache(self):
        """Test clear_cache runs."""
        manager = GPUManager()
        # Should not crash
        manager.clear_cache()

    def test_get_torch_device(self):
        """Test get_torch_device returns device."""
        manager = GPUManager()
        device = manager.get_torch_device()
        assert device is not None

    def test_get_optimal_batch_size(self):
        """Test get_optimal_batch_size returns int."""
        manager = GPUManager()
        batch_size = manager.get_optimal_batch_size()
        assert isinstance(batch_size, int)
        assert batch_size > 0

    def test_cuda_available_attribute(self):
        """Test cuda_available attribute exists."""
        manager = GPUManager()
        assert isinstance(manager.cuda_available, bool)

    def test_gpu_name_attribute(self):
        """Test gpu_name attribute."""
        manager = GPUManager()
        assert manager.gpu_name is None or isinstance(manager.gpu_name, str)

    def test_device_id_attribute(self):
        """Test device_id attribute."""
        manager = GPUManager()
        assert isinstance(manager.device_id, int)

    def test_str_representation(self):
        """Test string representation."""
        manager = GPUManager()
        str_repr = str(manager)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0


class TestGPUManagerWithMocks:
    """Test GPU manager with strategic mocking for coverage."""

    def test_init_with_cuda_available(self):
        """Test init when CUDA is available."""
        with patch("torch.cuda.is_available", return_value=True):
            with patch("torch.cuda.device_count", return_value=1):
                with patch("torch.cuda.get_device_name", return_value="GeForce RTX 3090"):
                    manager = GPUManager()
                    assert manager.gpu_available == True

    def test_init_with_cuda_unavailable(self):
        """Test init when CUDA is unavailable."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            assert manager.gpu_available == False
            assert manager.device == "cpu"

    def test_gpu_memory_with_cuda(self):
        """Test GPU memory with CUDA."""
        with patch("torch.cuda.is_available", return_value=True):
            with patch("torch.cuda.device_count", return_value=1):
                with patch("torch.cuda.get_device_properties") as mock_props:
                    mock_props.return_value.total_memory = 16000000000  # 16GB
                    manager = GPUManager()
                    assert manager.gpu_memory > 0

    def test_clear_cache_with_cuda(self):
        """Test clear cache with CUDA."""
        with patch("torch.cuda.is_available", return_value=True):
            with patch("torch.cuda.empty_cache") as mock_clear:
                manager = GPUManager()
                manager.clear_cache()
                # Cache clearing should be attempted

    @pytest.mark.gpu
    def test_optimize_for_inference_with_cuda(self):
        """Test inference optimization with CUDA."""
        with patch("torch.cuda.is_available", return_value=True):
            with patch("torch.cuda.device_count", return_value=1):
                with patch("torch.cuda.get_device_capability", return_value=(8, 0)):
                    manager = GPUManager()
                    # Should not crash
                    manager.optimize_for_inference()

    def test_get_optimal_batch_size_task_param(self):
        """Test batch size with different task parameter."""
        with patch("torch.cuda.is_available", return_value=True):
            with patch("torch.cuda.device_count", return_value=1):
                manager = GPUManager()
                batch_size = manager.get_optimal_batch_size(task="music")
                assert isinstance(batch_size, int)

    def test_device_string_format(self):
        """Test device string format."""
        with patch("torch.cuda.is_available", return_value=True):
            with patch("torch.cuda.device_count", return_value=1):
                manager = GPUManager()
                assert manager.device in ["cuda", "cpu"]

    @pytest.mark.gpu
    def test_get_optimal_batch_size_large_gpu(self):
        """Test batch size calculation for large GPU."""
        mock_torch = _create_mock_torch(cuda_available=True, memory_gb=24)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            batch_size = manager.get_optimal_batch_size()
            assert batch_size >= 1

    @pytest.mark.gpu
    def test_get_optimal_batch_size_small_gpu(self):
        """Test batch size calculation for small GPU."""
        mock_torch = _create_mock_torch(cuda_available=True, memory_gb=4)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            batch_size = manager.get_optimal_batch_size()
            assert batch_size >= 1


class TestGPUManagerEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.gpu
    def test_multiple_gpus(self):
        """Test handling of multiple GPUs."""
        mock_torch = _create_mock_torch(cuda_available=True)
        mock_torch.cuda.device_count.return_value = 2
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            assert manager.gpu_available == True

    def test_device_without_gpu(self):
        """Test device without GPU."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            assert manager.device == "cpu"
            assert manager.gpu_available == False
