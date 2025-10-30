#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Interactive Test & QA Menu for AI Podcast Creator

.DESCRIPTION
    Provides menu-driven access to testing, coverage, linting, and QA tools
#>

# Colors for output
$script:Colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
    Menu = "Magenta"
}

function Write-Header {
    param([string]$Text)
    Write-Host "`n$('='*80)" -ForegroundColor $Colors.Header
    Write-Host "  $Text" -ForegroundColor $Colors.Header
    Write-Host "$('='*80)`n" -ForegroundColor $Colors.Header
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor $Colors.Success
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠ $Text" -ForegroundColor $Colors.Warning
}

function Write-Error {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor $Colors.Error
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ $Text" -ForegroundColor $Colors.Info
}

function Test-VirtualEnv {
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Error "Virtual environment not found!"
        Write-Info "Run: python -m venv venv"
        return $false
    }
    return $true
}

function Invoke-MenuItem {
    param(
        [string]$Title,
        [scriptblock]$Action
    )
    
    Write-Header $Title
    
    if (-not (Test-VirtualEnv)) {
        Read-Host "`nPress Enter to continue"
        return
    }
    
    try {
        & $Action
    }
    catch {
        Write-Error "Error: $_"
    }
    
    Write-Host "`n"
    Read-Host "Press Enter to continue"
}

function Show-Menu {
    Clear-Host
    Write-Header "AI PODCAST CREATOR - TEST & QA MENU"
    
    Write-Host "  TESTING" -ForegroundColor $Colors.Menu
    Write-Host "  [1]  Run All Unit Tests" -ForegroundColor White
    Write-Host "  [2]  Run All Tests with Coverage" -ForegroundColor White
    Write-Host "  [3]  Run Fast Tests Only (skip GPU/network/slow)" -ForegroundColor White
    Write-Host "  [4]  Run Specific Test File" -ForegroundColor White
    Write-Host ""
    
    Write-Host "  COVERAGE" -ForegroundColor $Colors.Menu
    Write-Host "  [5]  Show Coverage Report" -ForegroundColor White
    Write-Host "  [6]  Show Coverage Summary" -ForegroundColor White
    Write-Host "  [7]  Generate HTML Coverage Report" -ForegroundColor White
    Write-Host "  [8]  Identify Untested Code" -ForegroundColor White
    Write-Host ""
    
    Write-Host "  CODE QUALITY" -ForegroundColor $Colors.Menu
    Write-Host "  [9]  Show Linter Issues" -ForegroundColor White
    Write-Host "  [10] Run Code Quality Checks" -ForegroundColor White
    Write-Host "  [11] Show Type Checking Issues" -ForegroundColor White
    Write-Host ""
    
    Write-Host "  UTILITIES" -ForegroundColor $Colors.Menu
    Write-Host "  [12] List All Tests" -ForegroundColor White
    Write-Host "  [13] Check Test Dependencies" -ForegroundColor White
    Write-Host "  [14] Clean Test Cache" -ForegroundColor White
    Write-Host "  [15] Show Test Statistics" -ForegroundColor White
    Write-Host ""
    
    Write-Host "  [Q]  Quit" -ForegroundColor Yellow
    Write-Host ""
}

# Menu Actions

function RunAllTests {
    Write-Info "Running all unit tests..."
    .\venv\Scripts\python.exe -m pytest tests/unit/ -v --tb=short
}

function RunTestsWithCoverage {
    Write-Info "Running tests with coverage..."
    .\venv\Scripts\python.exe -m pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
    Write-Success "Coverage report generated!"
    Write-Info "HTML report: htmlcov\index.html"
    Write-Info "XML report: coverage.xml"
}

function RunFastTests {
    Write-Info "Running fast tests (skipping GPU, network, and slow tests)..."
    .\venv\Scripts\python.exe -m pytest tests/unit/ -v -m "not gpu and not network and not slow"
}

