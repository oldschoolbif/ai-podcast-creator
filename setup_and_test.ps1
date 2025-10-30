# Complete Setup and Test Script
# Run this to install test dependencies and run tests

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  AI PODCAST CREATOR - SETUP AND TEST" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check current directory
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Yellow
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ ERROR: Virtual environment not found at venv\" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor White
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  pip install -r requirements.txt" -ForegroundColor White
    exit 1
}

Write-Host "✓ Virtual environment found" -ForegroundColor Green

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running manually:" -ForegroundColor Yellow
    Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    exit 1
}

Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Check Python version
Write-Host ""
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor White

# Check pip
Write-Host ""
Write-Host "Checking pip..." -ForegroundColor Yellow
$pipVersion = pip --version 2>&1
Write-Host "  $pipVersion" -ForegroundColor White

# Install test dependencies
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  INSTALLING TEST DEPENDENCIES" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "requirements-test.txt") {
    Write-Host "Installing from requirements-test.txt..." -ForegroundColor Yellow
    pip install -r requirements-test.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Test dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠ Warning: Some packages may have failed to install" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ ERROR: requirements-test.txt not found" -ForegroundColor Red
    exit 1
}

# Verify pytest is installed
Write-Host ""
Write-Host "Verifying pytest installation..." -ForegroundColor Yellow
$pytestVersion = python -m pytest --version 2>&1
Write-Host "  $pytestVersion" -ForegroundColor White

# Run tests
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  RUNNING TESTS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Running smoke tests..." -ForegroundColor Yellow
Write-Host ""

python -m pytest -v -m smoke tests/ --tb=short 2>&1 | Tee-Object -FilePath "test_results.txt"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan

# Check test results
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "  ⚠ SOME TESTS FAILED OR HAD ISSUES" -ForegroundColor Yellow
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test results saved to: test_results.txt" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  - Review test_results.txt for details" -ForegroundColor White
Write-Host "  - Run .\run_tests.ps1 for more test options" -ForegroundColor White
Write-Host "  - See TESTING_GUIDE.md for full documentation" -ForegroundColor White
Write-Host ""

