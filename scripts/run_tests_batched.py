#!/usr/bin/env python3
"""
Run the test suite in smaller batches to lower peak memory usage.

Features:
- Splits tests into logical batches (unit, integration, e2e optional)
- Forces CPU-only execution to avoid CUDA/driver allocations on local runs
- Triggers frequent GC between batches and optionally waits until RAM < threshold
- Propagates non-zero exit codes on failures
"""
from __future__ import annotations

import argparse
import gc
import os
import subprocess
import sys
import time
from typing import List, Sequence

try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # psutil is optional; we degrade gracefully

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env_cpu_only() -> dict:
    env = dict(os.environ)
    # Disable CUDA usage
    env["CUDA_VISIBLE_DEVICES"] = ""
    # Be conservative with PyTorch allocator if present
    env["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64,garbage_collection_threshold:0.6,expandable_segments:False"
    # Make allocations more release-friendly in CPython
    env.setdefault("PYTHONMALLOC", "malloc")
    # Keep pytest quiet-ish but show failures quickly
    env.setdefault("PYTEST_ADDOPTS", "--maxfail=1 --disable-warnings")
    return env


def _run_pytest_batch(args: Sequence[str], env: dict) -> int:
    print(f"\n=== Running batch: {' '.join(args)} ===")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
    )
    return proc.returncode


def _gc_and_wait_ram(target_percent: float, cooldown_s: float) -> None:
    # Aggressive GC
    gc.collect()
    gc.collect()
    # Optional backpressure using psutil if available
    if psutil is None or target_percent <= 0:
        time.sleep(cooldown_s)
        return
    for _ in range(60):  # up to ~60 * 0.5s = 30s wait
        mem = psutil.virtual_memory().percent
        print(f"[batched-tests] RAM: {mem:.1f}% (target < {target_percent:.1f}%)")
        if mem <= target_percent:
            break
        time.sleep(0.5)
    # short cooldown regardless
    time.sleep(cooldown_s)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run pytest in memory-friendly batches.")
    parser.add_argument(
        "--ram-target",
        type=float,
        default=80.0,
        help="Wait until RAM percent is below this threshold between batches (requires psutil).",
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=1.0,
        help="Seconds to sleep between batches (in addition to RAM waiting).",
    )
    parser.add_argument(
        "--include-e2e",
        action="store_true",
        help="Include e2e tests as a final batch.",
    )
    parser.add_argument(
        "--cov",
        action="store_true",
        help="Enable per-batch coverage reporting (term summary).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Number of xdist workers per batch (0 disables xdist).",
    )
    opts = parser.parse_args()

    env = _env_cpu_only()

    common_args: List[str] = []
    if opts.cov:
        # Lightweight, module-level coverage to avoid heavy source scanning
        common_args += ["--cov=src", "--cov-report=term"]

    if opts.workers and opts.workers > 0:
        common_args += ["-n", str(opts.workers)]

    # Order matters for resource profile: unit → integration → (optional) e2e
    batches: List[List[str]] = [
        ["tests/unit"],
        ["tests/integration"],
    ]
    if opts.include_e2e:
        batches.append(["tests/e2e"])

    # Execute batches
    for i, batch in enumerate(batches, 1):
        batch_args = [*batch, *common_args]
        code = _run_pytest_batch(batch_args, env)
        if code != 0:
            print(f"\n[batched-tests] Batch {i}/{len(batches)} failed with exit code {code}. Stopping.")
            return code
        _gc_and_wait_ram(opts.ram_target, opts.cooldown)

    print("\n[batched-tests] All batches completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


