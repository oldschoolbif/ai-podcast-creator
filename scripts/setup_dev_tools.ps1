# Development Tools Setup Script for Windows
# Run this once after cloning the repository

Write-Host "🚀 Setting up development tools..." -ForegroundColor Cyan
Write-Host ""

# Check if in virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Not in virtual environment!" -ForegroundColor Yellow
    Write-Host "   Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Virtual environment active" -ForegroundColor Green
Write-Host ""

# Install dev dependencies
Write-Host "📦 Installing development dependencies..." -ForegroundColor Cyan
if (Test-Path "requirements-dev.txt") {
    pip install -r requirements-dev.txt
} else {
    # Fallback (legacy)
    pip install pre-commit black flake8 isort bandit safety radon mypy pytest-html pytest-xdist pytest-timeout
}

# Install pre-commit hooks
Write-Host ""
Write-Host "🎣 Installing pre-commit hooks..." -ForegroundColor Cyan
pre-commit install

# Run pre-commit on all files
Write-Host ""
Write-Host "🧪 Running pre-commit checks..." -ForegroundColor Cyan
pre-commit run --all-files

Write-Host ""
Write-Host "✅ Development tools setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Quick Commands:" -ForegroundColor Cyan
Write-Host "   .\scripts\test.ps1          - Run all tests" -ForegroundColor White
Write-Host "   .\scripts\test-fast.ps1     - Run fast tests only" -ForegroundColor White
Write-Host "   .\scripts\coverage.ps1      - Generate coverage report" -ForegroundColor White
Write-Host "   .\scripts\lint.ps1          - Run linting" -ForegroundColor White
Write-Host "   .\scripts\security.ps1      - Run security scan" -ForegroundColor White
Write-Host "   python -m pytest tests/performance -k benchmark  - Run performance suites" -ForegroundColor White
Write-Host "   .\scripts\run_mutmut.ps1    - Launch mutation testing" -ForegroundColor White
Write-Host ""
Write-Host "📖 Full guide: CI_CD_SETUP_GUIDE.md" -ForegroundColor Cyan

