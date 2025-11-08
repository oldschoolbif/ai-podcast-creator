# Kitchen Cleanup Guide

## Cleanup Checklist

### 1. Test Outputs & Generated Files
- [ ] Remove test video/audio files from `Creations/MMedia/`
- [ ] Clean up temporary test files
- [ ] Remove pytest cache directories
- [ ] Remove coverage HTML reports

### 2. Python Cache & Build Artifacts
- [ ] Remove `__pycache__` directories (outside venv)
- [ ] Remove `.pyc` files
- [ ] Remove `.egg-info` directories

### 3. Logs & Temporary Files
- [ ] Clear log files
- [ ] Remove temporary test files
- [ ] Clean up test artifacts

### 4. Coverage Reports
- [ ] Remove `htmlcov/` directory
- [ ] Remove `.coverage` file
- [ ] Remove `coverage.xml` and `coverage.json`

### 5. Documentation Cleanup
- [ ] Review and consolidate documentation files
- [ ] Remove outdated/duplicate docs (keep essential ones)

## Cleanup Commands

Run these commands to clean up:

```powershell
cd D:\dev\AI_Podcast_Creator

# Remove test outputs (videos, audio)
Get-ChildItem -Path "Creations\MMedia" -Recurse -File | Where-Object { $_.Extension -in ".mp4",".mp3",".wav" } | Remove-Item -Force

# Remove pytest cache
Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" | Where-Object { $_.FullName -notlike "*\venv\*" } | Remove-Item -Recurse -Force

# Remove coverage files
Remove-Item -Path "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".coverage" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "coverage.xml" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "coverage.json" -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue

# Remove Python cache files (outside venv)
Get-ChildItem -Path "." -Recurse -File -Filter "*.pyc" | Where-Object { $_.FullName -notlike "*\venv\*" } | Remove-Item -Force
Get-ChildItem -Path "." -Recurse -File -Filter "*.pyo" | Where-Object { $_.FullName -notlike "*\venv\*" } | Remove-Item -Force

# Remove .egg-info directories (outside venv)
Get-ChildItem -Path "." -Recurse -Directory -Filter "*.egg-info" | Where-Object { $_.FullName -notlike "*\venv\*" } | Remove-Item -Recurse -Force

# Remove log files
Get-ChildItem -Path "." -Recurse -File -Filter "*.log" | Where-Object { $_.FullName -notlike "*\venv\*" -and $_.FullName -notlike "*\logs\*" } | Remove-Item -Force

# Clean up test artifacts
Remove-Item -Path "test_results.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "report.html" -Force -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
```

## What to Keep

### Essential Files
- ✅ All source code (`src/`)
- ✅ All tests (`tests/`)
- ✅ Configuration files (`config.yaml`, `requirements.txt`, etc.)
- ✅ Documentation (README, guides, etc.)
- ✅ `.gitignore`
- ✅ GitHub Actions workflows

### Static Assets
- ✅ `Creations/MMedia/JE_Static_Image.jpg` (static image used for testing)
- ✅ Example scripts in `Creations/Scripts/`

## What to Remove

### Generated Files
- ❌ Test videos (`.mp4` files in `Creations/MMedia/`)
- ❌ Test audio (`.mp3`, `.wav` files from tests)
- ❌ Coverage HTML reports (`htmlcov/`)
- ❌ Coverage data files (`.coverage`, `coverage.xml`, `coverage.json`)

### Cache & Build Artifacts
- ❌ `__pycache__` directories (outside `venv/`)
- ❌ `.pyc`, `.pyo` files (outside `venv/`)
- ❌ `.egg-info` directories (outside `venv/`)
- ❌ `.pytest_cache` directory

### Temporary Files
- ❌ Test result files (`test_results.txt`, `report.html`)
- ❌ Temporary log files (outside `logs/` directory)

## After Cleanup

1. Verify `.gitignore` is comprehensive
2. Run tests to ensure everything still works
3. Check git status to verify no important files are staged for deletion
4. Commit cleanup changes

