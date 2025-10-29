# Tools & Libraries Reference - AI Podcast Creator

Complete reference of all tools, libraries, and utilities used in the AI Podcast Creator system.

## Core Python Libraries

### Framework & CLI

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **typer** | 0.9.0 | Modern CLI framework with type hints | MIT | https://typer.tiangolo.com |
| **rich** | 13.7.0 | Beautiful terminal output, tables, progress bars | MIT | https://rich.readthedocs.io |
| **pydantic** | 2.5.0 | Data validation and settings management | MIT | https://docs.pydantic.dev |
| **click** | 8.x | CLI toolkit (dependency of typer) | BSD | https://click.palletsprojects.com |

### AI/ML Core

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **torch** | 2.1.0 | Deep learning framework | BSD | https://pytorch.org |
| **torchaudio** | 2.1.0 | Audio processing with PyTorch | BSD | https://pytorch.org/audio |
| **transformers** | 4.35.0 | HuggingFace model library | Apache 2.0 | https://huggingface.co/transformers |
| **diffusers** | 0.24.0 | Diffusion models (Stable Diffusion, etc.) | Apache 2.0 | https://github.com/huggingface/diffusers |
| **accelerate** | 0.25.0 | Multi-GPU and optimization | Apache 2.0 | https://huggingface.co/docs/accelerate |

### Text-to-Speech Engines

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **TTS (Coqui)** | 0.22.0 | Open-source TTS with voice cloning | MPL 2.0 | https://github.com/coqui-ai/TTS |
| **elevenlabs** | 0.2.27 | ElevenLabs API client (optional) | MIT | https://elevenlabs.io |
| **azure-cognitiveservices-speech** | 1.34.0 | Azure Speech Service (optional) | MIT | https://azure.microsoft.com/speech |
| **piper-tts** | 1.2.0 | Fast lightweight TTS (optional) | MIT | https://github.com/rhasspy/piper |

### Music Generation

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **audiocraft** | 1.3.0 | Meta's audio generation toolkit (MusicGen) | MIT | https://github.com/facebookresearch/audiocraft |

### Audio Processing

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **pydub** | 0.25.1 | Simple audio manipulation | MIT | https://github.com/jiaaro/pydub |
| **librosa** | 0.10.1 | Audio analysis and feature extraction | ISC | https://librosa.org |
| **soundfile** | 0.12.1 | Audio file I/O | BSD | https://pysoundfile.readthedocs.io |
| **scipy** | 1.11.4 | Scientific computing and signal processing | BSD | https://scipy.org |
| **numpy** | 1.24.3 | Numerical computing foundation | BSD | https://numpy.org |

### Video Processing

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **moviepy** | 1.0.3 | Video editing and composition | MIT | https://zulko.github.io/moviepy |
| **opencv-python** | 4.8.1 | Computer vision and image processing | Apache 2.0 | https://opencv.org |
| **pillow** | 10.1.0 | Image manipulation | PIL License | https://pillow.readthedocs.io |
| **imageio** | 2.33.0 | Image and video I/O | BSD | https://imageio.readthedocs.io |
| **imageio-ffmpeg** | 0.4.9 | FFmpeg backend for imageio | BSD | https://github.com/imageio/imageio-ffmpeg |

### Database & Storage

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **sqlalchemy** | 2.0.23 | SQL toolkit and ORM | MIT | https://www.sqlalchemy.org |
| **alembic** | 1.13.0 | Database migration tool | MIT | https://alembic.sqlalchemy.org |

### Task Queue (Optional)

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **celery** | 5.3.4 | Distributed task queue | BSD | https://docs.celeryq.dev |
| **redis** | 5.0.1 | Redis client for Python | MIT | https://redis-py.readthedocs.io |

### API Framework (Optional)

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **fastapi** | 0.104.1 | Modern web framework | MIT | https://fastapi.tiangolo.com |
| **uvicorn** | 0.24.0 | ASGI server | BSD | https://www.uvicorn.org |

