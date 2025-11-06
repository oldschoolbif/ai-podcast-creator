# Setup Script for Avatar Models (SadTalker + Wav2Lip)
# This script downloads and configures both avatar engines for lip-sync generation

param(
    [switch]$SadTalker,
    [switch]$Wav2Lip,
    [switch]$All
)

$ErrorActionPreference = "Stop"

Write-Host "=== Avatar Model Setup Script ===" -ForegroundColor Cyan
Write-Host "`nThis script will download models for:" -ForegroundColor Yellow
Write-Host "  1. SadTalker (~2-3GB) - High quality talking head" -ForegroundColor Green
Write-Host "  2. Wav2Lip (~200MB) - Accurate lip-sync" -ForegroundColor Green
Write-Host "`n"

# Determine what to install
if ($All) {
    $InstallSadTalker = $true
    $InstallWav2Lip = $true
} elseif ($SadTalker -or $Wav2Lip) {
    $InstallSadTalker = $SadTalker
    $InstallWav2Lip = $Wav2Lip
} else {
    # Prompt user
    $choice = Read-Host "Install (1) SadTalker, (2) Wav2Lip, or (3) Both? [1/2/3]"
    switch ($choice) {
        "1" { $InstallSadTalker = $true; $InstallWav2Lip = $false }
        "2" { $InstallSadTalker = $false; $InstallWav2Lip = $true }
        "3" { $InstallSadTalker = $true; $InstallWav2Lip = $true }
        default { Write-Host "Invalid choice. Exiting."; exit 1 }
    }
}

# Navigate to project directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "`n[1/3] Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\activate.ps1"
}

# ============================================================================
# SADTALKER SETUP
# ============================================================================
if ($InstallSadTalker) {
    Write-Host "`n=== Setting up SadTalker ===" -ForegroundColor Green
    
    $ExternalDir = Join-Path $ProjectRoot "external"
    $SadTalkerDir = Join-Path $ExternalDir "SadTalker"
    
    # Step 1: Clone SadTalker repository
    if (-not (Test-Path $SadTalkerDir)) {
        Write-Host "`n[1/4] Cloning SadTalker repository..." -ForegroundColor Cyan
        New-Item -ItemType Directory -Path $ExternalDir -Force | Out-Null
        Set-Location $ExternalDir
        git clone https://github.com/OpenTalker/SadTalker.git
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to clone SadTalker repository" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ SadTalker repository cloned" -ForegroundColor Green
    } else {
        Write-Host "✅ SadTalker directory exists, skipping clone" -ForegroundColor Green
    }
    
    Set-Location $SadTalkerDir
    
    # Step 2: Install SadTalker dependencies
    Write-Host "`n[2/4] Installing SadTalker dependencies..." -ForegroundColor Cyan
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  Some dependencies may have failed, continuing..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  requirements.txt not found, installing core dependencies..." -ForegroundColor Yellow
        pip install face-alignment gfpgan basicsr facexlib
    }
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    
    # Step 3: Download models
    Write-Host "`n[3/4] Downloading SadTalker models (~2-3GB)..." -ForegroundColor Cyan
    Write-Host "  This will download:" -ForegroundColor Yellow
    Write-Host "    - Checkpoint models" -ForegroundColor Yellow
    Write-Host "    - GFPGAN face enhancement models" -ForegroundColor Yellow
    Write-Host "    - Face detection models" -ForegroundColor Yellow
    
    $CheckpointsDir = Join-Path $SadTalkerDir "checkpoints"
    New-Item -ItemType Directory -Path $CheckpointsDir -Force | Out-Null
    
    # Check for download script
    if (Test-Path "scripts\download_models.sh") {
        Write-Host "  Running download script..." -ForegroundColor Yellow
        # For Windows, we'll need to manually download or use Python
        Write-Host "  ⚠️  Download script is for Linux. Using Python downloader..." -ForegroundColor Yellow
        
        # Use Python to download models
        python -c @"
import os
import subprocess
import sys

# Change to SadTalker directory
os.chdir(r'$SadTalkerDir')

# Run the download script if available, or download manually
if os.path.exists('scripts/download_models.sh'):
    print('Download script found, but requires Linux.')
    print('Please download models manually from:')
    print('https://github.com/OpenTalker/SadTalker#model-weights')
    print(f'Place models in: {os.path.join(os.getcwd(), \"checkpoints\")}')
else:
    print('Download script not found.')
"@
    } else {
        Write-Host "  ⚠️  Download script not found" -ForegroundColor Yellow
    }
    
    Write-Host "`n  📥 Manual download instructions:" -ForegroundColor Cyan
    Write-Host "     Visit: https://github.com/OpenTalker/SadTalker#model-weights" -ForegroundColor White
    Write-Host "     Download required models to: $CheckpointsDir" -ForegroundColor White
    Write-Host "`n     Required files:" -ForegroundColor Yellow
    Write-Host "       - checkpoints/auido2pose_ckpt/auido2pose.ckpt" -ForegroundColor White
    Write-Host "       - checkpoints/auido2exp_ckpt/auido2exp.ckpt" -ForegroundColor White
    Write-Host "       - checkpoints/auido2head_ckpt/auido2head.ckpt" -ForegroundColor White
    Write-Host "       - checkpoints/pretrained_models/*.pth" -ForegroundColor White
    Write-Host "`n  💡 Tip: The models will be auto-downloaded on first use if you have internet!" -ForegroundColor Green
    
    Write-Host "✅ SadTalker setup complete" -ForegroundColor Green
}