function RunSpecificTest {
    Write-Host "`nAvailable test files:" -ForegroundColor Cyan
    $testFiles = Get-ChildItem tests\unit\test_*.py | Select-Object -ExpandProperty Name
    
    for ($i = 0; $i -lt $testFiles.Count; $i++) {
        Write-Host "  [$($i+1)] $($testFiles[$i])" -ForegroundColor White
    }
    
    Write-Host ""
    $selection = Read-Host "Enter number (or filename)"
    
    if ($selection -match '^\d+$') {
        $index = [int]$selection - 1
        if ($index -ge 0 -and $index -lt $testFiles.Count) {
            $testFile = "tests\unit\$($testFiles[$index])"
        } else {
            Write-Error "Invalid selection"
            return
        }
    } else {
        $testFile = "tests\unit\$selection"
    }
    
    if (Test-Path $testFile) {
        Write-Info "Running $testFile..."
        .\venv\Scripts\python.exe -m pytest $testFile -v
    } else {
        Write-Error "Test file not found: $testFile"
    }
}

function ShowCoverageReport {
    if (Test-Path "htmlcov\index.html") {
        Write-Info "Opening coverage report in browser..."
        Start-Process "htmlcov\index.html"
    } else {
        Write-Warning "Coverage report not found. Run option [2] or [7] first."
    }
}

function ShowCoverageSummary {
    Write-Info "Generating coverage summary..."
    .\venv\Scripts\python.exe -m pytest tests/unit/ --cov=src --cov-report=term --quiet --quiet
}

function GenerateHTMLCoverage {
    Write-Info "Generating HTML coverage report..."
    .\venv\Scripts\python.exe -m pytest tests/unit/ --cov=src --cov-report=html --quiet
    Write-Success "HTML coverage report generated at htmlcov\index.html"
    
    $openReport = Read-Host "`nOpen report in browser? (Y/n)"
    if ($openReport -ne 'n' -and $openReport -ne 'N') {
        Start-Process "htmlcov\index.html"
    }
}

function IdentifyUntestedCode {
    Write-Info "Analyzing code coverage to identify untested code..."
    
    # Run coverage
    .\venv\Scripts\python.exe -m pytest tests/unit/ --cov=src --cov-report=term-missing --quiet 2>&1 | Tee-Object -Variable coverageOutput
    
    Write-Host "`n" -NoNewline
    Write-Header "UNTESTED CODE ANALYSIS"
    
    # Parse coverage output for files with less than 100% coverage
    $inCoverageSection = $false
    $untestedFiles = @()
    
    foreach ($line in $coverageOutput) {
        if ($line -match '^Name\s+Stmts\s+Miss') {
            $inCoverageSection = $true
            continue
        }
        
        if ($inCoverageSection -and $line -match '^src/') {
            $parts = $line -split '\s+' | Where-Object { $_ -ne '' }
            if ($parts.Count -ge 4) {
                $file = $parts[0]
                $stmts = $parts[1]
                $miss = $parts[2]
                $cover = $parts[3]
                
                if ($miss -ne '0') {
                    $untestedFiles += [PSCustomObject]@{
                        File = $file
                        Statements = $stmts
                        Missing = $miss
                        Coverage = $cover
                    }
                }
            }
        }
        
        if ($inCoverageSection -and $line -match '^-+') {
            break
        }
    }
    
    if ($untestedFiles.Count -gt 0) {
        Write-Warning "Files needing more test coverage:`n"
        $untestedFiles | Format-Table -Property File, Statements, Missing, Coverage -AutoSize
        
        Write-Info "`nTo see missing line numbers, run option [2] or [6]"
    } else {
        Write-Success "All code is fully tested! 🎉"
    }
}

