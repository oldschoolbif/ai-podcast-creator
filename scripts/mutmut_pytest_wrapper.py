"""Wrapper to run pytest for mutmut without argument mangling issues."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Execute pytest and propagate its exit code.

    Mutmut 3.3.1 currently passes the tests directory as individual characters
    (``t``, ``e``, ``s``, ``t``, ``s``) when ``tests_dir`` is configured via
    ``pyproject.toml``. Rather than rely on that argument list, we ignore the
    received CLI arguments and invoke ``pytest`` directly, letting
    ``pytest.ini`` control discovery and global options.
    """

    project_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    segments = [str(project_root)]
    if current_pythonpath:
        segments.append(current_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(segments)

    # Optimize for mutation testing: fast execution with parallel support
    # Skip slow/integration/e2e tests by default, but allow GPU tests
    # Use parallel execution with pytest-xdist if available
    cmd = [sys.executable, "-m", "pytest"]
    
    # Determine test selection based on environment
    # By default, skip slow/integration/e2e but include GPU tests (they're fast with GPU)
    include_gpu = os.getenv("MUTMUT_INCLUDE_GPU", "1") == "1"
    include_slow = os.getenv("MUTMUT_SLOW_TESTS", "0") == "1"
    
    if include_slow:
        # Full suite - just skip e2e tests (they're hardest to run repeatedly)
        test_marker = "not e2e"
    elif include_gpu:
        # Fast mode: Include GPU tests (they're fast when GPU is available)
        # Skip: slow, integration, e2e, performance
        test_marker = "not slow and not integration and not e2e and not performance"
    else:
        # Fastest mode: Skip everything slow including GPU
        test_marker = "not slow and not integration and not e2e and not gpu and not performance"
    
    cmd.extend([
        "-m", test_marker,
        "--maxfail=3",  # Allow a few failures (tests may have platform differences)
        "--tb=short",  # Short tracebacks (less output)
        "-q",  # Quiet mode (less output)
    ])
    
    # Enable parallel execution if pytest-xdist is available
    # This uses all CPU cores to run tests in parallel
    try:
        import pytest_xdist
        import multiprocessing
        # Use all available CPU cores for parallel test execution
        num_workers = os.getenv("MUTMUT_WORKERS", str(multiprocessing.cpu_count()))
        cmd.extend(["-n", num_workers])
    except ImportError:
        # pytest-xdist not available, run sequentially
        pass
    
    if os.getenv("MUTMUT_DEBUG", "0") == "1":
        print("[mutmut] PYTHONPATH=", env.get("PYTHONPATH"))
        print("[mutmut] Command:", " ".join(cmd))
    
    result = subprocess.run(cmd, env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()


