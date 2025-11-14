# Setup GPU Testing Environment
# Ensures GPU tests run locally and frequently

Write-Host "🎮 Setting up GPU Testing Environment" -ForegroundColor Cyan
Write-Host ""

# Check GPU hardware
Write-Host "1. Checking GPU Hardware..." -ForegroundColor Yellow
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    Write-Host "   ✅ NVIDIA GPU detected" -ForegroundColor Green
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | Select-Object -First 1
    Write-Host "   GPU: $gpuInfo" -ForegroundColor White
} else {
    Write-Host "   ❌ No NVIDIA GPU detected" -ForegroundColor Red
    Write-Host "   GPU tests will be skipped" -ForegroundColor Yellow
    exit 0
}

# Check PyTorch
Write-Host ""
Write-Host "2. Checking PyTorch Installation..." -ForegroundColor Yellow
try {
    $torchCheck = python -c "import torch; print('INSTALLED')" 2>&1
    if ($torchCheck -match "INSTALLED") {
        Write-Host "   ✅ PyTorch installed" -ForegroundColor Green
        
        # Check CUDA
        $cudaCheck = python -c "import torch; print('CUDA_AVAILABLE' if torch.cuda.is_available() else 'CUDA_UNAVAILABLE')" 2>&1
        if ($cudaCheck -match "CUDA_AVAILABLE") {
            Write-Host "   ✅ CUDA available" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  CUDA not available (install CUDA-enabled PyTorch)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  PyTorch not installed" -ForegroundColor Yellow
        Write-Host "   Install with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121" -ForegroundColor White
    }
} catch {
    Write-Host "   ⚠️  PyTorch check failed" -ForegroundColor Yellow
}

# Setup PowerShell profile
Write-Host ""
Write-Host "3. Setting up PowerShell Profile..." -ForegroundColor Yellow
$profilePath = $PROFILE.CurrentUserAllHosts
$profileDir = Split-Path -Parent $profilePath

if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    Write-Host "   Created profile directory: $profileDir" -ForegroundColor Green
}

$gpuTestLine = '$env:PY_ENABLE_GPU_TESTS = "1"  # Enable GPU tests for AI Podcast Creator'

if (Test-Path $profilePath) {
    $profileContent = Get-Content $profilePath -Raw
    if ($profileContent -notmatch "PY_ENABLE_GPU_TESTS") {
        Add-Content -Path $profilePath -Value "`n# AI Podcast Creator - GPU Testing`n$gpuTestLine`n"
        Write-Host "   ✅ Added GPU test enablement to profile" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  GPU test enablement already in profile" -ForegroundColor Gray
    }
} else {
    Set-Content -Path $profilePath -Value "# AI Podcast Creator - GPU Testing`n$gpuTestLine`n"
    Write-Host "   ✅ Created profile with GPU test enablement" -ForegroundColor Green
}

Write-Host "   Profile location: $profilePath" -ForegroundColor White

# Enable for current session
Write-Host ""
Write-Host "4. Enabling GPU Tests for Current Session..." -ForegroundColor Yellow
$env:PY_ENABLE_GPU_TESTS = "1"
Write-Host "   ✅ PY_ENABLE_GPU_TESTS=1" -ForegroundColor Green

# Create reminder script
Write-Host ""
Write-Host "5. Creating GPU Test Reminder..." -ForegroundColor Yellow
$reminderScript = @"
# GPU Test Reminder
# Run this weekly or before major commits

Write-Host "🎮 Running GPU Tests..." -ForegroundColor Cyan
`$env:PY_ENABLE_GPU_TESTS = "1"
pytest tests/unit tests/integration -m gpu -v
"@

$reminderPath = Join-Path $PSScriptRoot "run-gpu-tests-reminder.ps1"
Set-Content -Path $reminderPath -Value $reminderScript
Write-Host "   ✅ Created reminder script: $reminderPath" -ForegroundColor Green

Write-Host ""
Write-Host "✅ GPU Testing Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Restart PowerShell to load profile changes" -ForegroundColor White
Write-Host "  2. Run GPU tests: .\scripts\test-gpu.ps1" -ForegroundColor White
Write-Host "  3. Run weekly reminder: .\scripts\run-gpu-tests-reminder.ps1" -ForegroundColor White
Write-Host ""

