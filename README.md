# 🎙️ AI Podcast Creator

Transform text scripts into professional video podcasts with AI-powered narration, music, and animation.

## Overview

AI Podcast Creator is an automated video podcast generation system featuring:

- **🗣️ Natural Speech**: British female narrator "Vivienne Sterling" with professional RP accent
- **🎵 AI Music**: Automatically generated background music from text descriptions
- **🎬 Animated Presenter**: Talking head animation synced to audio
- **🏢 Professional Setting**: Recording studio background with customizable scenes
- **⚡ CLI Interface**: Easy-to-use command-line tools
- **🔧 Modular Design**: Swap TTS engines, avatar systems, and music generators
- **🚀 GPU Acceleration**: 10-12x faster generation with NVIDIA GPU support

## 🎨 GUI Interface Available!

**No command line needed!** We now have beautiful graphical interfaces:

### 🌐 Web Interface (Recommended) ⭐ **EASY LAUNCH!**

**Quick Start - Just double-click:**
```
start_web_ui.bat          # Minimized window (easy troubleshooting)
start_web_ui_hidden.vbs   # Completely hidden (no window)
```

**Or manually:**
```bash
python launch_web_gui.py --port 7861
```

**✅ Access at:** **http://localhost:7861**

**Features:**
- ✅ **Responsive Design** - No scrolling, works on any screen size
- ✅ **TTS Voice Selection** - Choose from 4 engines (gTTS/Coqui/ElevenLabs/Azure)
- ✅ **Voice Speed Control** - Adjust narration speed (0.5x - 2.0x)
- ✅ **Avatar Style Options** - Multiple visual themes
- ✅ Drag & drop file upload
- ✅ Video quality settings (480p/720p/1080p)
- ✅ Real-time processing feedback
- ✅ Example scripts included

**Stop Server:**
```
stop_web_ui.bat           # Stop the web server
```

### 💻 Desktop GUI:
```bash
python launch_desktop_gui.py
# Native desktop application
```

**See [WEB_INTERFACE_READY.md](WEB_INTERFACE_READY.md), [LAUNCH_GUI.md](LAUNCH_GUI.md) and [GUI_GUIDE.md](GUI_GUIDE.md) for details!**

---

## 🚀 GPU Acceleration (10x Faster!)

AI Podcast Creator supports **NVIDIA GPU acceleration** for dramatically faster generation:

### Performance Comparison (2-minute podcast):
- **CPU**: 60-80 minutes
- **GPU (RTX 4060)**: 5-8 minutes
- **Speedup**: **10-12x faster!** 🚀

### GPU-Accelerated Features:
- ✅ **TTS (Coqui XTTS)** - Natural voices, 5x faster
- ✅ **Music (MusicGen)** - AI-generated music, 10x faster
- ✅ **Avatar (SadTalker)** - Animated talking heads, 12x faster

### Requirements:
- NVIDIA GPU with 6GB+ VRAM (RTX 3060/4060 or better)
- CUDA-enabled PyTorch (included in requirements.txt)

### Quick GPU Setup (5 minutes):

```bash
# 1. Check GPU
python check_gpu.py

# 2. Install GPU packages
pip install TTS audiocraft

# 3. Update config.yaml (change engines to GPU versions)
# See QUICK_GPU_SETUP.md for details

# 4. Generate at GPU speed!
python -m src.cli.main create Creations/example_welcome.txt
```

**📚 Documentation:**
- **Quick Start**: [QUICK_GPU_SETUP.md](QUICK_GPU_SETUP.md) - 5-minute setup
- **Complete Guide**: [GPU_SETUP_COMPLETE.md](GPU_SETUP_COMPLETE.md) - Detailed setup & optimization

### 📊 GPU Monitoring

Monitor real-time GPU usage with accurate metrics:

```powershell
# Windows - Real-time monitoring
.\monitor_gpu.ps1

# Or use nvidia-smi directly
nvidia-smi
```

**Note:** Windows Task Manager and Xbox Game Bar may show **VRAM allocation** as "GPU usage" which can be misleading. Use `nvidia-smi` or `monitor_gpu.ps1` for accurate **compute utilization**.

---

## Quick Start (Command Line)

### Prerequisites

