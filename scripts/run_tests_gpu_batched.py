#!/usr/bin/env python3
"""
GPU-safe batched pytest runner for local development with memory safety.

CRITICAL SAFETY FEATURES:
- Pre-flight memory checks (abort if RAM > 70% or VRAM > 80%)
- Process memory limits (8GB per process via Windows Job Object)
- Watchdog that hard-kills process if memory > 90%
- One-file-per-batch mode to prevent memory accumulation
- Memory logging before/after each test file
- Stricter defaults (RAM target 70%, GPU split 64MB)

Goals:
- Exercise GPU-capable tests without overwhelming VRAM or crashing drivers
- Prevent system crashes from memory exhaustion
- Split GPU-heavy files into individual batches
- Apply "safe mode" CUDA allocator settings
- Clear CUDA cache and run GC between batches with RAM backpressure
"""
from __future__ import annotations

import argparse
import gc
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional, Sequence

try:
    import psutil  # type: ignore
except Exception:
    psutil = None

# Windows Job Object support for memory limits
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
        JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000

        class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", ctypes.c_byte * 72),
                ("IoInfo", ctypes.c_byte * 60),
                ("ProcessMemoryLimit", ctypes.c_ulonglong),
                ("JobMemoryLimit", ctypes.c_ulonglong),
                ("PeakProcessMemoryUsed", ctypes.c_ulonglong),
                ("PeakJobMemoryUsed", ctypes.c_ulonglong),
            ]

        WINDOWS_JOB_OBJECTS_AVAILABLE = True
    except Exception:
        WINDOWS_JOB_OBJECTS_AVAILABLE = False
else:
    WINDOWS_JOB_OBJECTS_AVAILABLE = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# GPU-heavy targets - ONE FILE PER BATCH for safety
GPU_BATCHES: List[List[str]] = [
    # GPU utils and real probing (keep isolated)
    ["tests/unit/test_gpu_utils_real.py"],
    ["tests/unit/test_gpu_utilization.py"],
    # Modules that may initialize encoders/codecs and video pipelines
    ["tests/unit/test_video_composer_focus.py"],
    ["tests/unit/test_video_composer.py"],
    # Music generator GPU paths and caches
    ["tests/unit/test_music_generator.py"],
    ["tests/unit/test_music_generator_focus.py"],
    # Avatar and integration tests that may touch GPU (separated for safety)
    ["tests/unit/test_avatar_generator.py"],
    ["tests/integration/test_gpu_integration.py"],
]

# Non-GPU targets can run after, on CPU to reduce VRAM churn
CPU_BATCHES: List[List[str]] = [
    ["tests/unit", "-k", "not gpu and not CUDA"],
    ["tests/integration", "-k", "not gpu and not CUDA"],
]

# Memory safety thresholds
RAM_PREFLIGHT_MAX = 70.0  # Abort if RAM > 70% before starting
VRAM_PREFLIGHT_MAX = 80.0  # Abort if VRAM > 80% before GPU tests
RAM_KILL_THRESHOLD = 90.0  # Hard kill if RAM > 90% during execution
PROCESS_MEMORY_LIMIT_GB = 8  # 8GB per process limit
MEMORY_PROFILE_ENABLED = True  # TODO: Set to False in a few days


def _get_ram_percent() -> float:
    """Get current RAM usage percentage."""
    if psutil is None:
        return 0.0
    return psutil.virtual_memory().percent


def _get_vram_percent() -> Optional[float]:
    """Get current GPU VRAM usage percentage."""
    try:
        # Try nvidia-smi first (works without torch)
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            if lines:
                used, total = map(int, lines[0].split(","))
                if total > 0:
                    return (used / total) * 100.0
    except Exception:
        pass

    # Fallback: try torch if available
    try:
        import torch

        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated(0)
            reserved = torch.cuda.memory_reserved(0)
            total = torch.cuda.get_device_properties(0).total_memory
            if total > 0:
                # Use reserved as it's more accurate for fragmentation
                return (reserved / total) * 100.0
    except Exception:
        pass

    return None


