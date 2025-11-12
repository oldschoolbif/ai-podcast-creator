# Source this before running pytest or mutmut.

$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
$env:PYTHONHASHSEED = "0"
$env:TZ = "UTC"
$env:LC_ALL = "C"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:HYPOTHESIS_SEED = "1337"
$env:TEST_SEED = "1337"
$env:PY_GPU_MAX_LOAD = if ($env:PY_GPU_MAX_LOAD) { $env:PY_GPU_MAX_LOAD } else { "0.9" }
$env:PY_MEMORY_LIMIT_FRACTION = if ($env:PY_MEMORY_LIMIT_FRACTION) { $env:PY_MEMORY_LIMIT_FRACTION } else { "0.8" }
$env:PY_ENABLE_GPU_TESTS = if ($env:PY_ENABLE_GPU_TESTS) { $env:PY_ENABLE_GPU_TESTS } else { "0" } # default OFF
$env:PY_PARALLEL = if ($env:PY_PARALLEL) { $env:PY_PARALLEL } else { "1" }
$env:PY_SAFE_CORES = if ($env:PY_SAFE_CORES) { $env:PY_SAFE_CORES } else { "26" }
# $env:PY_ENABLE_GPU_TESTS = "1"

if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $devices = (nvidia-smi --query-gpu=index --format=csv,noheader) -join ","
    if ($devices) {
        $env:CUDA_VISIBLE_DEVICES = $devices
    }
}

if ($env:PY_PARALLEL -ne "0") {
    if ($env:PYTEST_ADDOPTS) {
        $env:PYTEST_ADDOPTS = "$($env:PYTEST_ADDOPTS) -n $($env:PY_SAFE_CORES)"
    } else {
        $env:PYTEST_ADDOPTS = "-n $($env:PY_SAFE_CORES)"
    }
}