- Python 3.10 or higher
- FFmpeg 5.0+ installed and in PATH
- NVIDIA GPU with 6GB+ VRAM (recommended for GPU features, optional)
- 50GB free disk space for models

**Note:** GPU is optional but provides 10x faster generation. CPU works but is much slower.

### Installation

1. **Clone or download this repository**

```bash
cd AI_Podcast_Creator
```

2. **Create virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment** (optional for API services)

```bash
# Copy example env file
copy env.example .env  # Windows
cp env.example .env    # Linux/Mac

# Edit .env and add your API keys if using commercial services
```

5. **Initialize the system**

```bash
python -m src.cli.main init
```

This will:
- Create necessary directories
- Initialize the database
- Check system dependencies
- Download required models (on first use)

### Create Your First Podcast

```bash
python -m src.cli.main create data/scripts/example_welcome.txt
```

The generated video will be saved to `data/outputs/`.

## Usage

### Commands

#### Create a Podcast

```bash
# Basic usage
python -m src.cli.main create script.txt

# With custom output name
python -m src.cli.main create script.txt -o my_podcast

# Preview audio only (faster, no video)
python -m src.cli.main create script.txt --preview

# Skip music generation
python -m src.cli.main create script.txt --skip-music
```

#### List Podcasts

```bash
python -m src.cli.main list
```

#### Check System Status

```bash
python -m src.cli.main status
```

#### View Configuration

```bash
python -m src.cli.main config --show
```

### Script Format

Create text files with your podcast script. Use `[MUSIC: description]` tags to add background music.

**Example:**

```markdown
# Episode Title

[MUSIC: upbeat intro, electronic, energetic]

Hello and welcome to today's episode...

[MUSIC: soft ambient background, calming]

Let me tell you about an interesting topic...

[MUSIC: crescendo, dramatic build-up]

And that's when everything changed...

[MUSIC: fade out]
```

## Configuration

Edit `config.yaml` to customize:

- **Character settings**: Name, voice type, personality
- **TTS engine**: Choose between Coqui, ElevenLabs, Azure, or Piper
- **Music generation**: Configure MusicGen or other services
- **Avatar system**: Select SadTalker, Wav2Lip, or D-ID
- **Video settings**: Resolution, FPS, codec, background
- **Storage paths**: Output directories and cache locations

## Architecture

```
┌─────────────┐
│ CLI Input   │ (Script file)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │ (Extract text & music cues)
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌──────┐ ┌──────┐
│ TTS  │ │Music │
└───┬──┘ └──┬───┘
    │       │
    └───┬───┘
        ▼
    ┌───────┐
    │ Mixer │ (Combine with ducking)
    └───┬───┘
        │
        ▼
    ┌───────┐
    │Avatar │ (Animated talking head)
    └───┬───┘
        │
        ▼
    ┌─────────┐
    │Composer │ (Final video with background)
    └─────┬───┘
          │
          ▼
    ┌──────────┐
    │ Output   │ (MP4 video)
    └──────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## TTS Engine Options

### 1. Coqui TTS (Default - Open Source)

**Pros:**
- Free and open source
- Good quality
- Voice cloning capable
- Runs locally

**Cons:**
- Requires GPU for reasonable speed
- ~2GB model download

**Setup:** Automatic (included in requirements)

### 2. ElevenLabs (Premium Quality)

**Pros:**
- Exceptional quality
- Many British voices
- Fast generation
- Cloud-based

**Cons:**
- Requires API key
- Costs ~$5-99/month
- Internet required

**Setup:**
```bash
# Add to .env
ELEVENLABS_API_KEY=your_key_here

# Change in config.yaml
tts:
  engine: "elevenlabs"
```

### 3. Azure Speech (Good Balance)

**Pros:**
- High quality
- Pay-as-you-go
- Reliable
- Many languages

**Cons:**
- Requires Azure account
- Internet required

**Setup:**
```bash
# Add to .env
AZURE_SPEECH_KEY=your_key
AZURE_REGION=eastus

# Change in config.yaml
tts:
  engine: "azure"
