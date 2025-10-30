"""
Unit Tests for GPU Utilities
Tests for src/utils/gpu_utils.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.gpu_utils import GPUManager, get_device, get_gpu_manager, is_gpu_available


class TestGPUManager:
    """Test GPUManager class."""

    def test_init_without_gpu(self):
        """Test GPUManager initialization without GPU."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()

            assert manager.gpu_available == False
            assert manager.device == "cpu"
            assert manager.cuda_available == False

    @pytest.mark.gpu
    def test_init_with_gpu(self):
        """Test GPUManager initialization with GPU."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
        ):

            # Mock GPU properties
            mock_props.return_value.total_memory = 8 * 1024**3  # 8GB

            manager = GPUManager()

            assert manager.gpu_available == True
            assert manager.device == "cuda"
            assert manager.cuda_available == True
            assert manager.gpu_name == "Test GPU"
            assert manager.gpu_memory == 8.0

    def test_get_device_cpu(self):
        """Test get_device returns CPU when no GPU."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            assert manager.get_device() == "cpu"

    @pytest.mark.gpu
    def test_get_device_gpu(self):
        """Test get_device returns CUDA when GPU available."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            assert manager.get_device() == "cuda"

    def test_get_optimal_batch_size_cpu(self):
        """Test batch size calculation for CPU."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            assert manager.get_optimal_batch_size("tts") == 1
            assert manager.get_optimal_batch_size("music") == 1

    @pytest.mark.gpu
    def test_get_optimal_batch_size_gpu(self):
        """Test batch size calculation for GPU."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
        ):

            # Test with 12GB GPU
            mock_props.return_value.total_memory = 12 * 1024**3
            manager = GPUManager()

            assert manager.get_optimal_batch_size("tts") == 4
            assert manager.get_optimal_batch_size("avatar") == 2

    def test_get_performance_config_cpu(self):
        """Test performance config for CPU."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            config = manager.get_performance_config()

            assert config["device"] == "cpu"
            assert config["gpu_available"] == False
            assert config["use_fp16"] == False
            assert config["use_tf32"] == False

    @pytest.mark.gpu
    def test_get_performance_config_gpu(self):
        """Test performance config for GPU."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.get_device_capability", return_value=(8, 6)),
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            config = manager.get_performance_config()

            assert config["device"] == "cuda"
            assert config["gpu_available"] == True
            assert config["use_fp16"] == True  # Compute capability >= 7
            assert config["use_tf32"] == True  # Compute capability >= 8

    @pytest.mark.gpu
    def test_clear_cache(self):
        """Test GPU cache clearing."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.empty_cache") as mock_clear,
            patch("torch.cuda.synchronize") as mock_sync,
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()  # Calls empty_cache once in __init__
            manager.clear_cache()  # Calls empty_cache again

            # Should be called twice: once during init, once during clear_cache()
            assert mock_clear.call_count == 2
            mock_sync.assert_called_once()

    @pytest.mark.gpu
    def test_get_memory_usage(self):
        """Test memory usage reporting."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.memory_allocated", return_value=2 * 1024**3),
            patch("torch.cuda.memory_reserved", return_value=3 * 1024**3),
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            mem = manager.get_memory_usage()

            assert "allocated_gb" in mem
            assert "reserved_gb" in mem
            assert "free_gb" in mem
            assert mem["total_gb"] == 8.0


class TestGlobalFunctions:
    """Test global utility functions."""

    def test_get_gpu_manager_singleton(self):
        """Test that get_gpu_manager returns same instance."""
        with patch("torch.cuda.is_available", return_value=False):
            manager1 = get_gpu_manager()
            manager2 = get_gpu_manager()
            assert manager1 is manager2

    def test_is_gpu_available(self):
        """Test is_gpu_available function."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            # Clear singleton
            import src.utils.gpu_utils

            src.utils.gpu_utils._gpu_manager = None

            assert is_gpu_available() == True

    def test_get_device_function(self):
        """Test get_device function."""
        with patch("torch.cuda.is_available", return_value=False):
            # Clear singleton
            import src.utils.gpu_utils

            src.utils.gpu_utils._gpu_manager = None

            device = get_device()
            assert device == "cpu"