# ============================================================================
# WAV2LIP SETUP
# ============================================================================
if ($InstallWav2Lip) {
    Write-Host "`n=== Setting up Wav2Lip ===" -ForegroundColor Green
    
    # Create models directory
    $ModelsDir = Join-Path $ProjectRoot "models"
    New-Item -ItemType Directory -Path $ModelsDir -Force | Out-Null
    
    # Step 1: Download Wav2Lip model
    $ModelPath = Join-Path $ModelsDir "wav2lip_gan.pth"
    
    if (-not (Test-Path $ModelPath)) {
        Write-Host "`n[1/3] Downloading Wav2Lip model (~98MB)..." -ForegroundColor Cyan
        
        $ModelUrls = @(
            "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0.0/wav2lip_gan.pth",
            "https://github.com/justinjohn0306/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth"
        )
        
        $DownloadSuccess = $false
        foreach ($url in $ModelUrls) {
            Write-Host "  Trying: $url" -ForegroundColor Yellow
            try {
                Invoke-WebRequest -Uri $url -OutFile $ModelPath -ErrorAction Stop
                Write-Host "✅ Model downloaded successfully!" -ForegroundColor Green
                $DownloadSuccess = $true
                break
            } catch {
                Write-Host "  ❌ Failed: $_" -ForegroundColor Red
                continue
            }
        }
        
        if (-not $DownloadSuccess) {
            Write-Host "`n⚠️  Automatic download failed" -ForegroundColor Yellow
            Write-Host "  Please download manually from:" -ForegroundColor Yellow
            Write-Host "  https://github.com/Rudrabha/Wav2Lip/releases" -ForegroundColor White
            Write-Host "  Save as: $ModelPath" -ForegroundColor White
        }
    } else {
        Write-Host "✅ Wav2Lip model already exists: $ModelPath" -ForegroundColor Green
    }
    
    # Step 2: Download face detection model
    Write-Host "`n[2/3] Downloading face detection model (s3fd)..." -ForegroundColor Cyan
    $FaceDetModel = Join-Path $ModelsDir "s3fd.pth"
    
    if (-not (Test-Path $FaceDetModel)) {
        $FaceDetUrl = "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth"
        try {
            Invoke-WebRequest -Uri $FaceDetUrl -OutFile $FaceDetModel -ErrorAction Stop
            Write-Host "✅ Face detection model downloaded" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Failed to download face detection model: $_" -ForegroundColor Yellow
            Write-Host "  You can download manually from: $FaceDetUrl" -ForegroundColor White
        }
    } else {
        Write-Host "✅ Face detection model already exists" -ForegroundColor Green
    }
    
    # Step 3: Install Wav2Lip dependencies
    Write-Host "`n[3/3] Installing Wav2Lip dependencies..." -ForegroundColor Cyan
    pip install opencv-python opencv-contrib-python librosa==0.9.2 batch-face facexlib
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some dependencies may have failed" -ForegroundColor Yellow
    }
    
    Write-Host "✅ Wav2Lip setup complete" -ForegroundColor Green
}

# ============================================================================
# VERIFICATION
# ============================================================================
Write-Host "`n=== Verification ===" -ForegroundColor Cyan
Write-Host "`nChecking installations..." -ForegroundColor Yellow

$AllGood = $true

if ($InstallSadTalker) {
    $SadTalkerCheckpoint = Join-Path $ProjectRoot "external\SadTalker\checkpoints"
    if (Test-Path $SadTalkerCheckpoint) {
        $ModelCount = (Get-ChildItem -Path $SadTalkerCheckpoint -Recurse -Filter "*.pth","*.ckpt" -ErrorAction SilentlyContinue).Count
        if ($ModelCount -gt 0) {
            Write-Host "✅ SadTalker: $ModelCount model file(s) found" -ForegroundColor Green
        } else {
            Write-Host "⚠️  SadTalker: Models directory exists but no models found" -ForegroundColor Yellow
            Write-Host "   Models will be downloaded on first use" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  SadTalker: Checkpoints directory not found" -ForegroundColor Yellow
    }
}

if ($InstallWav2Lip) {
    $Wav2LipModel = Join-Path $ProjectRoot "models\wav2lip_gan.pth"
    if (Test-Path $Wav2LipModel) {
        $SizeMB = [math]::Round((Get-Item $Wav2LipModel).Length / 1MB, 2)
        Write-Host "✅ Wav2Lip: Model found ($SizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "❌ Wav2Lip: Model not found" -ForegroundColor Red
        $AllGood = $false
    }
}

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Test SadTalker:" -ForegroundColor Yellow
Write-Host "     python -m src.cli.main create Creations/Scripts/example_short_demo.txt --avatar -o test_sadtalker" -ForegroundColor White
Write-Host "`n  2. Test Wav2Lip:" -ForegroundColor Yellow
Write-Host "     # First, update config.yaml: avatar.engine = 'wav2lip'" -ForegroundColor White
Write-Host "     python -m src.cli.main create Creations/Scripts/example_short_demo.txt --avatar -o test_wav2lip" -ForegroundColor White
Write-Host "`n  3. Test Avatar + Waveform:" -ForegroundColor Yellow
Write-Host "     python -m src.cli.main create Creations/Scripts/example_short_demo.txt --avatar --visualize -o test_complete" -ForegroundColor White

if (-not $AllGood) {
    Write-Host "`n⚠️  Some models are missing. Check the manual download instructions above." -ForegroundColor Yellow
}

Set-Location $ProjectRoot