function ShowLinterIssues {
    Write-Info "Checking for linter issues..."
    
    # Check if flake8 is installed
    $flake8Installed = .\venv\Scripts\python.exe -m pip list | Select-String "flake8"
    
    if (-not $flake8Installed) {
        Write-Warning "flake8 not installed. Installing..."
        .\venv\Scripts\python.exe -m pip install flake8 -q
    }
    
    Write-Host "`nRunning flake8..." -ForegroundColor Cyan
    .\venv\Scripts\python.exe -m flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
    
    Write-Host "`nRunning extended checks..." -ForegroundColor Cyan
    .\venv\Scripts\python.exe -m flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
}

function RunCodeQualityChecks {
    Write-Info "Running comprehensive code quality checks..."
    
    # Install tools if needed
    $tools = @('flake8', 'pylint', 'black', 'isort')
    foreach ($tool in $tools) {
        $installed = .\venv\Scripts\python.exe -m pip list | Select-String $tool
        if (-not $installed) {
            Write-Info "Installing $tool..."
            .\venv\Scripts\python.exe -m pip install $tool -q
        }
    }
    
    Write-Host "`n1. Flake8 (Style Guide)" -ForegroundColor Magenta
    .\venv\Scripts\python.exe -m flake8 src/ --count --statistics --max-line-length=127
    
    Write-Host "`n2. Black (Code Formatting Check)" -ForegroundColor Magenta
    .\venv\Scripts\python.exe -m black src/ tests/ --check --diff
    
    Write-Host "`n3. Import Sorting Check" -ForegroundColor Magenta
    .\venv\Scripts\python.exe -m isort src/ tests/ --check-only --diff
    
    Write-Success "`nCode quality checks complete!"
}

function ShowTypeCheckingIssues {
    Write-Info "Running type checking with mypy..."
    
    $mypyInstalled = .\venv\Scripts\python.exe -m pip list | Select-String "mypy"
    
    if (-not $mypyInstalled) {
        Write-Warning "mypy not installed. Installing..."
        .\venv\Scripts\python.exe -m pip install mypy -q
    }
    
    .\venv\Scripts\python.exe -m mypy src/ --ignore-missing-imports --show-error-codes
}

function ListAllTests {
    Write-Info "Listing all available tests..."
    Write-Host ""
    .\venv\Scripts\python.exe -m pytest tests/unit/ --collect-only -q
}

function CheckTestDependencies {
    Write-Info "Checking test dependencies..."
    
    $required = @('pytest', 'pytest-cov', 'pytest-asyncio', 'pytest-mock')
    $missing = @()
    
    foreach ($pkg in $required) {
        $installed = .\venv\Scripts\python.exe -m pip list | Select-String $pkg
        if ($installed) {
            Write-Success "$pkg is installed"
        } else {
            Write-Warning "$pkg is MISSING"
            $missing += $pkg
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host ""
        $install = Read-Host "Install missing packages? (Y/n)"
        if ($install -ne 'n' -and $install -ne 'N') {
            .\venv\Scripts\python.exe -m pip install $missing -q
            Write-Success "Dependencies installed!"
        }
    } else {
        Write-Success "`nAll test dependencies are installed!"
    }
}

function CleanTestCache {
    Write-Info "Cleaning test cache and artifacts..."
    
    $itemsToDelete = @(
        '.pytest_cache',
        '.coverage',
        'coverage.xml',
        'htmlcov',
        '__pycache__',
        'tests/__pycache__',
        'tests/unit/__pycache__',
        'tests/integration/__pycache__'
    )
    
    foreach ($item in $itemsToDelete) {
        if (Test-Path $item) {
            Remove-Item $item -Recurse -Force -ErrorAction SilentlyContinue
            Write-Success "Deleted: $item"
        }
    }
    
    # Find and delete all __pycache__ directories
    Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Deleted: $($_.FullName)"
    }
    
    # Delete all .pyc files
    Get-ChildItem -Path . -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    }
    
    Write-Success "`nTest cache cleaned!"
}