### Utilities

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **python-dotenv** | 1.0.0 | Environment variable management | BSD | https://github.com/theskumar/python-dotenv |
| **requests** | 2.31.0 | HTTP library | Apache 2.0 | https://requests.readthedocs.io |
| **httpx** | 0.25.2 | Async HTTP client | BSD | https://www.python-httpx.org |
| **tenacity** | 8.2.3 | Retry logic and error handling | Apache 2.0 | https://tenacity.readthedocs.io |
| **loguru** | 0.7.2 | Better logging | MIT | https://loguru.readthedocs.io |
| **tqdm** | 4.66.1 | Progress bars | MPL/MIT | https://tqdm.github.io |
| **pyyaml** | 6.0.1 | YAML parser | MIT | https://pyyaml.org |

### Development Tools

| Library | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| **pytest** | 7.4.3 | Testing framework | MIT | https://pytest.org |
| **pytest-asyncio** | 0.21.1 | Async testing support | Apache 2.0 | https://pytest-asyncio.readthedocs.io |
| **pytest-cov** | 4.1.0 | Coverage reporting | MIT | https://pytest-cov.readthedocs.io |
| **black** | 23.12.1 | Code formatter | MIT | https://black.readthedocs.io |
| **flake8** | 6.1.0 | Linting | MIT | https://flake8.pycqa.org |
| **mypy** | 1.7.1 | Static type checking | MIT | https://mypy.readthedocs.io |
| **pre-commit** | 3.6.0 | Git hooks framework | MIT | https://pre-commit.com |

## External System Tools

### Required

| Tool | Min Version | Purpose | Installation |
|------|-------------|---------|--------------|
| **FFmpeg** | 5.0+ | Video/audio encoding and processing | apt/brew/choco install ffmpeg |
| **Python** | 3.10+ | Programming language runtime | python.org |
| **Git** | 2.0+ | Version control | git-scm.com |

### Optional

| Tool | Purpose | Installation |
|------|---------|--------------|
| **Git LFS** | Large file storage for models | git-lfs.github.com |
| **Docker** | Containerization | docker.com |
| **Docker Compose** | Multi-container orchestration | docs.docker.com/compose |
| **Redis** | Message broker for Celery | redis.io |
| **CUDA Toolkit** | GPU acceleration | developer.nvidia.com/cuda-downloads |

## AI Models & Checkpoints

### TTS Models

#### Coqui XTTS v2
- **Size**: ~2GB
- **Quality**: Excellent
- **Features**: Multilingual, voice cloning
- **Download**: Automatic via TTS package
- **Location**: `~/.local/share/tts/`
- **URL**: https://github.com/coqui-ai/TTS

#### Piper TTS - British Voices
- **Models**: 
  - en_GB-alan-medium (~50MB)
  - en_GB-jenny_dioco-medium (~50MB)
- **Quality**: Good
- **Speed**: Very fast
- **Download**: Automatic
- **URL**: https://github.com/rhasspy/piper

### Music Generation Models

#### MusicGen (Meta AudioCraft)
- **Models**:
  - `facebook/musicgen-small`: 300M params, ~1.5GB
  - `facebook/musicgen-medium`: 1.5B params, ~6GB
  - `facebook/musicgen-large`: 3.3B params, ~13GB
- **Quality**: Small=Good, Medium=Excellent, Large=Outstanding
- **Download**: Automatic via audiocraft
- **URL**: https://github.com/facebookresearch/audiocraft

### Avatar/Talking Head Models

#### SadTalker
- **Size**: ~5GB (all checkpoints)
- **Quality**: Excellent
- **Features**: Natural head movement, expressions
- **GPU Required**: 6GB+ VRAM
- **Manual Setup**: 
  ```bash
  git clone https://github.com/OpenTalker/SadTalker.git
  bash scripts/download_models.sh
  ```
