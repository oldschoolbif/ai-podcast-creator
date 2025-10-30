# Run security scans
Write-Host "🔒 Running security scans..." -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣ Bandit (code security)..." -ForegroundColor Yellow
bandit -r src/ -f screen

Write-Host ""
Write-Host "2️⃣ Safety (dependency security)..." -ForegroundColor Yellow
safety check

Write-Host ""
Write-Host "✅ Security scan complete!" -ForegroundColor Green

