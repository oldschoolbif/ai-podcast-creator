# PowerShell Test Runner
# Run automated tests on Windows

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  AI PODCAST CREATOR - AUTOMATED TEST SUITE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the right directory
if (-not (Test-Path "pytest.ini")) {
    Write-Host "❌ ERROR: Must run from AI_Podcast_Creator directory" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  WARNING: Virtual environment not found" -ForegroundColor Yellow
}

# Install test dependencies
Write-Host ""
Write-Host "Checking test dependencies..." -ForegroundColor Yellow
pip install -q -r requirements-test.txt

# Run tests based on argument
$testType = $args[0]

switch ($testType) {
    "smoke" {
        Write-Host ""
        Write-Host "Running SMOKE TESTS..." -ForegroundColor Green
        pytest -v -m smoke tests/
    }
    "unit" {
        Write-Host ""
        Write-Host "Running UNIT TESTS..." -ForegroundColor Green
        pytest -v -m unit tests/unit/
    }
    "integration" {
        Write-Host ""
        Write-Host "Running INTEGRATION TESTS..." -ForegroundColor Green
        pytest -v -m "integration and not gpu" tests/integration/
    }
    "gpu" {
        Write-Host ""
        Write-Host "Running GPU TESTS..." -ForegroundColor Green
        pytest -v -m gpu tests/
    }
    "coverage" {
        Write-Host ""
        Write-Host "Running FULL SUITE WITH COVERAGE..." -ForegroundColor Green
        pytest -v --cov=src --cov-report=html --cov-report=term tests/
        Write-Host ""
        Write-Host "✓ Coverage report: htmlcov/index.html" -ForegroundColor Green
    }
    "fast" {
        Write-Host ""
        Write-Host "Running FAST TESTS (excluding slow)..." -ForegroundColor Green
        pytest -v -m "not slow" tests/
    }
    "all" {
        Write-Host ""
        Write-Host "Running ALL TESTS..." -ForegroundColor Green
        pytest -v tests/
    }
    default {
        Write-Host ""
        Write-Host "Running QUICK VALIDATION (smoke + unit)..." -ForegroundColor Green
        pytest -v -m "smoke or unit" tests/
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Cyan
        Write-Host "Other options:" -ForegroundColor Yellow
        Write-Host "  .\run_tests.ps1 smoke       - Quick smoke tests" -ForegroundColor White
        Write-Host "  .\run_tests.ps1 unit        - Unit tests only" -ForegroundColor White
        Write-Host "  .\run_tests.ps1 integration - Integration tests" -ForegroundColor White
        Write-Host "  .\run_tests.ps1 gpu         - GPU tests" -ForegroundColor White
        Write-Host "  .\run_tests.ps1 coverage    - Full suite + coverage" -ForegroundColor White
        Write-Host "  .\run_tests.ps1 fast        - Fast tests only" -ForegroundColor White
        Write-Host "  .\run_tests.ps1 all         - All tests" -ForegroundColor White
        Write-Host "================================================" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  TEST EXECUTION COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

