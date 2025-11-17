# Simulate the exact CI workflow behavior
# This tests the exit code capture mechanism, not just pytest

Write-Host "🔍 Simulating CI Workflow (with exit code capture)..." -ForegroundColor Cyan
Write-Host ""

# Set CI environment variables
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

# Activate venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

# Simulate pytest run 1 with exit code capture (like GitHub Actions)
Write-Host "=== Pytest Run 1 ===" -ForegroundColor Cyan
$pytest1Script = @"
set +e
pytest -q 2>&1 | Tee-Object -Variable pytest1Output
`$exitCode1 = `$LASTEXITCODE
Write-Host "Pytest run 1 completed with exit code: `$exitCode1"
"@

# Run in bash-like mode (PowerShell)
$pytest1Output = ""
python -m pytest -q 2>&1 | Tee-Object -Variable pytest1Output
$exitCode1 = $LASTEXITCODE
Write-Host "Pytest run 1 completed with exit code: $exitCode1" -ForegroundColor $(if ($exitCode1 -eq 0) { "Green" } else { "Red" })

# Simulate pytest run 2
Write-Host ""
Write-Host "=== Pytest Run 2 ===" -ForegroundColor Cyan
$pytest2Output = ""
python -m pytest -q 2>&1 | Tee-Object -Variable pytest2Output
$exitCode2 = $LASTEXITCODE
Write-Host "Pytest run 2 completed with exit code: $exitCode2" -ForegroundColor $(if ($exitCode2 -eq 0) { "Green" } else { "Red" })

# Simulate compare step (like GitHub Actions)
Write-Host ""
Write-Host "=== Compare Run Results ===" -ForegroundColor Cyan
Write-Host "Run 1 exit code: '$exitCode1'"
Write-Host "Run 2 exit code: '$exitCode2'"

if ([string]::IsNullOrEmpty($exitCode1) -or [string]::IsNullOrEmpty($exitCode2)) {
    Write-Host "ERROR: Exit codes not captured properly" -ForegroundColor Red
    exit 1
}

if ($exitCode1 -ne $exitCode2) {
    Write-Host "ERROR: Pytest exit codes differed between runs. Tests are not deterministic." -ForegroundColor Red
    Write-Host "Run 1: $exitCode1, Run 2: $exitCode2" -ForegroundColor Red
    exit 1
}

if ($exitCode2 -ne 0) {
    Write-Host "ERROR: Pytest failed (exit code $exitCode2)." -ForegroundColor Red
    exit $exitCode2
}

Write-Host "SUCCESS: Both runs completed successfully with exit code 0" -ForegroundColor Green
exit 0

