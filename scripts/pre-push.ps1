# Pre-push checks - run before pushing to ensure CI will pass
Write-Host "🚀 Running pre-push checks..." -ForegroundColor Cyan
Write-Host ""

$failed = $false

# 1. Linting
Write-Host "1️⃣ Linting..." -ForegroundColor Yellow
black --check src/ tests/
if ($LASTEXITCODE -ne 0) { $failed = $true }

# 2. Tests
Write-Host ""
Write-Host "2️⃣ Running tests..." -ForegroundColor Yellow
pytest -x --tb=short -q
if ($LASTEXITCODE -ne 0) { $failed = $true }

# 3. Coverage check
Write-Host ""
Write-Host "3️⃣ Checking coverage..." -ForegroundColor Yellow
pytest --cov=src --cov-report=term --cov-fail-under=30 --tb=no -q
if ($LASTEXITCODE -ne 0) { $failed = $true }

# 4. GPU tests (if GPU available and enabled)
Write-Host ""
Write-Host "4️⃣ Checking GPU tests..." -ForegroundColor Yellow
if ($env:PY_ENABLE_GPU_TESTS -eq "1" -and (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    Write-Host "  Running GPU tests..." -ForegroundColor Cyan
    pytest tests/unit tests/integration -m gpu -q --tb=no
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ⚠️  Some GPU tests failed (non-blocking)" -ForegroundColor Yellow
        # Don't fail pre-push for GPU tests - they're optional
    } else {
        Write-Host "  ✅ GPU tests passed" -ForegroundColor Green
    }
} else {
    Write-Host "  ⏭️  GPU tests skipped (not enabled or no GPU)" -ForegroundColor Gray
}

Write-Host ""
if (-not $failed) {
    Write-Host "✅ All checks passed! Safe to push." -ForegroundColor Green
} else {
    Write-Host "❌ Some checks failed. Fix before pushing." -ForegroundColor Red
    exit 1
}

