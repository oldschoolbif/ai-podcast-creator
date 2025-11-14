#!/usr/bin/env bash
# Source this before running pytest or mutmut.

export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONHASHSEED=0
export TZ=UTC
export LC_ALL=C
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export HYPOTHESIS_SEED=1337
export TEST_SEED=1337
export PY_GPU_MAX_LOAD=${PY_GPU_MAX_LOAD:-0.9}
export PY_MEMORY_LIMIT_FRACTION=${PY_MEMORY_LIMIT_FRACTION:-0.8}
export PY_ENABLE_GPU_TESTS=${PY_ENABLE_GPU_TESTS:-0}  # default OFF
export PY_PARALLEL=${PY_PARALLEL:-1}
export PY_SAFE_CORES=${PY_SAFE_CORES:-26}
# export PY_ENABLE_GPU_TESTS=1

if command -v nvidia-smi >/dev/null 2>&1; then
  CUDA_IDS="$(nvidia-smi --query-gpu=index --format=csv,noheader | tr '\n' ',' | sed 's/,$//')"
  if [ -n "$CUDA_IDS" ]; then
    export CUDA_VISIBLE_DEVICES="$CUDA_IDS"
  fi
fi

if [ "${PY_PARALLEL}" != "0" ]; then
  export PYTEST_ADDOPTS="${PYTEST_ADDOPTS} -n ${PY_SAFE_CORES}"
  export PYTEST_ADDOPTS="${PYTEST_ADDOPTS#" "}"
fi

