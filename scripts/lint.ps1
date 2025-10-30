# Run linting and formatting checks
Write-Host "🧹 Running linting checks..." -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣ Flake8..." -ForegroundColor Yellow
flake8 src/ --max-line-length=120 --statistics

Write-Host ""
Write-Host "2️⃣ Black (check only)..." -ForegroundColor Yellow
black --check src/ tests/

Write-Host ""
Write-Host "3️⃣ isort (check only)..." -ForegroundColor Yellow
isort --check-only --profile=black src/ tests/

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All checks passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Issues found. Run this to fix:" -ForegroundColor Yellow
    Write-Host "   black src/ tests/" -ForegroundColor White
    Write-Host "   isort --profile=black src/ tests/" -ForegroundColor White
}

