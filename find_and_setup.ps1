# Find Python and Setup Everything
# This script finds Python and creates the virtual environment

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  FINDING PYTHON AND SETTING UP ENVIRONMENT" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Function to test if Python works
function Test-Python {
    param($pythonPath)
    try {
        $version = & $pythonPath --version 2>&1
        if ($version -match "Python 3\.(10|11|12)") {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Search for Python in common locations
Write-Host "Searching for Python installation..." -ForegroundColor Yellow
Write-Host ""

$pythonLocations = @(
    # py launcher
    "py",
    # Current user AppData
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    # System-wide
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    # Program Files
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe",
    # Check other projects
    "d:\dev\main\venv\Scripts\python.exe",
    "d:\dev\exponis-github\venv\Scripts\python.exe",
    "d:\dev\exponis-local\venv\Scripts\python.exe"
)

$foundPython = $null

foreach ($location in $pythonLocations) {
    if ($location -eq "py") {
        # Try py launcher
        try {
            $pyVersion = py --version 2>&1
            if ($pyVersion -match "Python 3\.(10|11|12)") {
                Write-Host "✓ Found Python via py launcher: $pyVersion" -ForegroundColor Green
                $foundPython = "py"
                break
            }
        } catch {
            # py launcher not available
        }
    } else {
        # Try direct path
        if (Test-Path $location) {
            Write-Host "  Checking: $location" -ForegroundColor Gray
            if (Test-Python $location) {
                $version = & $location --version 2>&1
                Write-Host "✓ Found Python: $location" -ForegroundColor Green
                Write-Host "  Version: $version" -ForegroundColor White
                $foundPython = $location
                break
            }
        }
    }
}

if (-not $foundPython) {
    Write-Host ""
    Write-Host "❌ ERROR: Could not find Python 3.10, 3.11, or 3.12" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python must be installed. Please:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "2. Install Python 3.10 or 3.11" -ForegroundColor White
    Write-Host "3. Make sure to check 'Add Python to PATH'" -ForegroundColor White
    Write-Host "4. Restart PowerShell and run this script again" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  CREATING VIRTUAL ENVIRONMENT" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Create venv
if (Test-Path "venv") {
    Write-Host "⚠ Virtual environment already exists. Removing old one..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

Write-Host "Creating virtual environment (this takes 30 seconds)..." -ForegroundColor Yellow

if ($foundPython -eq "py") {
    py -m venv venv
} else {
    & $foundPython -m venv venv
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Virtual environment created" -ForegroundColor Green

# Activate venv
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Verify activation
$venvPython = ".\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $venvVersion = & $venvPython --version
    Write-Host "✓ Virtual environment activated: $venvVersion" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: Virtual environment activation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  UPGRADING PIP" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

& ".\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet

Write-Host "✓ pip upgraded" -ForegroundColor Green

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  INSTALLING DEPENDENCIES" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Install main dependencies
Write-Host "Installing main dependencies (this takes 3-5 minutes)..." -ForegroundColor Yellow
Write-Host "Please be patient..." -ForegroundColor Gray
Write-Host ""

& ".\venv\Scripts\pip.exe" install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠ WARNING: Some main dependencies may have failed" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✓ Main dependencies installed" -ForegroundColor Green
}

# Install test dependencies
Write-Host ""
Write-Host "Installing test dependencies (1 minute)..." -ForegroundColor Yellow
Write-Host ""

& ".\venv\Scripts\pip.exe" install -r requirements-test.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠ WARNING: Some test dependencies may have failed" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✓ Test dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  RUNNING TESTS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Run smoke tests
Write-Host "Running smoke tests..." -ForegroundColor Yellow
Write-Host ""

& ".\venv\Scripts\python.exe" -m pytest -v -m smoke tests/ --tb=short

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run all tests: .\run_tests.ps1" -ForegroundColor White
Write-Host "  3. Check GPU: python check_gpu.py" -ForegroundColor White
Write-Host "  4. See TESTING_GUIDE.md for more" -ForegroundColor White
Write-Host ""


