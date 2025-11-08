# FFmpeg Installation Guide for Windows

## Why FFmpeg?
- **10-20x faster** video encoding with your RTX 4060 GPU (NVENC)
- Lower memory usage (streaming vs loading entire video)
- Primary method for production use

## Installation Options

### Option 1: Chocolatey (Recommended - Easiest)
```powershell
# Install Chocolatey first (if not installed)
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg -y

# Verify
ffmpeg -version
```

### Option 2: Scoop
```powershell
# Install Scoop first (if not installed)
# Run PowerShell, then:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Install FFmpeg
scoop install ffmpeg

# Verify
ffmpeg -version
```

### Option 3: Manual Download (No Package Manager)
1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Choose: **ffmpeg-release-essentials.zip**
3. Extract to: `C:\ffmpeg`
4. Add to PATH:
   - System Properties → Environment Variables
   - Add `C:\ffmpeg\bin` to PATH
5. Restart PowerShell/terminal
6. Verify: `ffmpeg -version`

### Option 4: Via pip (Alternative - but not recommended)
```powershell
pip install ffmpeg-python
```
Note: This only installs Python bindings, not FFmpeg binary. You still need FFmpeg installed separately.

## After Installation

Verify FFmpeg works:
```powershell
ffmpeg -version
ffmpeg -encoders | Select-String "h264_nvenc"  # Should show NVENC if GPU supported
```

## Current Code Status

✅ **Code Updated**: FFmpeg is now PRIMARY, MoviePy is fallback
- Tries FFmpeg first (for GPU acceleration)
- Falls back to MoviePy if FFmpeg unavailable (for testing)

## Testing

Once installed, run:
```powershell
cd D:\dev\AI_Podcast_Creator
python -m src.cli.main create test_script.txt --visualize -o test_video
```

You should see: `✓ Using GPU-accelerated H.264 encoding (NVENC)` if GPU is available!