```

### 4. Piper TTS (Fastest)

**Pros:**
- Very fast
- Small models (~50MB)
- Offline
- Low resource usage

**Cons:**
- Lower quality than others

**Setup:** Automatic (included in requirements)

## Avatar Options

### 1. SadTalker (Recommended - Open Source)

**Pros:**
- Excellent quality
- Good head movement
- Runs locally
- Free

**Cons:**
- Requires 6GB+ VRAM
- Slow on CPU
- ~5GB model download

**Setup:**
```bash
# Clone SadTalker repository
git clone https://github.com/OpenTalker/SadTalker.git data/models/sadtalker
cd data/models/sadtalker
pip install -r requirements.txt
bash scripts/download_models.sh
```

### 2. Wav2Lip (Alternative - Open Source)

**Pros:**
- Good lip sync
- Lighter weight
- Fast

**Cons:**
- Less natural movement
- Static head pose

**Setup:**
```bash
# Clone Wav2Lip repository
git clone https://github.com/Rudrabha/Wav2Lip.git data/models/wav2lip
# Download pretrained models from releases
```

### 3. D-ID (Commercial - Highest Quality)

**Pros:**
- Professional quality
- Very realistic
- Cloud-based
- Fast

**Cons:**
- Costs ~$5-300/month
- Requires API key

**Setup:**
```bash
# Add to .env
DID_API_KEY=your_key_here

# Change in config.yaml
avatar:
  engine: "did"
```

## GPU Acceleration ⚡

**The system is fully GPU-optimized with automatic detection and performance tuning!**

### Automatic GPU Features:
- ✅ **Automatic GPU Detection** - No manual configuration needed
- ✅ **FP16 Mixed Precision** - 2x faster on RTX/V100+ GPUs
- ✅ **TF32 Acceleration** - 8x faster on RTX 30/40 series
- ✅ **cuDNN Optimization** - Fastest algorithms auto-selected
- ✅ **NVENC Video Encoding** - GPU-accelerated H.264
- ✅ **torch.compile** - PyTorch 2.0+ JIT compilation
- ✅ **Memory Management** - Automatic cache clearing

### GPU Requirements

#### Minimum (6GB VRAM):
- NVIDIA: GTX 1060 6GB, RTX 3050, RTX 2060
- CUDA: 11.8+
- Speed: **10x faster** than CPU
- Generation: ~5-8 min per 2-min episode

#### Recommended (12GB VRAM):
- NVIDIA: RTX 3060 12GB, RTX 4070, RTX 3080
- CUDA: 12.0+
- Speed: **20x faster** than CPU
- Generation: ~2-3 min per 2-min episode

#### Optimal (24GB+ VRAM):
- NVIDIA: RTX 4090, RTX 3090, A5000/A6000
- CUDA: 12.0+
- Speed: **30-50x faster** than CPU
- Generation: ~1-2 min per 2-min episode

#### CPU Fallback:
- Works but 10-50x slower
- Basic version (gTTS): 25-30 seconds
- Full version: 45-90 minutes (not practical)

**See [GPU_OPTIMIZATION_GUIDE.md](GPU_OPTIMIZATION_GUIDE.md) for detailed optimization!**

## Project Structure

```
AI_Podcast_Creator/
├── src/
│   ├── cli/                  # Command-line interface
│   │   └── main.py          # CLI entry point
│   ├── core/                # Core processing modules
│   │   ├── script_parser.py
│   │   ├── tts_engine.py
│   │   ├── music_generator.py
│   │   ├── audio_mixer.py
│   │   ├── avatar_generator.py
│   │   └── video_composer.py
│   ├── models/              # Database models
│   │   └── database.py
│   └── utils/               # Utilities
│       └── config.py
├── data/
│   ├── scripts/             # Input scripts
│   ├── outputs/             # Generated videos
│   ├── cache/               # Temporary files
│   └── models/              # Downloaded AI models
├── tests/                   # Unit tests
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
├── ARCHITECTURE.md          # System architecture
├── REQUIREMENTS.md          # Detailed requirements
└── README.md               # This file
```

## Troubleshooting

### FFmpeg not found
```bash
# Windows (with Chocolatey)
choco install ffmpeg

# Linux
sudo apt install ffmpeg