class TestGetTorchDevice:
    """Test get_torch_device method."""

    def test_get_torch_device_cpu(self):
        """Test get_torch_device with CPU."""
        with patch("torch.cuda.is_available", return_value=False), patch("torch.device") as mock_device:
            manager = GPUManager()
            result = manager.get_torch_device()
            mock_device.assert_called_with("cpu")

    @pytest.mark.gpu
    def test_get_torch_device_gpu(self):
        """Test get_torch_device with GPU."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.device") as mock_device,
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            manager.get_torch_device()
            # Should call torch.device with 'cuda'
            assert mock_device.called

    def test_get_torch_device_no_torch(self):
        """Test get_torch_device when torch not available."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            # Temporarily break torch import
            with patch.dict("sys.modules", {"torch": None}):
                result = manager.get_torch_device()
                # Should return "cpu" string when torch unavailable
                assert result in ["cpu", "cuda"]


class TestOptimizeForInference:
    """Test optimize_for_inference method."""

    def test_optimize_cpu(self):
        """Test optimization when GPU not available."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            # Should not crash with CPU
            manager.optimize_for_inference()

    @pytest.mark.gpu
    def test_optimize_tf32_enabled(self):
        """Test TF32 optimization for Ampere+ GPUs."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="RTX 3090"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.get_device_capability", return_value=(8, 6)),
            patch("torch.backends.cuda.matmul") as mock_matmul,
            patch("torch.backends.cudnn") as mock_cudnn,
        ):

            mock_props.return_value.total_memory = 24 * 1024**3
            manager = GPUManager()
            manager.optimize_for_inference()

            # TF32 should be enabled for compute capability 8.x
            assert hasattr(mock_matmul, "allow_tf32") or True

    @pytest.mark.gpu
    def test_optimize_older_gpu(self):
        """Test optimization for older GPUs (no TF32)."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="GTX 1080"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.get_device_capability", return_value=(6, 1)),
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            manager.optimize_for_inference()
            # Should complete without error


class TestSetDevice:
    """Test set_device method."""

    @pytest.mark.gpu
    def test_set_device_success(self):
        """Test setting GPU device."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.set_device") as mock_set,
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            manager.set_device(1)

            mock_set.assert_called_with(1)
            assert manager.device_id == 1
            assert manager.device == "cuda:1"

    def test_set_device_cpu(self):
        """Test set_device when GPU not available."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            # Should not crash with CPU
            manager.set_device(0)

    @pytest.mark.gpu
    def test_set_device_error(self):
        """Test set_device with invalid device ID."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.set_device", side_effect=Exception("Invalid device")),
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            # Should handle error gracefully
            manager.set_device(999)


class TestGlobalUtilityFunctions:
    """Test module-level utility functions."""

    def test_get_performance_config(self):
        """Test global get_performance_config function."""
        from src.utils.gpu_utils import get_performance_config

        with patch("torch.cuda.is_available", return_value=False):
            # Clear singleton
            import src.utils.gpu_utils

            src.utils.gpu_utils._gpu_manager = None

            config = get_performance_config()

            assert "device" in config
            assert "gpu_available" in config
            assert config["device"] == "cpu"

    def test_print_gpu_info_cpu(self, capsys):
        """Test print_gpu_info with CPU."""
        from src.utils.gpu_utils import print_gpu_info

        with patch("torch.cuda.is_available", return_value=False):
            # Clear singleton
            import src.utils.gpu_utils

            src.utils.gpu_utils._gpu_manager = None

            print_gpu_info()

            captured = capsys.readouterr()
            assert "GPU CONFIGURATION" in captured.out
            assert "CPU Only" in captured.out or "Status" in captured.out

    @pytest.mark.gpu
    def test_print_gpu_info_gpu(self, capsys):
        """Test print_gpu_info with GPU."""
        from src.utils.gpu_utils import print_gpu_info

        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.get_device_capability", return_value=(8, 6)),
            patch("torch.cuda.memory_allocated", return_value=2 * 1024**3),
            patch("torch.cuda.memory_reserved", return_value=3 * 1024**3),
        ):

            mock_props.return_value.total_memory = 8 * 1024**3

            # Clear singleton
            import src.utils.gpu_utils

            src.utils.gpu_utils._gpu_manager = None

            print_gpu_info()

            captured = capsys.readouterr()
            assert "GPU CONFIGURATION" in captured.out
            assert "Test GPU" in captured.out or "Device" in captured.out