- **URL**: https://github.com/OpenTalker/SadTalker

#### Wav2Lip
- **Size**: ~200MB
- **Quality**: Good lip-sync
- **GPU Required**: 4GB+ VRAM
- **Models**:
  - wav2lip.pth (~200MB)
  - wav2lip_gan.pth (~200MB)
- **Download**: Manual from releases
- **URL**: https://github.com/Rudrabha/Wav2Lip

### Optional Enhancement Models

#### GFPGAN (Face Enhancement)
- **Size**: ~350MB
- **Purpose**: Enhance avatar face quality
- **Download**: Automatic when using SadTalker with enhancer
- **URL**: https://github.com/TencentARC/GFPGAN

#### Stable Diffusion XL (Background Generation)
- **Size**: ~7GB
- **Purpose**: Generate custom studio backgrounds
- **Model**: stabilityai/stable-diffusion-xl-base-1.0
- **Download**: Automatic via diffusers
- **URL**: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0

## Cloud API Services (Optional)

### Text-to-Speech

| Service | Quality | Pricing | British Voices | URL |
|---------|---------|---------|----------------|-----|
| **ElevenLabs** | Excellent | $5-99/mo | Charlotte, Alice, Jessica | elevenlabs.io |
| **Azure Speech** | Very Good | Pay-as-you-go (~$1/1M chars) | Sonia, Libby, Ryan | azure.microsoft.com/speech |
| **Google Cloud TTS** | Good | Pay-as-you-go | en-GB-Neural2-* | cloud.google.com/text-to-speech |
| **AWS Polly** | Good | Pay-as-you-go | Amy, Emma, Brian | aws.amazon.com/polly |

### Avatar Generation

| Service | Quality | Pricing | Features | URL |
|---------|---------|---------|----------|-----|
| **D-ID** | Excellent | $5-300/mo | Realistic talking heads | d-id.com |
| **Synthesia** | Excellent | $30+/mo | Professional avatars | synthesia.io |
| **HeyGen** | Very Good | $29+/mo | Custom avatars | heygen.com |

### Music Generation

| Service | Quality | Pricing | Features | URL |
|---------|---------|---------|----------|-----|
| **Mubert** | Good | $15-100/mo | Royalty-free AI music | mubert.com |
| **Soundraw** | Good | $20+/mo | Customizable music | soundraw.io |
| **AIVA** | Excellent | $15+/mo | Orchestral, cinematic | aiva.ai |

## Infrastructure Tools

### Development

| Tool | Purpose | URL |
|------|---------|-----|
| **Visual Studio Code** | Code editor | code.visualstudio.com |
| **PyCharm** | Python IDE | jetbrains.com/pycharm |
| **Jupyter** | Interactive notebooks | jupyter.org |

### Deployment

| Tool | Purpose | URL |
|------|---------|-----|
| **Docker** | Containerization | docker.com |
| **Kubernetes** | Container orchestration | kubernetes.io |
| **AWS EC2** | Cloud compute | aws.amazon.com/ec2 |
| **Azure VMs** | Cloud compute | azure.microsoft.com |
| **Google Cloud Compute** | Cloud compute | cloud.google.com/compute |

### Monitoring

| Tool | Purpose | URL |
|------|---------|-----|
| **Prometheus** | Metrics collection | prometheus.io |
| **Grafana** | Metrics visualization | grafana.com |
| **Sentry** | Error tracking | sentry.io |

## Media Assets

### Recommended Resources

#### Stock Images (for backgrounds)
- **Unsplash**: Free high-quality photos - unsplash.com
- **Pexels**: Free stock photos - pexels.com
- **Pixabay**: Free images and videos - pixabay.com

#### Stock Music (fallback library)
- **Free Music Archive**: CC-licensed music - freemusicarchive.org
- **YouTube Audio Library**: Royalty-free music - youtube.com/audiolibrary
- **Incompetech**: Kevin MacLeod's library - incompetech.com