# Mac
brew install ffmpeg
```

### GPU/CUDA issues
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, install CUDA-enabled PyTorch:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Out of memory errors
- Reduce video resolution in config.yaml
- Use smaller models (MusicGen small, etc.)
- Close other GPU-intensive applications
- Use CPU fallback (set use_gpu: false in config)

### Slow generation
- **Check GPU usage**: Run `python check_gpu.py` to verify GPU detection
- Ensure GPU is being used (check with `nvidia-smi`)
- Enable GPU acceleration (see QUICK_GPU_SETUP.md)
- Use smaller, faster models
- Consider cloud-based APIs (ElevenLabs, D-ID)
- Enable caching (default)

### GPU not detected
- Run `python check_gpu.py` for detailed diagnostics
- Check NVIDIA drivers are installed: `nvidia-smi`
- Reinstall PyTorch with CUDA:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
- See [GPU_SETUP_COMPLETE.md](GPU_SETUP_COMPLETE.md) troubleshooting section

### Known bugs
- Run `python fix_bugs.py` to apply automated fixes
- See [BUGS_FOUND_AND_FIXED.md](BUGS_FOUND_AND_FIXED.md) for details

## Advanced Features

### Custom Avatar Image

Replace `src/assets/avatars/vivienne_sterling.png` with your own portrait:
- 1024x1024 resolution recommended
- Frontal face pose
- Good lighting
- Neutral expression

### Custom Background

Replace `src/assets/backgrounds/studio_01.jpg` with your scene:
- 1920x1080 resolution
- Consider presenter placement
- Appropriate lighting and theme

### Multiple Characters

Edit config.yaml to create different character profiles, or maintain multiple config files:

```bash
python -m src.cli.main create script.txt -c config_character2.yaml
```

### Async Processing (Advanced)

For batch processing multiple podcasts:

1. Install Redis:
```bash
docker run -d -p 6379:6379 redis
```

2. Start Celery worker:
```bash
celery -A src.worker worker --loglevel=info
```

3. Enable async in config.yaml:
```yaml
processing:
  async_mode: true
```

## API/Web Interface (Optional)

For a web-based interface:

```bash
# Enable in config.yaml
api:
  enabled: true

# Start server
uvicorn src.api.main:app --reload
```

Access at http://localhost:8000

## 📚 Documentation

### Getting Started
- [README.md](README.md) - Main documentation (this file)
- [QUICK_START.md](QUICK_START.md) - Basic setup guide
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation
- [LAUNCH_GUI.md](LAUNCH_GUI.md) - GUI launch instructions

### GPU & Performance
- ⚡ [QUICK_GPU_SETUP.md](QUICK_GPU_SETUP.md) - **5-minute GPU setup** _(Start here for GPU!)_
- [GPU_SETUP_COMPLETE.md](GPU_SETUP_COMPLETE.md) - Complete GPU guide with troubleshooting
- [GPU_OPTIMIZATION_GUIDE.md](GPU_OPTIMIZATION_GUIDE.md) - Performance tuning
- [check_gpu.py](check_gpu.py) - GPU detection utility

### Features & Configuration
- [VOICE_OPTIONS_GUIDE.md](VOICE_OPTIONS_GUIDE.md) - TTS voice configuration
- [VOICE_QUICK_REF.md](VOICE_QUICK_REF.md) - Voice reference
- [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md) - Audio visualization
- [AVATAR_GUIDE.md](AVATAR_GUIDE.md) - Avatar setup
- [FEATURES.md](FEATURES.md) - All features overview

### Troubleshooting
- 🐛 [BUGS_FOUND_AND_FIXED.md](BUGS_FOUND_AND_FIXED.md) - Known issues and fixes
- [fix_bugs.py](fix_bugs.py) - Automated bug fix script
- [GPU_SETUP_COMPLETE.md](GPU_SETUP_COMPLETE.md) - GPU troubleshooting section

### Advanced
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [REQUIREMENTS.md](REQUIREMENTS.md) - Technical requirements
- [GUI_GUIDE.md](GUI_GUIDE.md) - GUI usage guide

## 🚀 CI/CD & Quality Automation

**Professional-grade automated testing pipeline!**

### Quick Start for Developers

```powershell
# One-time setup (5 minutes)
.\scripts\setup_dev_tools.ps1

