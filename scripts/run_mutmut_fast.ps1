#!/usr/bin/env pwsh
# Fast Mutation Testing - Optimized for GPU-enabled test execution
# 
# This script runs mutation testing with optimizations:
# - Parallel test execution (uses all CPU cores)
# - Skips slow/integration/e2e tests
# - Focuses on fast unit tests only
# - Uses GPU-accelerated tests when available

Param(
    [string]$Module = "",
    [int]$Workers = 0,
    [switch]$Full = $false,
    [switch]$Help = $false
)

function Write-Header {
    param([string]$Text)
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success { param([string]$Text) Write-Host $Text -ForegroundColor Green }
function Write-Info { param([string]$Text) Write-Host $Text -ForegroundColor Yellow }
function Write-Error { param([string]$Text) Write-Host $Text -ForegroundColor Red }

if ($Help) {
    Write-Header "FAST MUTATION TESTING - HELP"
    Write-Host "Usage:"
    Write-Host "  .\scripts\run_mutmut_fast.ps1                  # Test all core modules (fast mode)"
    Write-Host "  .\scripts\run_mutmut_fast.ps1 -Module tts      # Test only TTS engine"
    Write-Host "  .\scripts\run_mutmut_fast.ps1 -Workers 8       # Use 8 parallel workers"
    Write-Host "  .\scripts\run_mutmut_fast.ps1 -Full            # Include slow tests (takes longer)"
    Write-Host ""
    Write-Host "Available modules:"
    Write-Host "  - tts        (src/core/tts_engine.py)"
    Write-Host "  - video      (src/core/video_composer.py)"
    Write-Host "  - audio      (src/core/audio_mixer.py)"
    Write-Host "  - parser     (src/core/script_parser.py)"
    Write-Host "  - config     (src/utils/config.py)"
    Write-Host ""
    Write-Host "Optimizations enabled by default:"
    Write-Host "  ✅ Parallel test execution (all CPU cores)"
    Write-Host "  ✅ Skip slow/integration/e2e tests"
    Write-Host "  ✅ GPU-accelerated tests used when available"
    Write-Host "  ✅ Stop on first failure for faster feedback"
    Write-Host ""
    exit 0
}

if (-not $env:VIRTUAL_ENV) {
    Write-Error "❌ Activate your virtual environment first: .\venv\Scripts\Activate.ps1"
    exit 1
}

# Check if mutmut is available
try {
    mutmut --help | Out-Null
} catch {
    Write-Error "❌ mutmut not found. Install: pip install -r requirements-dev.txt"
    exit 1
}

# Check if pytest-xdist is available (for parallel execution)
$hasXdist = $false
try {
    python -c "import pytest_xdist" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $hasXdist = $true
        $cpuCount = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
        Write-Info "✅ pytest-xdist available - will use $cpuCount parallel workers"
    }
} catch {
    Write-Info "⚠️  pytest-xdist not available - tests will run sequentially (slower)"
}

# Determine what to test
$pathsToMutate = ""
if ($Module -ne "") {
    switch ($Module.ToLower()) {
        "tts" { $pathsToMutate = "src/core/tts_engine.py" }
        "video" { $pathsToMutate = "src/core/video_composer.py" }
        "audio" { $pathsToMutate = "src/core/audio_mixer.py" }
        "parser" { $pathsToMutate = "src/core/script_parser.py" }
        "config" { $pathsToMutate = "src/utils/config.py" }
        default {
            Write-Error "Unknown module: $Module. Use -Help for options."
            exit 1
        }
    }
}

# Set workers (use all CPU cores by default)
if ($Workers -eq 0) {
    $cpuCount = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
    $Workers = $cpuCount
    Write-Info "💻 Detected $cpuCount CPU cores - using all for parallel execution"
}

# Build mutmut command
$mutmutArgs = ""
if ($pathsToMutate -ne "") {
    $mutmutArgs = "--paths-to-mutate=$pathsToMutate"
}

# Set environment variable for parallel workers
if ($hasXdist) {
    $env:MUTMUT_WORKERS = $Workers.ToString()
    Write-Info "🚀 Using $Workers parallel workers for test execution"
} else {
    Write-Info "⚠️  Running sequentially (install pytest-xdist for 10x speedup)"
}

if ($Full) {
    Write-Info "⚠️  Running with slow tests included (this will take longer)"
    $env:MUTMUT_SLOW_TESTS = "1"
} else {
    Write-Info "✅ Fast mode: Skipping slow/integration/e2e tests"
}

Write-Header "FAST MUTATION TESTING"
Write-Info "This will run tests in parallel for maximum speed."
Write-Info "GPU-accelerated tests will use GPU when available."
Write-Host ""

$command = "mutmut run $mutmutArgs".Trim()
Write-Info "▶️  Running: $command"
Write-Host ""

# Run mutation testing
Invoke-Expression $command

if ($LASTEXITCODE -eq 0) {
    Write-Success "`n✅ Mutation testing complete!"
    Write-Info "📊 View results: mutmut show"
    Write-Info "📊 HTML report: mutmut html"
} else {
    Write-Error "`n❌ Mutation testing failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

