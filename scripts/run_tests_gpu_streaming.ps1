# Real-time streaming wrapper for GPU batched tests
# Provides active log output with timestamps

param(
    [float]$RamTarget = 70.0,
    [float]$Cooldown = 1.0,
    [int]$Workers = 0,
    [switch]$SkipCpuFollowup,
    [switch]$Cov
)

$ErrorActionPreference = "Continue"
$env:GPU_SAFE_MODE = "1"
$env:GPU_MAX_SPLIT_MB = "64"
$env:PYTHONUNBUFFERED = "1"

$logFile = "gpu_batched_streaming_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$scriptRoot = Split-Path -Parent $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GPU Batched Tests - Real-Time Streaming" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Log file: $logFile" -ForegroundColor Yellow
Write-Host ""

# Build command
$pythonExe = Join-Path $scriptRoot ".venv312\Scripts\python.exe"
$testScript = Join-Path $scriptRoot "scripts\run_tests_gpu_batched.py"

$args = @(
    "-u", $testScript,
    "--ram-target", $RamTarget,
    "--cooldown", $Cooldown,
    "--workers", $Workers
)

if ($SkipCpuFollowup) {
    $args += "--skip-cpu-followup"
}

if ($Cov) {
    $args += "--cov"
}

# Start process with real-time output
$process = Start-Process -FilePath $pythonExe -ArgumentList $args -NoNewWindow -PassThru -RedirectStandardOutput "stdout.tmp" -RedirectStandardError "stderr.tmp"

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Process started (PID: $($process.Id))" -ForegroundColor Green
Write-Host ""

# Monitor and stream output
$stdoutReader = [System.IO.StreamReader]::new([System.IO.File]::OpenRead("stdout.tmp"))
$stderrReader = [System.IO.StreamReader]::new([System.IO.File]::OpenRead("stderr.tmp"))

$buffer = New-Object System.Text.StringBuilder

while (-not $process.HasExited) {
    # Read stdout
    while ($stdoutReader.Peek() -ge 0) {
        $line = $stdoutReader.ReadLine()
        if ($line) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            Write-Host "[$timestamp] $line"
            Add-Content -Path $logFile -Value "[$timestamp] $line"
        }
    }
    
    # Read stderr
    while ($stderrReader.Peek() -ge 0) {
        $line = $stderrReader.ReadLine()
        if ($line) {
            $timestamp = Get-Date -Format "HH:mm:ss"
            Write-Host "[$timestamp] $line" -ForegroundColor Red
            Add-Content -Path $logFile -Value "[$timestamp] [ERROR] $line"
        }
    }
    
    Start-Sleep -Milliseconds 100
}

# Read any remaining output
while (-not $stdoutReader.EndOfStream) {
    $line = $stdoutReader.ReadLine()
    if ($line) {
        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "[$timestamp] $line"
        Add-Content -Path $logFile -Value "[$timestamp] $line"
    }
}

while (-not $stderrReader.EndOfStream) {
    $line = $stderrReader.ReadLine()
    if ($line) {
        $timestamp = Get-Date -Format "HH:mm:ss"
        Write-Host "[$timestamp] $line" -ForegroundColor Red
        Add-Content -Path $logFile -Value "[$timestamp] [ERROR] $line"
    }
}

$stdoutReader.Close()
$stderrReader.Close()

# Cleanup temp files
Remove-Item "stdout.tmp" -ErrorAction SilentlyContinue
Remove-Item "stderr.tmp" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Process completed with exit code: $($process.ExitCode)" -ForegroundColor $(if ($process.ExitCode -eq 0) { "Green" } else { "Red" })
Write-Host "Full log: $logFile" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

exit $process.ExitCode

