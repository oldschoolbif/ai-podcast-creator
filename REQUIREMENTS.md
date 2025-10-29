# AI Podcast Creator - Technical Requirements

## Core Dependencies

### Python Packages

```plaintext
# Core Framework
python>=3.10
typer>=0.9.0              # Modern CLI framework
rich>=13.0.0              # Beautiful terminal output
pydantic>=2.0.0           # Data validation

# AI/ML Libraries
torch>=2.0.0              # PyTorch for ML models
torchaudio>=2.0.0         # Audio processing with PyTorch
transformers>=4.30.0      # HuggingFace transformers
diffusers>=0.20.0         # Stable Diffusion models
accelerate>=0.20.0        # Model acceleration

# TTS Engines
TTS>=0.22.0               # Coqui TTS (open source)
elevenlabs>=0.2.0         # ElevenLabs API client (optional)
azure-cognitiveservices-speech>=1.31.0  # Azure TTS (optional)
piper-tts>=1.2.0          # Piper TTS (optional)

# Audio Processing
pydub>=0.25.1             # Audio manipulation
librosa>=0.10.0           # Audio analysis
soundfile>=0.12.1         # Audio file I/O
scipy>=1.11.0             # Signal processing

# Music Generation
audiocraft>=1.0.0         # Meta's AudioCraft (MusicGen)
# OR
# mubert>=0.1.0           # Mubert API (alternative)

# Video Processing
moviepy>=1.0.3            # Video editing
opencv-python>=4.8.0      # Computer vision
pillow>=10.0.0            # Image processing
imageio>=2.31.0           # Image/video I/O
imageio-ffmpeg>=0.4.9     # FFmpeg backend

# Avatar/Talking Head
# Note: These may need manual installation
# sadtalker                # Requires separate installation
# wav2lip                  # Requires separate installation

# Database
sqlalchemy>=2.0.0         # ORM
alembic>=1.11.0           # Database migrations

# Task Queue (Optional for async)
celery>=5.3.0             # Distributed task queue
redis>=4.6.0              # Message broker

# API Framework (Optional for web interface)
fastapi>=0.100.0          # Modern web framework
uvicorn>=0.23.0           # ASGI server
pydantic>=2.0.0           # Data validation

# Utilities
python-dotenv>=1.0.0      # Environment variables
requests>=2.31.0          # HTTP client
httpx>=0.24.0             # Async HTTP client
tenacity>=8.2.0           # Retry logic
loguru>=0.7.0             # Better logging
tqdm>=4.65.0              # Progress bars
pyyaml>=6.0               # YAML parsing
```

## External Tools & Services

### Required System Tools

1. **FFmpeg** (>=5.0)
   - Video/audio encoding and processing
   - Installation:
     - Windows: `choco install ffmpeg` or download from ffmpeg.org
     - Linux: `apt install ffmpeg`
     - Mac: `brew install ffmpeg`

2. **Git LFS** (Large File Storage)
   - For storing large model files
   - Installation: `git lfs install`

### Optional API Services

1. **ElevenLabs** (Recommended for best TTS quality)
   - Website: elevenlabs.io
   - Pricing: ~$5-$99/month
   - British voices: Charlotte, Alice, Jessica

2. **Azure Speech Service** (Alternative TTS)
   - Website: azure.microsoft.com/speech
   - Pricing: Pay-as-you-go, ~$1 per 1M chars
   - Voices: en-GB-SoniaNeural, en-GB-LibbyNeural

3. **D-ID** (Premium avatar generation)
   - Website: d-id.com
   - Pricing: ~$5-$300/month
   - High-quality talking heads

4. **Mubert** (Music generation API)
   - Website: mubert.com
   - Alternative to local MusicGen

## ML Models to Download

### 1. TTS Models

**Coqui XTTS v2** (Recommended for local)
- Size: ~2GB
- Quality: Excellent, voice cloning capable
- Download: Automatic via TTS package

**Piper TTS - British Voice**
- Size: ~50MB
- Quality: Good, very fast
- Models: en_GB-alan-medium, en_GB-jenny_dioco-medium

### 2. Avatar/Talking Head Models

**SadTalker** (Recommended for local)
- Repository: https://github.com/OpenTalker/SadTalker
- Size: ~5GB (checkpoints)
- GPU Required: 6GB+ VRAM
- Quality: Excellent