#### Fonts (for subtitles/watermarks)
- **Google Fonts**: Free fonts - fonts.google.com
- **Font Awesome**: Icons - fontawesome.com

## Utility Commands

### FFmpeg Common Operations

```bash
# Convert audio format
ffmpeg -i input.wav -acodec libmp3lame output.mp3

# Combine audio and video
ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac output.mp4

# Resize video
ffmpeg -i input.mp4 -vf scale=1920:1080 output.mp4

# Extract audio from video
ffmpeg -i input.mp4 -vn -acodec copy output.wav

# Create video from image + audio
ffmpeg -loop 1 -i image.jpg -i audio.mp3 -c:v libx264 -tune stillimage -c:a aac -shortest output.mp4
```

### GPU/CUDA Commands

```bash
# Check NVIDIA driver
nvidia-smi

# Monitor GPU usage in real-time
watch -n 1 nvidia-smi

# Check CUDA version
nvcc --version

# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install from requirements
pip install -r requirements.txt

# Generate requirements
pip freeze > requirements.txt

# Update all packages
pip list --outdated
pip install -U package_name
```

## Additional Tools & Utilities to Consider

### For Enhanced Features

| Tool/Library | Purpose | Why Add It |
|--------------|---------|------------|
| **whisper** | Audio transcription | Auto-generate subtitles |
| **bark** | Voice generation | Alternative TTS with more emotion |
| **rvc-python** | Voice conversion | Change voice characteristics |
| **demucs** | Audio source separation | Remove noise from audio |
| **gradio** | Web UI framework | Create interactive web interface |
| **streamlit** | Dashboard framework | Build admin dashboard |
| **telegram-bot** | Bot framework | Bot interface for generation |
| **discord.py** | Discord bot | Discord integration |

### For Production Deployment

| Tool | Purpose |
|------|---------|
| **nginx** | Reverse proxy, load balancing |
| **gunicorn** | WSGI HTTP server |
| **supervisor** | Process management |
| **certbot** | SSL certificates |
| **cloudflare** | CDN and DDoS protection |

### For Analytics

| Tool | Purpose |
|------|---------|
| **Google Analytics** | Usage tracking |
| **Mixpanel** | Product analytics |
| **PostHog** | Open-source analytics |

## License Summary

| License Type | Libraries | Commercial Use | Redistribution |
|--------------|-----------|----------------|----------------|
| **MIT** | Most libraries | ✓ Yes | ✓ Yes |
| **Apache 2.0** | Transformers, Diffusers | ✓ Yes | ✓ Yes |
| **BSD** | PyTorch, NumPy, SciPy | ✓ Yes | ✓ Yes |
| **MPL 2.0** | Coqui TTS | ✓ Yes | ✓ Yes (with conditions) |
| **Academic** | Wav2Lip | ⚠ Check terms | ⚠ Check terms |

**Important**: Always verify license terms for commercial use, especially:
- Wav2Lip has academic license (check for commercial use)
- API services have their own terms of service
- Generated content may require attribution/labeling

## Version Compatibility Matrix

| Component | Python 3.10 | Python 3.11 | Python 3.12 | CUDA 11.8 | CUDA 12.1 |
|-----------|-------------|-------------|-------------|-----------|-----------|
| PyTorch 2.1 | ✓ | ✓ | ✗ | ✓ | ✓ |
| TTS 0.22 | ✓ | ✓ | ✗ | ✓ | ✓ |
| AudioCraft | ✓ | ✓ | ⚠ | ✓ | ✓ |
| MoviePy | ✓ | ✓ | ✓ | N/A | N/A |

✓ = Fully supported  
⚠ = Experimental  
✗ = Not supported  
N/A = Not applicable

---

**Last Updated**: October 2024  
**Maintainer**: AI Podcast Creator Team

For the latest updates, check individual project repositories and documentation.

