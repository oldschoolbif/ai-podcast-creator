# Check GPU test dependencies
Write-Host "Checking GPU test dependencies..." -ForegroundColor Cyan

# Check PyTorch
Write-Host "`n1. Checking PyTorch..." -ForegroundColor Yellow
try {
    $torchCheck = python -c "import torch; print(f'{torch.__version__}|{torch.cuda.is_available()}')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $parts = $torchCheck -split '\|'
        Write-Host "   PyTorch: $($parts[0])" -ForegroundColor Green
        Write-Host "   CUDA Available: $($parts[1])" -ForegroundColor $(if ($parts[1] -eq "True") { "Green" } else { "Yellow" })
    } else {
        Write-Host "   PyTorch: NOT INSTALLED" -ForegroundColor Red
    }
} catch {
    Write-Host "   PyTorch: NOT INSTALLED" -ForegroundColor Red
}

# Check audiocraft
Write-Host "`n2. Checking AudioCraft..." -ForegroundColor Yellow
$audiocraftCheck = python -c "import sys; print('audiocraft' in sys.modules)" 2>&1
if ($audiocraftCheck -eq "True") {
    Write-Host "   AudioCraft: INSTALLED" -ForegroundColor Green
} else {
    Write-Host "   AudioCraft: NOT INSTALLED" -ForegroundColor Yellow
}

# Check TTS (Coqui)
Write-Host "`n3. Checking Coqui TTS..." -ForegroundColor Yellow
try {
    $ttsCheck = python -c "import TTS; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Coqui TTS: INSTALLED" -ForegroundColor Green
    } else {
        Write-Host "   Coqui TTS: NOT INSTALLED" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   Coqui TTS: NOT INSTALLED" -ForegroundColor Yellow
}

# Check freezegun
Write-Host "`n4. Checking freezegun..." -ForegroundColor Yellow
try {
    $freezeCheck = python -c "from freezegun import freeze_time; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   freezegun: INSTALLED" -ForegroundColor Green
    } else {
        Write-Host "   freezegun: ERROR - $freezeCheck" -ForegroundColor Red
    }
} catch {
    Write-Host "   freezegun: ERROR" -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Cyan

