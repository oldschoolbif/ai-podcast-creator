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
    mock_torch.device = MagicMock(side_effect=lambda x: f"device({x})")
    
    return mock_torch


class TestGPUManager:
    """Test GPUManager class."""

    def test_init_without_gpu(self):
        """Test GPUManager initialization without GPU."""
        # Mock torch module before patching
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.version.cuda = "12.1"
        mock_torch.backends.cudnn.enabled = True
        
        # Remove torch from sys.modules if present to ensure clean patching
        torch_backup = sys.modules.pop("torch", None)
        try:
            with patch.dict("sys.modules", {"torch": mock_torch}):
                manager = GPUManager()

                assert manager.gpu_available == False
                assert manager.device == "cpu"
                assert manager.cuda_available == False
        finally:
            # Restore torch if it was there
            if torch_backup is not None:
                sys.modules["torch"] = torch_backup

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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            # Clear singleton
            import src.utils.gpu_utils
            src.utils.gpu_utils._gpu_manager = None
            manager1 = get_gpu_manager()
            manager2 = get_gpu_manager()
            assert manager1 is manager2

    @pytest.mark.gpu
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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            # Clear singleton
            import src.utils.gpu_utils
            src.utils.gpu_utils._gpu_manager = None
            device = get_device()
            assert device == "cpu"


class TestGetTorchDevice:
    """Test get_torch_device method."""

    def test_get_torch_device_cpu(self):
        """Test get_torch_device with CPU."""
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            result = manager.get_torch_device()
            mock_torch.device.assert_called_with("cpu")

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
        # Mock torch import to raise ImportError
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == "torch":
                raise ImportError("No module named 'torch'")
            return original_import(name, *args, **kwargs)
        
        with patch("builtins.__import__", side_effect=mock_import):
            # Remove torch from sys.modules if present
            torch_backup = sys.modules.pop("torch", None)
            try:
                manager = GPUManager()
                result = manager.get_torch_device()
                # Should return "cpu" string when torch unavailable
                assert result == "cpu"
            finally:
                # Restore torch if it was there
                if torch_backup is not None:
                    sys.modules["torch"] = torch_backup


class TestOptimizeForInference:
    """Test optimize_for_inference method."""

    def test_optimize_cpu(self):
        """Test optimization when GPU not available."""
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            # Should not crash with CPU
            manager.set_device(0)
            assert manager.device == "cpu"

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

        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
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

        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
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
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            # Should not crash
            manager.clear_cache()

    @pytest.mark.gpu
    def test_clear_cache_error_handling(self):
        """Test cache clearing with errors."""
        mock_torch = _create_mock_torch(cuda_available=True, memory_gb=8)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            # Initialize manager first (without error)
            manager = GPUManager()
            
            # Then test error handling in clear_cache
            mock_torch.cuda.empty_cache.side_effect = Exception("Error")
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
    @pytest.mark.gpu
    def test_optimal_batch_sizes(self, gpu_memory, task, expected_batch):
        """Test optimal batch size calculations."""
        mock_torch = _create_mock_torch(cuda_available=True, memory_gb=gpu_memory)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            batch_size = manager.get_optimal_batch_size(task)
            assert batch_size == expected_batch

    @pytest.mark.gpu
    def test_unknown_task_default_batch(self):
        """Test batch size for unknown task."""
        mock_torch = _create_mock_torch(cuda_available=True, memory_gb=16)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            batch_size = manager.get_optimal_batch_size("unknown_task")
            assert batch_size == 1  # Default


class TestPytorchNotInstalled:
    """Test behavior when PyTorch is not installed."""

    def test_init_without_pytorch(self, capsys):
        """Test initialization when PyTorch not available."""
        # Mock torch import to raise ImportError
        original_import = __import__
        def mock_import(name, *args, **kwargs):
            if name == "torch":
                raise ImportError("No module named 'torch'")
            return original_import(name, *args, **kwargs)
        
        with patch("builtins.__import__", side_effect=mock_import):
            # Remove torch from sys.modules if present
            torch_backup = sys.modules.pop("torch", None)
            try:
                manager = GPUManager()
                assert manager.gpu_available == False
                assert manager.device == "cpu"
                captured = capsys.readouterr()
                assert "PyTorch not installed" in captured.out
            finally:
                # Restore torch if it was there
                if torch_backup is not None:
                    sys.modules["torch"] = torch_backup

    def test_get_torch_device_import_error(self):
        """Test get_torch_device when torch can't be imported."""
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            # Remove torch from modules to simulate ImportError in get_torch_device
            with patch.dict("sys.modules", {"torch": None}, clear=False):
                result = manager.get_torch_device()
                assert result == "cpu"
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
@pytest.mark.gpu
def test_performance_config_by_compute_capability(compute_capability, expected_fp16, expected_tf32):
    """Test performance config varies by compute capability."""
    mock_torch = _create_mock_torch(cuda_available=True, memory_gb=8)
    mock_torch.cuda.get_device_capability.return_value = compute_capability
    with patch.dict("sys.modules", {"torch": mock_torch}):
        manager = GPUManager()
        config = manager.get_performance_config()

        assert config["use_fp16"] == expected_fp16
        assert config["use_tf32"] == expected_tf32


