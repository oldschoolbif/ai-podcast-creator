# README – Deterministic Testing & Mutation Analysis

## Purpose
Ensure `pytest` and `mutmut` runs are reproducible across machines and CI by standardizing environment variables, dependency pins, and execution commands.

## One-Time Setup
- `pip install -r requirements.txt`
  - If using Poetry: `poetry install`

## Deterministic Environment
Source the helper scripts before running tests to enforce deterministic options.

**Bash**
```
source scripts/test_env_example.sh
```

**PowerShell**
```
. .\scripts\test_env_example.ps1
```

Manual equivalent variables if needed:
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`
- `PYTHONHASHSEED=0`
- `TZ=UTC`
- `LC_ALL=C`
- `OMP_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `HYPOTHESIS_SEED=1337`
- `TEST_SEED=1337`
- `PY_ENABLE_GPU_TESTS=0` (enable with `1` when running on CUDA-capable hosts)
- `PY_GPU_MAX_LOAD=0.9`
- `PY_MEMORY_LIMIT_FRACTION=0.8`
- `PY_PARALLEL=1`
- `PY_SAFE_CORES=26`

## Run Tests Deterministically
```
pytest -q
```

## Run Mutation Tests Deterministically
```
mutmut run --use-coverage --runner "python scripts/mutmut_pytest_wrapper.py"
mutmut results
```

## Troubleshooting Flakiness
- **Time-sensitive tests**: freeze time using the `frozen_time` fixture.
- **Randomness**: verify `TEST_SEED` / `PYTHONHASHSEED` are set; reseed if needed.
- **Network calls**: tests without `@pytest.mark.network` are blocked; add the mark or stub network access.
- **Concurrency**: avoid mixing threaded/process tests with mutation runs unless deterministic.
- **BLAS threads**: confirm `OMP_NUM_THREADS` and `MKL_NUM_THREADS` are pinned to 1 to reduce nondeterminism.

## Network-Test Policy
- Mark tests that truly require outbound network access:
  ```
  @pytest.mark.network
  ```
- During mutation tests and default CI runs, network access remains disabled unless explicitly allowed.

## GPU Quarantine Policy
- Tests marked `@pytest.mark.gpu` are skipped by default to avoid flaky CUDA setup unless `PY_ENABLE_GPU_TESTS=1`.
- Enable GPU tests temporarily:
  - **Bash**
    ```
    export PY_ENABLE_GPU_TESTS=1
    pytest -m gpu -q
    ```
  - **PowerShell**
    ```
    $env:PY_ENABLE_GPU_TESTS="1"
    pytest -m gpu -q
    ```
- To run GPU tests in CI, add an ephemeral job with:
  ```
  env:
    PY_ENABLE_GPU_TESTS: "1"
  ```
  and ensure CUDA drivers are available.
- Mutation testing excludes GPU cases by default; enable them only in a dedicated GPU-capable pipeline.

## Performance Mode
- These settings leverage ~85% of CPU cores and high GPU utilization. Disable with `PY_PARALLEL=0` or lower `PY_GPU_MAX_LOAD` if the system becomes sluggish.
- **Bash**
  ```
  export PY_PARALLEL=1 PY_GPU_MAX_LOAD=0.9 PY_MEMORY_LIMIT_FRACTION=0.8
  source scripts/test_env_example.sh
  pytest -n auto -q
  mutmut run --use-coverage
  ```
- **PowerShell**
  ```
  $env:PY_PARALLEL="1"
  $env:PY_GPU_MAX_LOAD="0.9"
  $env:PY_MEMORY_LIMIT_FRACTION="0.8"
  . .\scripts\test_env_example.ps1
  pytest -n auto -q
  mutmut run --use-coverage
  ```
- If your system becomes unstable, set `PY_PARALLEL=0` or reduce `PY_GPU_MAX_LOAD` before rerunning.

