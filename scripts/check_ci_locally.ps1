# Check CI Status Locally
# Simulates the CI environment and runs tests

Write-Host "🔍 Checking CI Status Locally..." -ForegroundColor Cyan
Write-Host ""

# Set CI environment variables (same as GitHub Actions)
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
$env:PYTHONHASHSEED = "0"
$env:TZ = "UTC"
$env:LC_ALL = "C"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:HYPOTHESIS_SEED = "1337"
$env:TEST_SEED = "1337"
$env:PY_ENABLE_GPU_TESTS = "0"
$env:PY_PARALLEL = "0"

Write-Host "Environment variables set (matching CI)" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Virtual environment not found. Activate manually." -ForegroundColor Yellow
}

Write-Host "Running Pytest Run 1 (simulating CI)..." -ForegroundColor Cyan
Write-Host ""

# Run pytest (same as CI)
$result1 = python -m pytest -q 2>&1
$exitCode1 = $LASTEXITCODE

Write-Host ""
Write-Host "Run 1 Exit Code: $exitCode1" -ForegroundColor $(if ($exitCode1 -eq 0) { "Green" } else { "Red" })
Write-Host ""

Write-Host "Running Pytest Run 2 (determinism check)..." -ForegroundColor Cyan
Write-Host ""

# Run pytest again (determinism check)
$result2 = python -m pytest -q 2>&1
$exitCode2 = $LASTEXITCODE

Write-Host ""
Write-Host "Run 2 Exit Code: $exitCode2" -ForegroundColor $(if ($exitCode2 -eq 0) { "Green" } else { "Red" })
Write-Host ""

# Compare results
Write-Host "=== Comparison ===" -ForegroundColor Cyan
if ($exitCode1 -ne $exitCode2) {
    Write-Host "❌ FAILED: Exit codes differ ($exitCode1 vs $exitCode2)" -ForegroundColor Red
    Write-Host "   Tests are not deterministic!" -ForegroundColor Red
    exit 1
} elseif ($exitCode2 -ne 0) {
    Write-Host "❌ FAILED: Tests failed (exit code $exitCode2)" -ForegroundColor Red
    exit $exitCode2
} else {
    Write-Host "✅ PASSED: Both runs succeeded with same exit code" -ForegroundColor Green
    Write-Host "   Tests are deterministic" -ForegroundColor Green
    exit 0
}