# Daily workflow
git add .
git commit -m "message"    # Auto-formatting, linting, tests
.\scripts\pre-push.ps1     # Verify before pushing
git push                   # GitHub Actions runs automatically
```

### What's Automated ✅
- ✅ **Code formatting** (Black) on every commit
- ✅ **Linting** (Flake8) on every commit  
- ✅ **Security scanning** (Bandit) on every push
- ✅ **Full test suite** (286 tests) on every push
- ✅ **Multi-platform testing** (Ubuntu + Windows)
- ✅ **Multi-version testing** (Python 3.10, 3.11, 3.12)
- ✅ **Coverage tracking** (30% minimum enforced)
- ✅ **Weekly deep scans** (mutation testing, type checking, security audits)

### Documentation
- **Quick Start:** [QUICK_START_CI_CD.md](QUICK_START_CI_CD.md) (5 minutes)
- **Full Guide:** [CI_CD_SETUP_GUIDE.md](CI_CD_SETUP_GUIDE.md) (comprehensive)
- **Future Plans:** [QA_EXCELLENCE_ROADMAP.md](QA_EXCELLENCE_ROADMAP.md)

### Helper Scripts
```powershell
.\scripts\test.ps1          # Run all tests with coverage
.\scripts\test-fast.ps1     # Run fast tests only
.\scripts\coverage.ps1      # Generate coverage report (opens in browser)
.\scripts\lint.ps1          # Run linting checks
.\scripts\security.ps1      # Run security scans
.\scripts\pre-push.ps1      # Validate before pushing
```

---

## Testing

### Test Coverage

**Current Status:** 31% overall coverage (48% on core modules, 100% pass rate)

| Module | Coverage | Status |
|--------|----------|--------|
| audio_mixer.py | 100% | ✅ Perfect |
| script_parser.py | 100% | ✅ Perfect |
| config.py | 100% | ✅ Perfect |
| gpu_utils.py | 99% | 🏆 Excellent |
| video_composer.py | 72% | ✅ Very Good |
| avatar_generator.py | 63% | ✅ Good |
| tts_engine.py | 52% | 📈 Fair |
| music_generator.py | 31% | 📊 Moderate |

**Test Suite:** 286 passing tests, 18 skipped (optional dependencies), 0 failures

### Running Tests

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html tests/

# View HTML coverage report
start htmlcov\index.html
```

### Test Documentation

See detailed testing reports:
- `TEST_COVERAGE_COMPLETE_REPORT.md` - Comprehensive coverage analysis
- `COVERAGE_FINAL_STATUS.md` - Current status and metrics
- `COVERAGE_PROGRESS_REPORT.md` - Progress tracking

### Key Testing Features

- ✅ 192 comprehensive tests
- ✅ Pytest framework with fixtures
- ✅ Mocking for external dependencies
- ✅ Skip markers for optional features
- ✅ Real functional tests (not over-mocked)
- ✅ CI/CD ready

## Contributing

This is an open-source project. Contributions welcome:

- Report bugs and request features via issues
- Submit pull requests for improvements
- Share your generated content (with AI disclosure)
- Improve documentation
- Write additional tests (see testing section above)

## License

See individual component licenses:
- Coqui TTS: MPL 2.0
- AudioCraft: MIT
- SadTalker: MIT
- Wav2Lip: Custom academic license

## Ethical Use

**Important Guidelines:**

1. **Disclose AI Generation**: Always label content as AI-generated
2. **Respect Rights**: Don't impersonate real people without permission
3. **Follow Terms**: Comply with API service terms of use
4. **Content Moderation**: Use responsibly, avoid harmful content
5. **Attribution**: Credit the tools and models used

## Support

- **Documentation**: See ARCHITECTURE.md and REQUIREMENTS.md
- **Issues**: Report bugs via GitHub issues
- **Community**: Share experiences and get help

## Roadmap

- [ ] Multi-language support
- [ ] Multiple character/voice options
- [ ] Real-time preview interface
- [ ] YouTube/Spotify direct upload
- [ ] Voice cloning from samples
- [ ] Scene transitions
- [ ] Guest co-host support
- [ ] Subtitle generation
- [ ] Mobile app

## Acknowledgments

Built with amazing open-source tools:
- **Coqui TTS**: Text-to-speech
- **AudioCraft/MusicGen**: Music generation
- **SadTalker**: Avatar animation
- **FFmpeg**: Media processing
- **PyTorch**: ML framework

---

**AI Podcast Creator** - Bringing your stories to life with AI 🎙️✨