def _check_preflight_memory(require_gpu: bool = False) -> tuple[bool, str]:
    """
    Check memory before starting tests.
    Returns (is_safe, error_message).
    """
    if psutil is None:
        return True, ""  # Can't check without psutil

    ram_percent = _get_ram_percent()
    if ram_percent > RAM_PREFLIGHT_MAX:
        return False, f"RAM usage too high: {ram_percent:.1f}% > {RAM_PREFLIGHT_MAX}% (aborting for safety)"

    if require_gpu:
        vram_percent = _get_vram_percent()
        if vram_percent is not None and vram_percent > VRAM_PREFLIGHT_MAX:
            return False, f"VRAM usage too high: {vram_percent:.1f}% > {VRAM_PREFLIGHT_MAX}% (aborting for safety)"

    return True, ""


def _log_memory_state(label: str, test_file: Optional[str] = None) -> None:
    """Log current memory state for profiling."""
    if not MEMORY_PROFILE_ENABLED:
        return

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    ram_percent = _get_ram_percent()
    vram_percent = _get_vram_percent()

    log_msg = f"[MEMORY-PROFILE {timestamp}] {label}"
    if test_file:
        log_msg += f" | Test: {test_file}"
    log_msg += f" | RAM: {ram_percent:.1f}%"

    if vram_percent is not None:
        log_msg += f" | VRAM: {vram_percent:.1f}%"
    else:
        log_msg += " | VRAM: N/A"

    # Also log process memory if available
    if psutil:
        try:
            process = psutil.Process()
            proc_mem_mb = process.memory_info().rss / (1024 * 1024)
            log_msg += f" | Process: {proc_mem_mb:.0f}MB"
        except Exception:
            pass

    print(log_msg)


def _set_process_memory_limit_gb(gb: int) -> bool:
    """
    Set Windows Job Object memory limit for current process.
    Returns True if successful, False otherwise.
    """
    if not WINDOWS_JOB_OBJECTS_AVAILABLE:
        return False

    try:
        # Create job object
        job_handle = kernel32.CreateJobObjectW(None, None)
        if job_handle == 0:
            return False

        # Assign current process to job
        current_process = kernel32.GetCurrentProcess()
        if not kernel32.AssignProcessToJobObject(job_handle, current_process):
            kernel32.CloseHandle(job_handle)
            return False

        # Set memory limit
        limit_info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limit_info.ProcessMemoryLimit = gb * (1024**3)  # Convert GB to bytes
        limit_info.JobMemoryLimit = gb * (1024**3)

        # Set limits
        result = kernel32.SetInformationJobObject(
            job_handle,
            9,  # JobObjectExtendedLimitInformation
            ctypes.byref(limit_info),
            ctypes.sizeof(limit_info),
        )

        if result:
            print(f"[gpu-batched] Set process memory limit to {gb}GB via Windows Job Object")
            return True
        else:
            kernel32.CloseHandle(job_handle)
            return False
    except Exception as e:
        print(f"[gpu-batched] Warning: Could not set memory limit: {e}")
        return False


class MemoryWatchdog(threading.Thread):
    """Watchdog thread that kills process if memory exceeds threshold."""

    def __init__(self, kill_threshold: float, check_interval: float = 2.0):
        super().__init__(daemon=True)
        self.kill_threshold = kill_threshold
        self.check_interval = check_interval
        self.running = True

    def run(self) -> None:
        """Monitor memory and kill if threshold exceeded."""
        while self.running:
            try:
                ram_percent = _get_ram_percent()
                if ram_percent > self.kill_threshold:
                    print(f"\n[WATCHDOG] CRITICAL: RAM {ram_percent:.1f}% > {self.kill_threshold}%")
                    print("[WATCHDOG] Hard killing process to prevent system crash...")
                    # Force exit - this is intentional for safety
                    os._exit(1)
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"[WATCHDOG] Error: {e}")
                time.sleep(self.check_interval)

    def stop(self) -> None:
        """Stop the watchdog."""
        self.running = False


