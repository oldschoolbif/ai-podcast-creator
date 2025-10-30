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

Write-Host ""
if (-not $failed) {
    Write-Host "✅ All checks passed! Safe to push." -ForegroundColor Green
} else {
    Write-Host "❌ Some checks failed. Fix before pushing." -ForegroundColor Red
    exit 1
}