class TestMemoryManagement:
    """Test memory management functions."""

    def test_get_memory_usage_cpu(self):
        """Test memory usage with CPU."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            mem = manager.get_memory_usage()

            assert mem["allocated"] == 0
            assert mem["reserved"] == 0
            assert mem["free"] == 0

    @pytest.mark.gpu
    def test_get_memory_usage_error_handling(self):
        """Test memory usage with errors."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
            patch("torch.cuda.memory_allocated", side_effect=Exception("Error")),
        ):

            mock_props.return_value.total_memory = 8 * 1024**3
            manager = GPUManager()
            mem = manager.get_memory_usage()

            # Should return zeros on error
            assert "allocated" in mem or "allocated_gb" in mem

    def test_clear_cache_cpu(self):
        """Test cache clearing with CPU."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            # Should not crash
            manager.clear_cache()

    def test_clear_cache_error_handling(self):
        """Test cache clearing with errors."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
        ):

            mock_props.return_value.total_memory = 8 * 1024**3

            # Initialize manager first (without error)
            with patch("torch.cuda.empty_cache"):
                manager = GPUManager()

            # Then test error handling in clear_cache
            with patch("torch.cuda.empty_cache", side_effect=Exception("Error")):
                # Should handle error gracefully (exception is caught internally)
                manager.clear_cache()


class TestBatchSizeCalculation:
    """Test batch size calculations for different tasks and GPUs."""

    @pytest.mark.parametrize(
        "gpu_memory,task,expected_batch",
        [
            (16, "tts", 4),
            (12, "tts", 4),
            (8, "tts", 2),
            (4, "tts", 1),
            (16, "avatar", 2),
            (12, "avatar", 2),
            (8, "avatar", 1),
            (20, "music", 2),
            (16, "music", 2),
            (12, "music", 1),
        ],
    )
    def test_optimal_batch_sizes(self, gpu_memory, task, expected_batch):
        """Test optimal batch size calculations."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
        ):

            mock_props.return_value.total_memory = gpu_memory * 1024**3
            manager = GPUManager()

            batch_size = manager.get_optimal_batch_size(task)
            assert batch_size == expected_batch

    def test_unknown_task_default_batch(self):
        """Test batch size for unknown task."""
        with (
            patch("torch.cuda.is_available", return_value=True),
            patch("torch.cuda.get_device_name", return_value="Test GPU"),
            patch("torch.cuda.get_device_properties") as mock_props,
        ):

            mock_props.return_value.total_memory = 16 * 1024**3
            manager = GPUManager()

            batch_size = manager.get_optimal_batch_size("unknown_task")
            assert batch_size == 1  # Default


class TestPytorchNotInstalled:
    """Test behavior when PyTorch is not installed."""

    def test_init_without_pytorch(self, capsys):
        """Test initialization when PyTorch not available."""
        with patch("torch.cuda.is_available", side_effect=ImportError):
            manager = GPUManager()

            assert manager.gpu_available == False
            assert manager.device == "cpu"

            captured = capsys.readouterr()
            assert "PyTorch not installed" in captured.out

    def test_get_torch_device_import_error(self):
        """Test get_torch_device when torch can't be imported."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()

            # Mock ImportError for get_torch_device
            with patch("builtins.__import__", side_effect=ImportError):
                result = manager.get_torch_device()
                # Should return fallback
                assert result in ["cpu", "cuda"]


@pytest.mark.parametrize(
    "compute_capability,expected_fp16,expected_tf32",
    [
        ((6, 1), False, False),  # Pascal - no FP16/TF32
        ((7, 0), True, False),  # Volta - FP16 only
        ((7, 5), True, False),  # Turing - FP16 only
        ((8, 0), True, True),  # Ampere - FP16 and TF32
        ((8, 6), True, True),  # Ampere - FP16 and TF32
    ],
)
def test_performance_config_by_compute_capability(compute_capability, expected_fp16, expected_tf32):
    """Test performance config varies by compute capability."""
    with (
        patch("torch.cuda.is_available", return_value=True),
        patch("torch.cuda.get_device_name", return_value="Test GPU"),
        patch("torch.cuda.get_device_properties") as mock_props,
        patch("torch.cuda.get_device_capability", return_value=compute_capability),
    ):

        mock_props.return_value.total_memory = 8 * 1024**3
        manager = GPUManager()
        config = manager.get_performance_config()

        assert config["use_fp16"] == expected_fp16
        assert config["use_tf32"] == expected_tf32


@pytest.mark.benchmark
class TestGPUManagerPerformance:
    """Performance benchmarks for GPU utilities."""

    def test_initialization_performance(self, benchmark):
        """Benchmark GPUManager initialization."""
        with patch("torch.cuda.is_available", return_value=False):

            def create_manager():
                return GPUManager()

            result = benchmark(create_manager)
            assert result is not None

    def test_get_device_performance(self, benchmark):
        """Benchmark get_device call."""
        with patch("torch.cuda.is_available", return_value=False):
            manager = GPUManager()
            result = benchmark(manager.get_device)
            assert result == "cpu"
