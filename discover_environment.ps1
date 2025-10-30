# Comprehensive Environment Discovery
# Learn about the system we're working in

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  ENVIRONMENT DISCOVERY" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# System Info
Write-Host "SYSTEM INFORMATION:" -ForegroundColor Yellow
Write-Host "  OS: $([System.Environment]::OSVersion.VersionString)" -ForegroundColor White
Write-Host "  Computer: $env:COMPUTERNAME" -ForegroundColor White
Write-Host "  User: $env:USERNAME" -ForegroundColor White
Write-Host "  PowerShell: $($PSVersionTable.PSVersion)" -ForegroundColor White
Write-Host ""

# Python
Write-Host "PYTHON:" -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    $pythonPath = (Get-Command python).Source
    Write-Host "  Version: $pythonVersion" -ForegroundColor Green
    Write-Host "  Path: $pythonPath" -ForegroundColor White
} catch {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
}
Write-Host ""

# Check for py launcher
Write-Host "PY LAUNCHER:" -ForegroundColor Yellow
try {
    $pyVersion = py --version 2>&1
    Write-Host "  Version: $pyVersion" -ForegroundColor Green
    py -0 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
} catch {
    Write-Host "  ✗ py launcher not found" -ForegroundColor Red
}
Write-Host ""

# Git
Write-Host "GIT:" -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "  Version: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Git not found" -ForegroundColor Red
}
Write-Host ""

# Docker
Write-Host "DOCKER:" -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  Version: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker not found" -ForegroundColor Red
}
Write-Host ""

# Node.js
Write-Host "NODE.JS:" -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  Version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found" -ForegroundColor Red
}
Write-Host ""

# Current Project
Write-Host "CURRENT PROJECT:" -ForegroundColor Yellow
$currentDir = Get-Location
Write-Host "  Directory: $currentDir" -ForegroundColor White
Write-Host "  Has venv: $(Test-Path 'venv')" -ForegroundColor White
Write-Host "  Has requirements.txt: $(Test-Path 'requirements.txt')" -ForegroundColor White
Write-Host "  Has requirements-test.txt: $(Test-Path 'requirements-test.txt')" -ForegroundColor White
Write-Host ""

# Other Projects
Write-Host "OTHER PROJECTS IN D:\DEV:" -ForegroundColor Yellow
Get-ChildItem d:\dev -Directory | ForEach-Object {
    $hasVenv = Test-Path (Join-Path $_.FullName "venv")
    $hasDocker = Test-Path (Join-Path $_.FullName "docker-compose.yml")
    $hasPython = Test-Path (Join-Path $_.FullName "*.py")
    
    if ($hasVenv -or $hasDocker -or $hasPython) {
        Write-Host "  $($_.Name):" -ForegroundColor White
        if ($hasVenv) { Write-Host "    - Has venv" -ForegroundColor Gray }
        if ($hasDocker) { Write-Host "    - Has Docker" -ForegroundColor Gray }
    }
}
Write-Host ""

# GPU Check
Write-Host "GPU:" -ForegroundColor Yellow
try {
    $gpu = Get-WmiObject Win32_VideoController | Select-Object -First 1
    Write-Host "  Name: $($gpu.Name)" -ForegroundColor White
    Write-Host "  Driver: $($gpu.DriverVersion)" -ForegroundColor White
    
    # Try nvidia-smi
    try {
        $nvidiaSmi = nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>&1
        Write-Host "  NVIDIA:" -ForegroundColor Green
        Write-Host "    $nvidiaSmi" -ForegroundColor White
    } catch {
        Write-Host "  NVIDIA: Not available" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Could not detect GPU" -ForegroundColor Red
}
Write-Host ""

# Available Memory
Write-Host "MEMORY:" -ForegroundColor Yellow
$mem = Get-CimInstance Win32_OperatingSystem
$totalMem = [math]::Round($mem.TotalVisibleMemorySize / 1MB, 2)
$freeMem = [math]::Round($mem.FreePhysicalMemory / 1MB, 2)
Write-Host "  Total: $totalMem GB" -ForegroundColor White
Write-Host "  Free: $freeMem GB" -ForegroundColor White
Write-Host ""

# Disk Space
Write-Host "DISK SPACE (D:):" -ForegroundColor Yellow
$disk = Get-PSDrive D
Write-Host "  Used: $([math]::Round($disk.Used / 1GB, 2)) GB" -ForegroundColor White
Write-Host "  Free: $([math]::Round($disk.Free / 1GB, 2)) GB" -ForegroundColor White
Write-Host ""

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  DISCOVERY COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

