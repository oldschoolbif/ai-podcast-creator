# Check PR CI Status
# Simulates CI and provides status summary

Write-Host "🔍 Checking PR CI Status..." -ForegroundColor Cyan
Write-Host ""

# Get current branch
$branch = git rev-parse --abbrev-ref HEAD
Write-Host "Current Branch: $branch" -ForegroundColor Yellow
Write-Host ""

# Check if branch is pushed
Write-Host "Checking if branch is pushed..." -ForegroundColor Cyan
$remoteBranch = git ls-remote --heads origin $branch 2>&1
if ($remoteBranch) {
    Write-Host "✅ Branch is pushed to origin" -ForegroundColor Green
    
    # Get latest commit
    $latestCommit = git log --oneline -1
    Write-Host "Latest commit: $latestCommit" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "⚠️  Branch not pushed to origin" -ForegroundColor Yellow
    Write-Host "   Run: git push origin $branch" -ForegroundColor Yellow
    Write-Host ""
}

# Check for uncommitted changes
Write-Host "Checking for uncommitted changes..." -ForegroundColor Cyan
$status = git status --short
if ($status) {
    Write-Host "⚠️  Uncommitted changes found:" -ForegroundColor Yellow
    $status | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    Write-Host ""
} else {
    Write-Host "✅ No uncommitted changes" -ForegroundColor Green
    Write-Host ""
}

# Run CI simulation
Write-Host "Running CI simulation..." -ForegroundColor Cyan
Write-Host ""

$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
$env:PYTHONHASHSEED = "0"
$env:HYPOTHESIS_SEED = "1337"
$env:TEST_SEED = "1337"
$env:PY_ENABLE_GPU_TESTS = "0"
$env:PY_PARALLEL = "0"

if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

Write-Host "Run 1: Testing..." -ForegroundColor Cyan
$result1 = python -m pytest -q 2>&1
$exitCode1 = $LASTEXITCODE

Write-Host "Run 2: Determinism check..." -ForegroundColor Cyan
$result2 = python -m pytest -q 2>&1
$exitCode2 = $LASTEXITCODE

Write-Host ""
Write-Host "=== CI Simulation Results ===" -ForegroundColor Cyan
Write-Host "Run 1 Exit Code: $exitCode1" -ForegroundColor $(if ($exitCode1 -eq 0) { "Green" } else { "Red" })
Write-Host "Run 2 Exit Code: $exitCode2" -ForegroundColor $(if ($exitCode2 -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($exitCode1 -ne $exitCode2) {
    Write-Host "❌ FAILED: Tests are not deterministic" -ForegroundColor Red
    Write-Host "   Exit codes differ: $exitCode1 vs $exitCode2" -ForegroundColor Red
    exit 1
} elseif ($exitCode2 -ne 0) {
    Write-Host "❌ FAILED: Tests failed (exit code $exitCode2)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Failed tests:" -ForegroundColor Yellow
    $result2 | Select-String -Pattern "FAILED|ERROR" | Select-Object -First 10
    exit $exitCode2
} else {
    Write-Host "✅ PASSED: All tests pass and are deterministic" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Summary ===" -ForegroundColor Cyan
    Write-Host "✅ Tests passing locally" -ForegroundColor Green
    Write-Host "✅ Tests are deterministic" -ForegroundColor Green
    Write-Host "✅ Ready for CI" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Check PR on GitHub: https://github.com/oldschoolbif/ai-podcast-creator/pulls" -ForegroundColor Gray
    Write-Host "2. Verify CI passes in GitHub Actions" -ForegroundColor Gray
    Write-Host "3. Review any CI failures if present" -ForegroundColor Gray
    exit 0
}

