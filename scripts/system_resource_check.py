"""Quick system resource sampler to prevent overload during heavy test runs."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from typing import List

try:
    import psutil  # type: ignore
except ImportError:  # pragma: no cover - psutil is an optional dependency
    print("psutil not installed; skipping resource sampling.")
    sys.exit(0)


INTERVAL_SECONDS = 5
TOTAL_DURATION = 30
OVERLOAD_THRESHOLD = 95.0
OVERLOAD_WINDOW = 10  # seconds


def main() -> None:
    overload_accumulator = 0
    for _ in range(TOTAL_DURATION // INTERVAL_SECONDS):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        gpu_loads = _query_gpu_loads()

        print(
            f"[resource-check] CPU: {cpu:.1f}% | RAM: {mem:.1f}%"
            + (" | GPU: " + ", ".join(f"{g:.1f}%" for g in gpu_loads) if gpu_loads else " | GPU: N/A")
        )

        if _is_overloaded(cpu, mem, gpu_loads):
            overload_accumulator += INTERVAL_SECONDS
        else:
            overload_accumulator = 0

        if overload_accumulator >= OVERLOAD_WINDOW:
            print(
                "System near overload—reduce PY_PARALLEL or PY_GPU_MAX_LOAD "
                "before continuing heavy workloads."
            )
            break

        time.sleep(INTERVAL_SECONDS)


def _is_overloaded(cpu: float, mem: float, gpu_loads: List[float]) -> bool:
    if cpu >= OVERLOAD_THRESHOLD or mem >= OVERLOAD_THRESHOLD:
        return True
    return any(load >= OVERLOAD_THRESHOLD for load in gpu_loads)


def _query_gpu_loads() -> List[float]:
    if shutil.which("nvidia-smi") is None:
        return []

    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception:
        return []

    loads: List[float] = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            loads.append(float(line))
        except ValueError:
            continue
    return loads


if __name__ == "__main__":
    main()