**Wav2Lip** (Alternative)
- Repository: https://github.com/Rudrabha/Wav2Lip
- Size: ~200MB
- GPU Required: 4GB+ VRAM
- Quality: Good lip-sync

### 3. Music Generation Models

**MusicGen** (Meta AudioCraft)
- Models:
  - `small`: 300M params, ~1.5GB
  - `medium`: 1.5B params, ~6GB
  - `large`: 3.3B params, ~13GB
- Download: Automatic via audiocraft package

### 4. Optional: Stable Diffusion for Backgrounds

**Stable Diffusion XL** (for custom studio generation)
- Size: ~7GB
- Purpose: Generate custom backgrounds
- Model: stabilityai/stable-diffusion-xl-base-1.0

## GPU Requirements

### Minimum Configuration
- **GPU**: NVIDIA GPU with 6GB VRAM (GTX 1060 6GB, RTX 3050)
- **CUDA**: 11.8+
- **CPU Fallback**: Possible but 10-50x slower

### Recommended Configuration
- **GPU**: NVIDIA GPU with 12GB+ VRAM (RTX 3060, RTX 4070)
- **CUDA**: 12.0+
- **RAM**: 16GB system RAM
- **Storage**: 50GB free space (for models and outputs)

### Optimal Configuration
- **GPU**: NVIDIA GPU with 24GB+ VRAM (RTX 3090, RTX 4090, A5000)
- **CUDA**: 12.0+
- **RAM**: 32GB+ system RAM
- **Storage**: 100GB+ NVMe SSD

## System Requirements

### Operating Systems
- **Windows**: 10/11 (with WSL2 for some features)
- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 36+
- **macOS**: 12+ (CPU only, no CUDA support)

### Docker Requirements
- Docker Desktop 4.0+ or Docker Engine 20.10+
- Docker Compose v2.0+
- WSL2 (Windows only)

## Development Tools

```plaintext
# Development Dependencies
pytest>=7.4.0             # Testing framework
pytest-asyncio>=0.21.0    # Async testing
pytest-cov>=4.1.0         # Coverage reporting
black>=23.7.0             # Code formatting
flake8>=6.0.0             # Linting
mypy>=1.4.0               # Type checking
pre-commit>=3.3.0         # Git hooks
```

## Cloud Services (Optional)

For scaling beyond local machine:

1. **AWS**
   - EC2 G4/G5 instances (GPU instances)
   - S3 for storage
   - SQS for job queues

2. **Azure**
   - NC-series VMs (GPU VMs)
   - Blob Storage
   - Azure Speech Service

3. **Google Cloud**
   - Compute Engine with GPUs
   - Cloud Storage
   - Cloud Text-to-Speech

## Installation Priority

### Phase 1: Core Setup
1. Python 3.10+
2. FFmpeg
3. Basic Python packages (typer, rich, pydantic)

### Phase 2: Audio Pipeline
1. TTS engine (Coqui TTS or API)
2. Audio processing (pydub, librosa)
3. Music generation (AudioCraft)

### Phase 3: Video Pipeline
1. Video processing (moviepy, opencv)
2. Avatar generation (SadTalker or Wav2Lip)
3. Composition tools

### Phase 4: Advanced Features
1. Task queue (Celery + Redis)
2. Web interface (FastAPI)
3. Cloud integration

## Estimated Resource Usage

### Per 5-minute Podcast Episode

| Component | CPU Time | GPU Time | Storage | VRAM |
|-----------|----------|----------|---------|------|
| TTS       | 2-5 min  | 30-60s   | 10MB    | 2GB  |
| Music Gen | 5-10 min | 1-3 min  | 20MB    | 4GB  |
| Avatar    | 10-20 min| 3-8 min  | 500MB   | 6GB  |
| Video Mix | 2-5 min  | 1-2 min  | 200MB   | 1GB  |
| **Total** | 20-40 min| 5-15 min | 730MB   | 8GB* |

*Peak VRAM usage, not cumulative

## License Considerations

- **Coqui TTS**: MPL 2.0 (open source)
- **AudioCraft**: MIT License (open source)
- **SadTalker**: MIT License (open source)
- **Wav2Lip**: Custom academic license (check before commercial use)
- **FFmpeg**: LGPL/GPL (depending on build)
- **MoviePy**: MIT License (open source)

## Security Notes

1. API keys should be stored in `.env` files (never commit)
2. Use environment variables for sensitive configuration
3. Generated content should be watermarked/attributed
4. Respect TTS service terms of use
5. Consider content moderation for user inputs