function ShowTestStatistics {
    Write-Info "Gathering test statistics..."
    
    # Count test files
    $testFiles = (Get-ChildItem tests/unit/test_*.py).Count
    
    # Count test functions
    $testCount = 0
    Get-ChildItem tests/unit/test_*.py | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        $testCount += ([regex]::Matches($content, 'def test_')).Count
    }
    
    # Get lines of test code
    $testLines = 0
    Get-ChildItem tests/unit/test_*.py | ForEach-Object {
        $testLines += (Get-Content $_.FullName).Count
    }
    
    # Get source code stats
    $srcFiles = (Get-ChildItem src/ -Recurse -Filter "*.py").Count
    $srcLines = 0
    Get-ChildItem src/ -Recurse -Filter "*.py" | ForEach-Object {
        $srcLines += (Get-Content $_.FullName).Count
    }
    
    Write-Host "`nTEST SUITE STATISTICS" -ForegroundColor Cyan
    Write-Host "$('='*50)" -ForegroundColor Cyan
    Write-Host "Test Files:        $testFiles" -ForegroundColor White
    Write-Host "Test Functions:    $testCount" -ForegroundColor White
    Write-Host "Test Code Lines:   $testLines" -ForegroundColor White
    Write-Host ""
    Write-Host "Source Files:      $srcFiles" -ForegroundColor White
    Write-Host "Source Lines:      $srcLines" -ForegroundColor White
    Write-Host ""
    $ratio = [math]::Round($testLines / $srcLines, 2)
    Write-Host "Test/Source Ratio: $ratio" -ForegroundColor $(if ($ratio -gt 0.5) { "Green" } else { "Yellow" })
    Write-Host "$('='*50)" -ForegroundColor Cyan
    
    # Run quick test to get pass/fail stats
    Write-Host "`nRunning quick test check..." -ForegroundColor Cyan
    .\venv\Scripts\python.exe -m pytest tests/unit/ --collect-only -q 2>&1 | Select-Object -Last 1
}

# Main Loop

$continue = $true

while ($continue) {
    Show-Menu
    $choice = Read-Host "Select an option"
    
    switch ($choice) {
        '1'  { Invoke-MenuItem "Run All Unit Tests" { RunAllTests } }
        '2'  { Invoke-MenuItem "Run Tests with Coverage" { RunTestsWithCoverage } }
        '3'  { Invoke-MenuItem "Run Fast Tests Only" { RunFastTests } }
        '4'  { Invoke-MenuItem "Run Specific Test File" { RunSpecificTest } }
        '5'  { Invoke-MenuItem "Show Coverage Report" { ShowCoverageReport } }
        '6'  { Invoke-MenuItem "Show Coverage Summary" { ShowCoverageSummary } }
        '7'  { Invoke-MenuItem "Generate HTML Coverage Report" { GenerateHTMLCoverage } }
        '8'  { Invoke-MenuItem "Identify Untested Code" { IdentifyUntestedCode } }
        '9'  { Invoke-MenuItem "Show Linter Issues" { ShowLinterIssues } }
        '10' { Invoke-MenuItem "Run Code Quality Checks" { RunCodeQualityChecks } }
        '11' { Invoke-MenuItem "Show Type Checking Issues" { ShowTypeCheckingIssues } }
        '12' { Invoke-MenuItem "List All Tests" { ListAllTests } }
        '13' { Invoke-MenuItem "Check Test Dependencies" { CheckTestDependencies } }
        '14' { Invoke-MenuItem "Clean Test Cache" { CleanTestCache } }
        '15' { Invoke-MenuItem "Show Test Statistics" { ShowTestStatistics } }
        'q'  { $continue = $false }
        'Q'  { $continue = $false }
        default {
            Write-Warning "Invalid option. Please try again."
            Start-Sleep -Seconds 1
        }
    }
}

Write-Host "`nGoodbye! 👋" -ForegroundColor Green