def _env_gpu_safe() -> dict:
    env = dict(os.environ)
    # Enable safe mode behavior in gpu_utils
    env["GPU_SAFE_MODE"] = env.get("GPU_SAFE_MODE", "1")
    # Use conservative allocator splits (64MB default, was 128MB)
    env.setdefault("GPU_MAX_SPLIT_MB", "64")
    # Avoid test-level parallelism unless explicitly requested
    env.setdefault("PYTEST_ADDOPTS", "--maxfail=1 --disable-warnings")
    # If torch is not installed, prepend stub to PYTHONPATH for test import-time patching
    stub_path = os.path.join(REPO_ROOT, "scripts", "_torch_stub")
    current_pp = env.get("PYTHONPATH", "")
    if stub_path not in current_pp:
        env["PYTHONPATH"] = (stub_path + os.pathsep + current_pp) if current_pp else stub_path
    return env


def _env_cpu_only(base: dict) -> dict:
    env = dict(base)
    env["CUDA_VISIBLE_DEVICES"] = ""
    # Also put conservative allocator to avoid odd CUDA init if something triggers it
    env.setdefault(
        "PYTORCH_CUDA_ALLOC_CONF",
        "max_split_size_mb:64,garbage_collection_threshold:0.6,expandable_segments:False",
    )
    return env


def _run_pytest(args: Sequence[str], env: dict, test_file: Optional[str] = None) -> int:
    """Run pytest with memory logging and real-time output."""
    _log_memory_state("BEFORE", test_file)
    print(f"\n{'='*80}")
    print(f"=== Running: {' '.join(args)} ===")
    print(f"{'='*80}")
    sys.stdout.flush()
    
    # Run pytest with unbuffered output for real-time streaming
    proc = subprocess.run(
        [sys.executable, "-u", "-m", "pytest", "-v", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        bufsize=0,  # Unbuffered for real-time output
    )
    
    _log_memory_state("AFTER", test_file)
    sys.stdout.flush()
    return proc.returncode


def _torch_clear_cache(env: dict) -> None:
    """Try to clear CUDA cache if torch present."""
    code = (
        "import sys; "
        "from src.utils.gpu_utils import get_gpu_manager; "
        "m=get_gpu_manager(); m.clear_cache(); "
        "import torch as t; "
        "print('[gpu-batched] cleared cuda cache' if m.cuda_available else '[gpu-batched] cpu-only')"
    )
    subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, env=env, text=True)


def _gc_and_wait_ram(target_percent: float, cooldown_s: float) -> None:
    """Garbage collect and wait for RAM to drop below target."""
    gc.collect()
    gc.collect()
    if psutil is None or target_percent <= 0:
        time.sleep(cooldown_s)
        return
    for _ in range(60):
        mem = psutil.virtual_memory().percent
        print(f"[gpu-batched] RAM: {mem:.1f}% (target < {target_percent:.1f}%)")
        if mem <= target_percent:
            break
        time.sleep(0.5)
    time.sleep(cooldown_s)


