# Simple Test Runner with Clear Output
# Run this to see test results clearly

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  RUNNING TESTS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Activate venv and run tests
& ".\venv\Scripts\python.exe" -m pytest -v tests/

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TEST RUN COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more options:" -ForegroundColor Yellow
Write-Host "  python -m pytest -v tests/              # Verbose output" -ForegroundColor White
Write-Host "  python -m pytest -v -m smoke tests/     # Just smoke tests" -ForegroundColor White
Write-Host "  python -m pytest --cov=src tests/       # With coverage" -ForegroundColor White
Write-Host ""

