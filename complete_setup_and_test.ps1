# Complete Setup and Test - With Full Logging
# This runs everything and saves output to files

$ErrorActionPreference = "Continue"
$logFile = "setup_log.txt"
$testFile = "test_results.txt"

function Log {
    param($message, $color = "White")
    Write-Host $message -ForegroundColor $color
    $message | Out-File -Append -FilePath $logFile
}

# Clear old logs
if (Test-Path $logFile) { Remove-Item $logFile }
if (Test-Path $testFile) { Remove-Item $testFile }

Log "======================================================================" "Cyan"
Log "  COMPLETE SETUP AND TEST - $(Get-Date)" "Cyan"
Log "======================================================================" "Cyan"
Log ""

# Step 1: Check Python
Log "STEP 1: Checking Python..." "Yellow"
try {
    $pythonVersion = python --version 2>&1
    Log "  Python version: $pythonVersion" "Green"
    $pythonPath = (Get-Command python).Source
    Log "  Python path: $pythonPath" "White"
} catch {
    Log "  ERROR: Python not found!" "Red"
    exit 1
}
Log ""

# Step 2: Create venv
Log "STEP 2: Creating virtual environment..." "Yellow"
if (Test-Path "venv") {
    Log "  Removing existing venv..." "Gray"
    Remove-Item -Recurse -Force venv
}

python -m venv venv 2>&1 | Out-File -Append $logFile

if (Test-Path "venv\Scripts\python.exe") {
    Log "  ✓ Virtual environment created" "Green"
} else {
    Log "  ERROR: Failed to create venv" "Red"
    exit 1
}
Log ""

# Step 3: Upgrade pip
Log "STEP 3: Upgrading pip..." "Yellow"
.\venv\Scripts\python.exe -m pip install --upgrade pip 2>&1 | Out-File -Append $logFile
$pipVersion = .\venv\Scripts\pip.exe --version
Log "  pip version: $pipVersion" "Green"
Log ""

# Step 4: Install test dependencies
Log "STEP 4: Installing test dependencies (this takes 2-3 minutes)..." "Yellow"
Log "  Please wait..." "Gray"
.\venv\Scripts\pip.exe install -r requirements-test.txt 2>&1 | Out-File -Append $logFile

if ($LASTEXITCODE -eq 0) {
    Log "  ✓ Test dependencies installed" "Green"
} else {
    Log "  ⚠ Warning: Some packages may have issues" "Yellow"
}
Log ""

# Step 5: Verify pytest
Log "STEP 5: Verifying pytest..." "Yellow"
$pytestVersion = .\venv\Scripts\python.exe -m pytest --version 2>&1
Log "  pytest version: $pytestVersion" "Green"
Log ""

# Step 6: Run tests
Log "STEP 6: Running smoke tests..." "Yellow"
Log "  This may take 30-60 seconds..." "Gray"
Log ""

.\venv\Scripts\python.exe -m pytest -v -m smoke tests/ --tb=short 2>&1 | Tee-Object -FilePath $testFile | Out-File -Append $logFile

Log ""
Log "======================================================================" "Cyan"
Log "  SETUP COMPLETE!" "Cyan"
Log "======================================================================" "Cyan"
Log ""

# Show test summary
if (Test-Path $testFile) {
    Log "Test results saved to: $testFile" "White"
    Log ""
    Log "Last 20 lines of test output:" "Yellow"
    Get-Content $testFile -Tail 20 | ForEach-Object {
        Log "  $_" "White"
    }
}

Log ""
Log "Full log saved to: $logFile" "White"
Log ""
Log "Next steps:" "Yellow"
Log "  1. Check test_results.txt for full test output" "White"
Log "  2. Check setup_log.txt for full installation log" "White"
Log "  3. Run: .\venv\Scripts\Activate.ps1 to activate venv" "White"
Log "  4. Run: python -m pytest tests/ to run all tests" "White"
Log ""