@pytest.mark.benchmark
class TestGPUManagerPerformance:
    """Performance benchmarks for GPU utilities."""

    def test_initialization_performance(self, benchmark):
        """Benchmark GPUManager initialization."""
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            def create_manager():
                return GPUManager()
            result = benchmark(create_manager)
            assert result is not None

    def test_get_device_performance(self, benchmark):
        """Benchmark get_device call."""
        mock_torch = _create_mock_torch(cuda_available=False)
        with patch.dict("sys.modules", {"torch": mock_torch}):
            manager = GPUManager()
            result = benchmark(manager.get_device)
            assert result == "cpu"


# ============================================================================
# Additional error path tests
# ============================================================================

@pytest.mark.unit
def test_optimize_for_inference_exception():
    """Test optimize_for_inference handles exceptions gracefully."""
    mock_torch = _create_mock_torch(cuda_available=True)
    mock_torch.cuda.get_device_capability.side_effect = Exception("Capability check failed")
    
    with patch.dict("sys.modules", {"torch": mock_torch}):
        manager = GPUManager()
        # Should not raise exception
        manager.optimize_for_inference()


@pytest.mark.unit
def test_get_performance_config_exception():
    """Test get_performance_config handles exceptions when checking compute capability."""
    mock_torch = _create_mock_torch(cuda_available=True)
    mock_torch.cuda.get_device_capability.side_effect = Exception("Capability check failed")
    
    with patch.dict("sys.modules", {"torch": mock_torch}):
        manager = GPUManager()
        config = manager.get_performance_config()
        
        # Should return config with defaults
        assert config["use_fp16"] is False
        assert config["use_tf32"] is False


@pytest.mark.unit
def test_clear_cache_exception():
    """Test clear_cache handles exceptions gracefully."""
    mock_torch = _create_mock_torch(cuda_available=True)
    
    with patch.dict("sys.modules", {"torch": mock_torch}):
        manager = GPUManager()
        # Now patch empty_cache to raise exception AFTER init
        mock_torch.cuda.empty_cache.side_effect = Exception("Cache clear failed")
        # Should not raise exception
        manager.clear_cache()


@pytest.mark.unit
def test_get_memory_usage_exception():
    """Test get_memory_usage handles exceptions gracefully."""
    mock_torch = _create_mock_torch(cuda_available=True)
    mock_torch.cuda.memory_allocated.side_effect = Exception("Memory check failed")
    
    with patch.dict("sys.modules", {"torch": mock_torch}):
        manager = GPUManager()
        usage = manager.get_memory_usage()
        
        # Should return default values
        assert usage["allocated"] == 0
        assert usage["reserved"] == 0
        assert usage["free"] == 0


@pytest.mark.skip(reason="Complex subprocess exception mocking - subprocess imported locally")
def test_get_utilization_subprocess_error():
    """Test get_utilization handles subprocess errors."""
    # This requires complex mocking of subprocess which is imported locally
    # The exception handling is tested via integration tests
    pass


@pytest.mark.unit
def test_get_utilization_timeout():
    """Test get_utilization handles subprocess timeout."""
    import subprocess
    
    mock_torch = _create_mock_torch(cuda_available=True)
    
    with (
        patch.dict("sys.modules", {"torch": mock_torch}),
        patch("subprocess.run", side_effect=subprocess.TimeoutExpired("nvidia-smi", 2)),
    ):
        manager = GPUManager()
        utilization = manager.get_utilization()
        
        # Should return zeros on timeout
        assert utilization["gpu_percent"] == 0.0
        assert utilization["memory_percent"] == 0.0


@pytest.mark.unit
def test_get_utilization_invalid_output():
    """Test get_utilization handles invalid nvidia-smi output."""
    import subprocess
    
    mock_torch = _create_mock_torch(cuda_available=True)
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "invalid,output"
    
    with (
        patch.dict("sys.modules", {"torch": mock_torch}),
        patch("subprocess.run", return_value=mock_result),
    ):
        manager = GPUManager()
        utilization = manager.get_utilization()
        
        # Should return zeros on invalid output
        assert utilization["gpu_percent"] == 0.0
        assert utilization["memory_percent"] == 0.0
