# Ensure GPU Tests Run Locally
# This script helps ensure GPU tests run frequently during development

Write-Host "🎮 GPU Test Automation Setup" -ForegroundColor Cyan
Write-Host ""

# Check current GPU test configuration
Write-Host "Current Configuration:" -ForegroundColor Yellow
$gpuEnabled = $env:PY_ENABLE_GPU_TESTS
if ($gpuEnabled -eq "1") {
    Write-Host "  ✅ PY_ENABLE_GPU_TESTS=1 (enabled)" -ForegroundColor Green
} else {
    Write-Host "  ❌ PY_ENABLE_GPU_TESTS=$gpuEnabled (disabled)" -ForegroundColor Red
}

# Check GPU availability
Write-Host ""
Write-Host "GPU Hardware Check:" -ForegroundColor Yellow
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    Write-Host "  ✅ nvidia-smi found - NVIDIA GPU detected" -ForegroundColor Green
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | Select-Object -First 1
    Write-Host "  GPU: $gpuInfo" -ForegroundColor White
} else {
    Write-Host "  ⚠️  nvidia-smi not found - no NVIDIA GPU" -ForegroundColor Yellow
}

# Check PyTorch CUDA
Write-Host ""
Write-Host "PyTorch CUDA Check:" -ForegroundColor Yellow
try {
    $torchCheck = python -c "import torch; print('CUDA_AVAILABLE' if torch.cuda.is_available() else 'CUDA_UNAVAILABLE')" 2>&1
    if ($torchCheck -match "CUDA_AVAILABLE") {
        Write-Host "  ✅ PyTorch CUDA available" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  PyTorch installed but CUDA not available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  PyTorch not installed or check failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Recommendations:" -ForegroundColor Cyan
Write-Host ""

# Recommendation 1: Add to PowerShell profile
$profilePath = $PROFILE.CurrentUserAllHosts
Write-Host "1. Add to PowerShell Profile ($profilePath):" -ForegroundColor Yellow
Write-Host "   `$env:PY_ENABLE_GPU_TESTS = `"1`"" -ForegroundColor White
Write-Host ""

# Recommendation 2: Update test scripts
Write-Host "2. Run GPU tests before pushing:" -ForegroundColor Yellow
Write-Host "   .\scripts\test-gpu.ps1" -ForegroundColor White
Write-Host ""

# Recommendation 3: Add to pre-push hook
Write-Host "3. Add GPU test check to pre-push.ps1 (optional):" -ForegroundColor Yellow
Write-Host "   # Add GPU test run if GPU available" -ForegroundColor White
Write-Host ""

# Recommendation 4: Scheduled runs
Write-Host "4. Run GPU tests regularly:" -ForegroundColor Yellow
Write-Host "   - Before major commits" -ForegroundColor White
Write-Host "   - Weekly/daily on GPU machines" -ForegroundColor White
Write-Host "   - After GPU-related code changes" -ForegroundColor White
Write-Host ""

Write-Host "Current Status:" -ForegroundColor Cyan
if ($gpuEnabled -eq "1" -and (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    Write-Host "  ✅ Ready to run GPU tests!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run GPU tests now? (Y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host ""
        .\scripts\test-gpu.ps1
    }
} else {
    Write-Host "  ⚠️  GPU tests not enabled or GPU not available" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable GPU tests:" -ForegroundColor Yellow
    Write-Host "  `$env:PY_ENABLE_GPU_TESTS = `"1`"" -ForegroundColor White
}