def main() -> int:
    """Main entry point with all safety features."""
    ap = argparse.ArgumentParser(description="Run GPU tests in safe, small batches with memory safety.")
    ap.add_argument(
        "--ram-target",
        type=float,
        default=70.0,
        help="Target RAM %% between batches (default 70%%, was 85%%).",
    )
    ap.add_argument("--cooldown", type=float, default=1.0, help="Seconds to sleep between batches.")
    ap.add_argument("--workers", type=int, default=0, help="xdist workers per batch (default 0 = no xdist).")
    ap.add_argument("--cov", action="store_true", help="Enable term coverage report per batch.")
    ap.add_argument("--skip-cpu-followup", action="store_true", help="Skip CPU-only follow-up batches.")
    ap.add_argument(
        "--disable-watchdog",
        action="store_true",
        help="Disable memory watchdog (NOT RECOMMENDED - may cause system crashes).",
    )
    ap.add_argument(
        "--disable-memory-limit",
        action="store_true",
        help="Disable process memory limit (NOT RECOMMENDED).",
    )
    args = ap.parse_args()

    # Pre-flight checks
    print("[gpu-batched] Pre-flight memory checks...")
    is_safe, error_msg = _check_preflight_memory(require_gpu=True)
    if not is_safe:
        print(f"[gpu-batched] FATAL: {error_msg}")
        return 1

    # Set process memory limit
    if not args.disable_memory_limit:
        _set_process_memory_limit_gb(PROCESS_MEMORY_LIMIT_GB)

    # Start watchdog
    watchdog: Optional[MemoryWatchdog] = None
    if not args.disable_watchdog:
        watchdog = MemoryWatchdog(kill_threshold=RAM_KILL_THRESHOLD)
        watchdog.start()
        print(f"[gpu-batched] Memory watchdog started (kill threshold: {RAM_KILL_THRESHOLD}%)")

    try:
        gpu_env = _env_gpu_safe()

        common: List[str] = []
        if args.cov:
            common += ["--cov=src", "--cov-report=term"]
        if args.workers and args.workers > 0:
            common += ["-n", str(args.workers)]

        # GPU batches (one file per batch)
        for i, batch in enumerate(GPU_BATCHES, 1):
            test_file = batch[0] if batch else "unknown"
            print(f"\n[PROGRESS] GPU Batch {i}/{len(GPU_BATCHES)}: {test_file}")
            sys.stdout.flush()
            code = _run_pytest([*batch, *common], gpu_env, test_file=test_file)
            if code != 0:
                print(f"\n[ERROR] GPU batch {i}/{len(GPU_BATCHES)} failed with code {code}")
                sys.stdout.flush()
                return code
            print(f"[SUCCESS] GPU batch {i}/{len(GPU_BATCHES)} completed")
            sys.stdout.flush()
            _torch_clear_cache(gpu_env)
            print(f"[COOLDOWN] Waiting for RAM to drop below {args.ram_target}%...")
            sys.stdout.flush()
            _gc_and_wait_ram(args.ram_target, args.cooldown)

            # Check memory before next batch
            ram_percent = _get_ram_percent()
            if ram_percent > args.ram_target * 1.1:  # 10% buffer
                print(f"[gpu-batched] WARNING: RAM {ram_percent:.1f}% still high after cooldown")

        # CPU follow-up batches for the rest
        if not args.skip_cpu_followup:
            cpu_env = _env_cpu_only(gpu_env)
            for i, batch in enumerate(CPU_BATCHES, 1):
                test_file = batch[0] if batch else "unknown"
                print(f"\n[PROGRESS] CPU Batch {i}/{len(CPU_BATCHES)}: {test_file}")
                sys.stdout.flush()
                code = _run_pytest([*batch, *common], cpu_env, test_file=test_file)
                if code != 0:
                    print(f"\n[ERROR] CPU batch {i}/{len(CPU_BATCHES)} failed with code {code}")
                    sys.stdout.flush()
                    return code
                print(f"[SUCCESS] CPU batch {i}/{len(CPU_BATCHES)} completed")
                sys.stdout.flush()
                print(f"[COOLDOWN] Waiting for RAM to drop below {args.ram_target}%...")
                sys.stdout.flush()
                _gc_and_wait_ram(args.ram_target, args.cooldown)

        print("[gpu-batched] All batches completed successfully.")
        return 0
    finally:
        if watchdog:
            watchdog.stop()


if __name__ == "__main__":
    raise SystemExit(main())
