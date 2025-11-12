"""Deterministic pytest wrapper for mutmut with dynamic exclusions."""

from __future__ import annotations

import math
import os
import subprocess
import sys
from pathlib import Path
from typing import List


PYTEST_FLAGS = ["-q", "--maxfail=1", "--tb=short"]
GPU_ENV = "PY_ENABLE_GPU_TESTS"
PARALLEL_ENV = "PY_PARALLEL"
SAFE_CORES_ENV = "PY_SAFE_CORES"
RESOURCE_MONITOR_ENV = "PY_MONITOR_RESOURCES"
TARGETS_ENV = "PYTEST_TARGETS"
SCRIPT_DIR = Path(__file__).resolve().parent


def _build_command() -> list[str]:
    cmd: List[str] = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        _marker_expression(),
    ]
    cmd.extend(_parallel_args())
    cmd.extend(_target_args())
    cmd.extend(PYTEST_FLAGS)
    return cmd


def _prepare_env() -> dict[str, str]:
    env = os.environ.copy()
    project_root = Path(__file__).resolve().parent.parent
    existing = env.get("PYTHONPATH")
    path_parts = [str(project_root)]
    if existing:
        path_parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(path_parts)
    return env


def main() -> int:
    env = _prepare_env()
    _maybe_run_resource_check(env)
    cmd = _build_command()
    result = subprocess.run(cmd, env=env)
    return result.returncode


def _marker_expression() -> str:
    parts: List[str] = ["not slow", "not integration", "not e2e", "not performance"]
    if os.getenv(GPU_ENV, "0") != "1":
        parts.append("not gpu")
    return " and ".join(parts)


def _parallel_args() -> list[str]:
    if os.getenv(PARALLEL_ENV, "1") == "0":
        return []

    safe_value = os.getenv(SAFE_CORES_ENV)
    safe = None
    if safe_value:
        try:
            safe = int(safe_value)
        except ValueError:
            safe = None
    if safe is None:
        safe = _compute_safe_cores()

    if safe > 1:
        return ["-n", str(safe)]
    return []


def _compute_safe_cores() -> int:
    total = os.cpu_count() or 1
    try:
        import psutil  # type: ignore
    except ImportError:
        pass
    else:
        total = psutil.cpu_count(logical=True) or total

    safe = max(1, int(math.floor(total * 0.85)))
    if safe % 2 == 1:
        safe = max(1, safe - 1)
    return max(1, safe)


def _maybe_run_resource_check(env: dict[str, str]) -> None:
    if env.get(RESOURCE_MONITOR_ENV, "0") != "1":
        return

    checker = SCRIPT_DIR / "system_resource_check.py"
    if not checker.exists():
        return

    subprocess.run(
        [sys.executable, str(checker)],
        env=env,
        check=False,
    )


def _target_args() -> list[str]:
    targets = os.getenv(TARGETS_ENV)
    if not targets:
        return []
    if os.getenv("MUTMUT_DEBUG", "0") == "1":
        print(f"[mutmut-wrapper] targeting: {targets}")
    return targets.split()


if __name__ == "__main__":
    raise SystemExit(main())
