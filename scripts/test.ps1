# Run full test suite
Write-Host "🧪 Running full test suite..." -ForegroundColor Cyan
Write-Host ""

pytest --cov=src --cov-report=term --cov-report=html -v

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host "📊 Coverage report: htmlcov\index.html" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Tests failed!" -ForegroundColor Red
    exit 1
}

