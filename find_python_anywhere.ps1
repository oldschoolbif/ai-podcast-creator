# Comprehensive Python Search
# This will find Python wherever it's hiding

Write-Host "COMPREHENSIVE PYTHON SEARCH" -ForegroundColor Cyan
Write-Host "Searching your entire system..." -ForegroundColor Yellow
Write-Host ""

# Check PATH environment variable
Write-Host "1. Checking PATH environment variable..." -ForegroundColor Yellow
$env:PATH -split ';' | Where-Object { $_ -match 'python' } | ForEach-Object {
    Write-Host "  Found in PATH: $_" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. Checking for 'py' launcher..." -ForegroundColor Yellow
try {
    $pyOutput = py --version 2>&1
    Write-Host "  ✓ py launcher found: $pyOutput" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Full py info:" -ForegroundColor White
    py -0
} catch {
    Write-Host "  ✗ py launcher not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "3. Checking all d:\dev projects for existing venv..." -ForegroundColor Yellow
Get-ChildItem d:\dev -Directory | ForEach-Object {
    $venvPath = Join-Path $_.FullName "venv\Scripts\python.exe"
    if (Test-Path $venvPath) {
        try {
            $version = & $venvPath --version 2>&1
            Write-Host "  ✓ Found: $venvPath" -ForegroundColor Green
            Write-Host "    Version: $version" -ForegroundColor White
        } catch {}
    }
}

Write-Host ""
Write-Host "4. Searching AppData for Python..." -ForegroundColor Yellow
Get-ChildItem "$env:LOCALAPPDATA\Programs" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  ✓ Found: $($_.FullName)" -ForegroundColor Green
    try {
        $version = & $_.FullName --version 2>&1
        Write-Host "    Version: $version" -ForegroundColor White
    } catch {}
}

Write-Host ""
Write-Host "5. Checking Program Files..." -ForegroundColor Yellow
Get-ChildItem "C:\Program Files" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue -Depth 2 | ForEach-Object {
    Write-Host "  ✓ Found: $($_.FullName)" -ForegroundColor Green
}

Write-Host ""
Write-Host "6. Checking C:\ for Python directories..." -ForegroundColor Yellow
Get-ChildItem "C:\" -Directory -Filter "Python*" -ErrorAction SilentlyContinue | ForEach-Object {
    $pythonExe = Join-Path $_.FullName "python.exe"
    if (Test-Path $pythonExe) {
        Write-Host "  ✓ Found: $pythonExe" -ForegroundColor Green
        try {
            $version = & $pythonExe --version 2>&1
            Write-Host "    Version: $version" -ForegroundColor White
        } catch {}
    }
}

Write-Host ""
Write-Host "7. Checking where command knows about python..." -ForegroundColor Yellow
$wherePython = where.exe python 2>$null
if ($wherePython) {
    Write-Host "  ✓ 'where python' found:" -ForegroundColor Green
    $wherePython | ForEach-Object {
        Write-Host "    $_" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "8. Checking Windows Store Python..." -ForegroundColor Yellow
$storePython = "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe"
if (Test-Path $storePython) {
    Write-Host "  ✓ Found Windows Store Python: $storePython" -ForegroundColor Green
    Write-Host "    (This is a stub - real Python needs to be installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "SEARCH COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copy one of the working Python paths above and use it like:" -ForegroundColor Yellow
Write-Host '  & "C:\path\to\python.exe" -m venv venv' -ForegroundColor White
Write-Host ""
Write-Host "OR if py launcher works:" -ForegroundColor Yellow
Write-Host "  py -m venv venv" -ForegroundColor White
Write-Host ""


