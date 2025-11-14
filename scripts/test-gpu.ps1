# Run GPU tests locally
# Requires: PY_ENABLE_GPU_TESTS=1 and CUDA-capable GPU

Write-Host "🎮 Running GPU Tests..." -ForegroundColor Cyan
Write-Host ""

# Check if GPU tests are enabled
if ($env:PY_ENABLE_GPU_TESTS -ne "1") {
    Write-Host "⚠️  GPU tests are disabled. Set PY_ENABLE_GPU_TESTS=1 to enable." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable GPU tests:" -ForegroundColor Yellow
    Write-Host "  `$env:PY_ENABLE_GPU_TESTS = `"1`"" -ForegroundColor White
    Write-Host ""
    Write-Host "Enabling GPU tests for this session..." -ForegroundColor Yellow
    $env:PY_ENABLE_GPU_TESTS = "1"
}

# Check CUDA availability
Write-Host "Checking GPU availability..." -ForegroundColor Yellow
try {
    $torchCheck = python -c "import torch; print('CUDA_AVAILABLE' if torch.cuda.is_available() else 'CUDA_UNAVAILABLE')" 2>&1
    if ($torchCheck -match "CUDA_AVAILABLE") {
        Write-Host "✅ CUDA GPU detected!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No CUDA GPU detected. GPU tests will be skipped." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  PyTorch not installed or CUDA check failed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Running GPU-marked tests..." -ForegroundColor Cyan
Write-Host ""

# Run GPU tests with verbose output
pytest tests/unit tests/integration -m gpu -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All GPU tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Some GPU tests failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Note: GPU tests require:" -ForegroundColor Yellow
    Write-Host "  1. PY_ENABLE_GPU_TESTS=1" -ForegroundColor White
    Write-Host "  2. NVIDIA GPU with CUDA support" -ForegroundColor White
    Write-Host "  3. CUDA-enabled PyTorch installed" -ForegroundColor White
    exit 1
}

