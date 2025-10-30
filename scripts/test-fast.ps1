# Run fast unit tests only
Write-Host "⚡ Running fast unit tests..." -ForegroundColor Cyan
Write-Host ""

pytest tests/unit -x --tb=short -q --maxfail=5

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Fast tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Tests failed!" -ForegroundColor Red
    exit 1
}

