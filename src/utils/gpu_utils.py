"""
GPU Utilities - Detection and Optimization
Handles GPU detection and configuration for maximum performance
"""

import os
from typing import Any, Dict


class GPUManager:
    """Manage GPU detection and optimization settings."""

    def __init__(self):
        self.gpu_available = False
        self.gpu_name: str | None = None
        self.gpu_memory: float = 0.0
        self.device = "cpu"
        self.cuda_available = False
        self.device_id = 0

        self._detect_gpu()

    def _detect_gpu(self):
        """Detect GPU availability and capabilities."""
        try:
            import torch

            if torch.cuda.is_available():
                self.cuda_available = True
                self.gpu_available = True
                self.device = "cuda"
                self.device_id = 0

                # Get GPU info
                self.gpu_name = torch.cuda.get_device_name(0)
                self.gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB

                # Enable cudnn optimizations
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.enabled = True

                # Set memory growth to avoid OOM
                torch.cuda.empty_cache()

                print(f"✓ GPU Detected: {self.gpu_name} ({self.gpu_memory:.1f} GB)")
                print(f"✓ CUDA Version: {torch.version.cuda}")
                print(f"✓ cuDNN Enabled: {torch.backends.cudnn.enabled}")

            else:
                print("⚠ No CUDA GPU detected, using CPU")
                self.device = "cpu"

        except ImportError:
            print("⚠ PyTorch not installed, GPU detection unavailable")
            self.device = "cpu"

    def get_device(self) -> str:
        """Get the device string for model placement."""
        return self.device

    def get_torch_device(self):
        """Get torch device object."""
        try:
            import torch

            return torch.device(self.device)
        except ImportError:
            return "cpu"

    def optimize_for_inference(self):
        """Apply inference-specific optimizations."""
        if not self.cuda_available:
            return

        try:
            import torch

            # Enable TF32 for better performance on Ampere+ GPUs
            if torch.cuda.get_device_capability()[0] >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                print("✓ TF32 enabled for Ampere+ GPU")

            # Set optimal memory allocation
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

        except Exception as e:
            print(f"⚠ Could not apply inference optimizations: {e}")

    def get_optimal_batch_size(self, task: str = "tts") -> int:
        """Get optimal batch size based on GPU memory."""
        if not self.gpu_available:
            return 1

        # Conservative estimates based on VRAM
        if task == "tts":
            if self.gpu_memory >= 12:
                return 4
            elif self.gpu_memory >= 8:
                return 2
            else:
                return 1
        elif task == "avatar":
            if self.gpu_memory >= 12:
                return 2
            else:
                return 1
        elif task == "music":
            if self.gpu_memory >= 16:
                return 2
            else:
                return 1

        return 1

    def get_performance_config(self) -> Dict[str, Any]:
        """Get optimized configuration based on GPU capabilities."""
        config = {
            "device": self.device,
            "gpu_available": self.gpu_available,
            "gpu_name": self.gpu_name,
            "gpu_memory_gb": self.gpu_memory,
            "use_fp16": False,
            "use_tf32": False,
            "batch_size": 1,
            "num_workers": 4,
        }

        if self.gpu_available:
            # Enable FP16 for GPUs with Tensor Cores (compute capability >= 7.0)
            try:
                import torch

                compute_cap = torch.cuda.get_device_capability()

                if compute_cap[0] >= 7:
                    config["use_fp16"] = True
                    print("✓ FP16 (Mixed Precision) enabled")

                if compute_cap[0] >= 8:
                    config["use_tf32"] = True

                # Set optimal worker count
                config["num_workers"] = min(8, os.cpu_count() or 4)

            except Exception as e:
                print(f"⚠ Could not determine compute capability: {e}")

        return config

    def clear_cache(self):
        """Clear GPU cache to free memory."""
        if self.cuda_available:
            try:
                import torch

                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            except Exception:
                pass

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current GPU memory usage."""
        if not self.cuda_available:
            return {"allocated": 0, "reserved": 0, "free": 0}

        try:
            import torch

            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            reserved = torch.cuda.memory_reserved(0) / (1024**3)
            free = self.gpu_memory - allocated

            return {"allocated_gb": allocated, "reserved_gb": reserved, "free_gb": free, "total_gb": self.gpu_memory}
        except Exception:
            return {"allocated": 0, "reserved": 0, "free": 0}

    def set_device(self, device_id: int = 0):
        """Set active GPU device."""
        if self.cuda_available:
            try:
                import torch

                torch.cuda.set_device(device_id)
                self.device_id = device_id
                self.device = f"cuda:{device_id}"
            except Exception as e:
                print(f"⚠ Could not set device {device_id}: {e}")


# Global GPU manager instance
_gpu_manager = None


def get_gpu_manager() -> GPUManager:
    """Get or create global GPU manager instance."""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUManager()
        _gpu_manager.optimize_for_inference()
    return _gpu_manager


def is_gpu_available() -> bool:
    """Quick check if GPU is available."""
    return get_gpu_manager().gpu_available


def get_device() -> str:
    """Get device string (cuda or cpu)."""
    return get_gpu_manager().get_device()


def get_performance_config() -> Dict[str, Any]:
    """Get performance configuration."""
    return get_gpu_manager().get_performance_config()


def print_gpu_info():
    """Print detailed GPU information."""
    manager = get_gpu_manager()

    print("\n" + "=" * 60)
    print("GPU CONFIGURATION")
    print("=" * 60)

    if manager.gpu_available:
        print(f"Device: {manager.gpu_name}")
        print(f"VRAM: {manager.gpu_memory:.1f} GB")
        print(f"CUDA Device: {manager.device}")

        config = manager.get_performance_config()
        print(f"FP16 (Mixed Precision): {'Enabled' if config['use_fp16'] else 'Disabled'}")
        print(f"TF32: {'Enabled' if config['use_tf32'] else 'Disabled'}")

        mem = manager.get_memory_usage()
        print("\nMemory Usage:")
        print(f"  Allocated: {mem['allocated_gb']:.2f} GB")
        print(f"  Free: {mem['free_gb']:.2f} GB")

    else:
        print("Status: CPU Only (No GPU detected)")
        print("Note: GPU acceleration unavailable")

    print("=" * 60 + "\n")
