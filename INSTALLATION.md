# Installation Guide - AI Podcast Creator

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Install](#quick-install)
3. [Detailed Installation](#detailed-installation)
4. [GPU Setup](#gpu-setup)
5. [Model Downloads](#model-downloads)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Operating Systems
- **Windows**: 10/11 with WSL2 (recommended) or native
- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 36+
- **macOS**: 12+ (CPU only, no GPU acceleration)

### Hardware - Minimum
- **CPU**: Intel i5 / AMD Ryzen 5 or better
- **RAM**: 16GB
- **Storage**: 50GB free space
- **GPU**: NVIDIA GPU with 6GB VRAM (optional but recommended)

### Hardware - Recommended
- **CPU**: Intel i7 / AMD Ryzen 7 or better
- **RAM**: 32GB
- **Storage**: 100GB NVMe SSD
- **GPU**: NVIDIA GPU with 12GB+ VRAM

### Software Requirements
- Python 3.10 or 3.11
- FFmpeg 5.0+
- Git
- CUDA 11.8+ (for GPU support)

## Quick Install

### For Linux/WSL2 (Recommended)

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3.10 python3-pip ffmpeg git

# 2. Clone/navigate to project
cd AI_Podcast_Creator

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python packages
pip install -r requirements.txt

# 5. Initialize
python -m src.cli.main init

# 6. Test
python -m src.cli.main status
```

### For Windows (Native)

```powershell
# 1. Install Chocolatey (if not installed)
# Visit https://chocolatey.org/install

# 2. Install dependencies
choco install python310 ffmpeg git -y

# 3. Navigate to project
cd AI_Podcast_Creator

# 4. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Initialize
python -m src.cli.main init

# 7. Test
python -m src.cli.main status
```

### For macOS

```bash
# 1. Install Homebrew (if not installed)
# Visit https://brew.sh

# 2. Install dependencies
brew install python@3.10 ffmpeg git

# 3. Navigate to project
cd AI_Podcast_Creator

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install -r requirements.txt

# 6. Initialize
python -m src.cli.main init

# 7. Test
python -m src.cli.main status
```

## Detailed Installation

### Step 1: Python Installation

#### Verify Python Version
```bash
python --version  # Should be 3.10 or 3.11
```

#### Install Python 3.10 (if needed)

**Ubuntu/Debian:**
```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Or use Chocolatey: `choco install python310`

**macOS:**
```bash
brew install python@3.10
```

### Step 2: FFmpeg Installation

#### Verify FFmpeg
```bash
ffmpeg -version
```

#### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**Windows:**
```powershell
choco install ffmpeg
# Or download from https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

### Step 3: Virtual Environment Setup

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify activation (should show venv path)
which python  # Linux/Mac
where python  # Windows
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt

# This may take 10-20 minutes depending on your connection
```

### Step 5: Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys (optional)
nano .env  # or use any text editor

# Review and customize config.yaml
nano config.yaml
```

### Step 6: Initialize System

```bash
python -m src.cli.main init
```

This will:
- Create necessary directories
- Initialize database
- Check system dependencies
- Verify GPU availability

## GPU Setup

### NVIDIA GPU with CUDA

#### Check GPU
```bash
nvidia-smi
```

If command not found, install NVIDIA drivers first.

#### Install CUDA Toolkit

**Linux:**
```bash
# Ubuntu example for CUDA 12.1
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install cuda-12-1
```

**Windows:**
- Download CUDA Toolkit from [NVIDIA website](https://developer.nvidia.com/cuda-downloads)
- Install with default settings

#### Install PyTorch with CUDA

```bash
# Uninstall CPU version if installed
pip uninstall torch torchaudio

# Install CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Verify GPU Setup

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}')"
```

Should output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3080
```

## Model Downloads

### Automatic Downloads (First Run)

Most models download automatically on first use:

```bash
# This will trigger model downloads
python -m src.cli.main create data/scripts/example_welcome.txt
```

### Manual Model Downloads

#### Coqui TTS Models
```bash
# Models download automatically via TTS package
# Location: ~/.local/share/tts/
```

#### SadTalker (for avatar)
```bash
# Clone repository
git clone https://github.com/OpenTalker/SadTalker.git data/models/sadtalker
cd data/models/sadtalker

# Install dependencies
pip install -r requirements.txt

# Download checkpoints
bash scripts/download_models.sh
```

#### Wav2Lip (alternative avatar)
```bash
git clone https://github.com/Rudrabha/Wav2Lip.git data/models/wav2lip
cd data/models/wav2lip

# Download models
wget "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0.0/wav2lip_gan.pth" -O checkpoints/wav2lip_gan.pth
```

#### MusicGen Models
```bash
# Models download automatically via audiocraft
# Sizes: small (~1.5GB), medium (~6GB), large (~13GB)
```

### Check Downloaded Models

```bash
ls -lh data/models/
du -sh data/models/*
```

## Verification

### Run System Status Check

```bash
python -m src.cli.main status
```

Expected output:
```
System Status

Component  Status  Details
─────────────────────────────
Python     ✓       3.10.12
FFmpeg     ✓       Installed
GPU        ✓       NVIDIA GeForce RTX 3080
Models     ✓       42 files
```

### Create Test Podcast

```bash
# Preview audio only (faster test)
python -m src.cli.main create data/scripts/example_welcome.txt --preview

# Full video generation
python -m src.cli.main create data/scripts/example_welcome.txt
```

Check output:
```bash
ls -lh data/outputs/
```

### Run Unit Tests (Optional)

```bash
pytest tests/ -v
```

## Troubleshooting

### Python Import Errors

**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
# Ensure venv is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### FFmpeg Not Found

**Problem**: `FileNotFoundError: FFmpeg not found`

**Solution**:
```bash
# Verify FFmpeg installation
ffmpeg -version

# If not found, install:
# Ubuntu: sudo apt install ffmpeg
# Windows: choco install ffmpeg
# Mac: brew install ffmpeg

# Add to PATH if needed
# Windows: Add C:\ProgramData\chocolatey\bin to PATH
```

### CUDA/GPU Issues

**Problem**: `CUDA not available` or `torch.cuda.is_available() returns False`

**Solution**:
```bash
# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory Errors

**Problem**: `CUDA out of memory`

**Solution**:
1. Close other GPU-intensive applications
2. Reduce batch sizes in config.yaml
3. Use smaller models (MusicGen small)
4. Lower video resolution
5. Enable CPU fallback: `use_gpu: false` in config.yaml

### Permission Errors

**Problem**: `Permission denied` when creating directories

**Solution**:
```bash
# Linux/Mac: Fix permissions
sudo chown -R $USER:$USER AI_Podcast_Creator/
chmod -R 755 AI_Podcast_Creator/

# Windows: Run as administrator or check folder permissions
```

### Slow Generation

**Problem**: Video generation takes very long

**Solutions**:
1. Verify GPU is being used: `nvidia-smi` during generation
2. Use faster models (Piper TTS, MusicGen small)
3. Consider cloud APIs (ElevenLabs, D-ID)
4. Check CPU usage - may be bottleneck
5. Use SSD instead of HDD for data storage

### Model Download Failures

**Problem**: Models fail to download

**Solution**:
```bash
# Check internet connection
# Try manual download with increased timeout
HF_HUB_DOWNLOAD_TIMEOUT=300 python -m src.cli.main create script.txt

# Or download manually and place in data/models/
```

### API Key Issues

**Problem**: API authentication failures

**Solution**:
```bash
# Verify .env file exists
cat .env

# Check API keys are correct
# Ensure no extra spaces or quotes
# Format: API_KEY=your_key_here (no quotes)

# Restart application after changing .env
```

## Docker Installation (Alternative)

If you prefer Docker:

```bash
# Build image
docker compose build

# Initialize
docker compose run podcast-creator init

# Create podcast
docker compose run podcast-creator create data/scripts/example_welcome.txt

# With GPU support (requires nvidia-docker)
docker compose run --gpus all podcast-creator create script.txt
```

## Next Steps

After successful installation:

1. Review and customize `config.yaml`
2. Add API keys to `.env` if using commercial services
3. Prepare your avatar image (1024x1024 PNG)
4. Create custom studio background (1920x1080 JPG)
5. Write your first script
6. Generate your first podcast!

## Getting Help

- Check [README.md](README.md) for usage guide
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [REQUIREMENTS.md](REQUIREMENTS.md) for detailed specs
- Report issues on GitHub

---

**Installation complete!** 🎉 Ready to create amazing podcasts!

