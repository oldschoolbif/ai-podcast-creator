# Historical Architecture Decisions - Complete Log

**Created:** 2025-11-03  
**Purpose:** Comprehensive log of ALL architectural and implementation decisions made throughout the project  
**Scope:** Decisions inferred, implied, and explicitly made from project inception to current date

---

## Table of Contents

1. [Core Architecture Decisions](#core-architecture-decisions)
2. [Technology Stack Choices](#technology-stack-choices)
3. [TTS Engine Decisions](#tts-engine-decisions)
4. [Video/Audio Processing Decisions](#videoaudio-processing-decisions)
5. [GUI/Interface Decisions](#guiinterface-decisions)
6. [Quality & Compatibility Decisions](#quality--compatibility-decisions)
7. [Performance Optimization Decisions](#performance-optimization-decisions)
8. [Testing & QA Decisions](#testing--qa-decisions)
9. [Storage & Organization Decisions](#storage--organization-decisions)
10. [Advanced Script Format Decisions](#advanced-script-format-decisions)

---

## Core Architecture Decisions

### ADL-H001: Python as Primary Language
**Date:** Project Inception  
**Status:** Decided  
**Decision:** Python 3.10+ chosen as primary development language

**Rationale:**
- ✅ Rich AI/ML ecosystem (PyTorch, transformers, etc.)
- ✅ Excellent audio/video libraries (pydub, moviepy, librosa)
- ✅ Easy integration with command-line tools (FFmpeg)
- ✅ Cross-platform support
- ✅ Rapid development

**Alternatives Considered:**
- Node.js/TypeScript (limited ML libraries)
- C++ (complexity, slower development)
- Go/Rust (limited AI/ML ecosystem)

**Impact:** Foundation for entire project

---

### ADL-H002: CLI-First Architecture
**Date:** Project Inception  
**Status:** Decided  
**Decision:** Command-line interface as primary interaction method, GUI optional

**Rationale:**
- ✅ Scriptability and automation
- ✅ Easy integration into workflows
- ✅ No UI framework dependencies
- ✅ Faster development
- ✅ Server-friendly (headless operation)

**Implementation:**
- Typer framework chosen for CLI
- Rich library for beautiful terminal output
- Optional Gradio web interface added later
- Optional Tkinter desktop GUI added later

**Consequences:**
- Can run on servers without displays
- Easy to integrate into CI/CD
- GUI added later without breaking CLI

---

### ADL-H003: Modular Component Architecture
**Date:** Project Inception  
**Status:** Decided  
**Decision:** Separate modules for each major function (TTS, Music, Audio Mixing, Avatar, Video Composition)

**Rationale:**
- ✅ Swap components independently (e.g., different TTS engines)
- ✅ Test components separately
- ✅ Clear separation of concerns
- ✅ Easy to extend

**Structure:**
```
src/core/
  ├── script_parser.py      # Script parsing
  ├── tts_engine.py         # TTS generation
  ├── music_generator.py    # Music generation
  ├── audio_mixer.py        # Audio mixing
  ├── avatar_generator.py  # Avatar animation
  └── video_composer.py     # Video composition
```

**Impact:** Enables flexible engine swapping, easy testing

---

### ADL-H004: Configuration-Driven Design
**Date:** Project Inception  
**Status:** Decided  
**Decision:** YAML configuration file for all settings

**Rationale:**
- ✅ No code changes needed for most customizations
- ✅ Easy to maintain multiple configurations
- ✅ Human-readable
- ✅ Version control friendly

**Implementation:**
- `config.yaml` as primary config
- Environment variable support (`.env` file)
- Config file override via CLI (`--config`)

**Impact:** Users can customize without touching code

---

### ADL-H005: SQLite for Metadata Storage
**Date:** Project Inception  
**Status:** Decided  
**Decision:** SQLite database for podcast metadata

**Rationale:**
- ✅ No server required (file-based)
- ✅ Zero configuration
- ✅ Sufficient for single-user or small-scale use
- ✅ Python has excellent SQLite support

**Alternatives Considered:**
- PostgreSQL (overkill for this use case)
- NoSQL (unnecessary complexity)
- File-based JSON (limited querying)

**Impact:** Simple database setup, no external dependencies

---

## Technology Stack Choices

### ADL-H006: PyTorch for ML Framework
**Date:** Project Inception  
**Status:** Decided  
**Decision:** PyTorch chosen over TensorFlow/JAX

**Rationale:**
- ✅ Best GPU support (CUDA)
- ✅ Most AI models use PyTorch
- ✅ Easy to use Python API
- ✅ Strong community for AI models

**Version Decision:** PyTorch 2.1+ for `torch.compile` support

**Impact:** All ML components (TTS, Music, Avatar) use PyTorch

---

### ADL-H007: FFmpeg as Primary Video Processor
**Date:** Early Development  
**Status:** Decided  
**Decision:** FFmpeg primary, MoviePy as fallback

**Rationale (from MOVIEPY_VS_FFMPEG.md):**
- ✅ GPU acceleration (NVENC) - 10-20x faster
- ✅ Industry standard
- ✅ Lower memory usage (streaming)
- ✅ Professional features

**Fallback Strategy:**
- Try FFmpeg first (GPU-accelerated)
- Fall back to MoviePy if FFmpeg unavailable
- MoviePy good for basic/testing scenarios

**Impact:** 10-20x faster video encoding with GPU

---

### ADL-H008: pydub for Audio Manipulation
**Date:** Early Development  
**Status:** Decided  
**Decision:** pydub for audio mixing, format conversion, basic manipulation

**Rationale:**
- ✅ Simple Python API
- ✅ Easy audio format conversion
- ✅ Good for mixing and ducking
- ✅ Cross-platform

**Limitations Accepted:**
- CPU-only (but simple API worth it)
- Less advanced than dedicated audio tools
- Audio effects require additional libraries (led to pedalboard decision)

**Impact:** Clean, simple audio mixing code

---

### ADL-H009: Gradio for Web Interface
**Date:** GUI Implementation Phase  
**Status:** Decided  
**Decision:** Gradio chosen for web interface (optional)

**Rationale:**
- ✅ Python-native (no JavaScript)
- ✅ Quick to implement
- ✅ Automatic UI generation
- ✅ Built-in file upload/download
- ✅ Can run locally or deploy

**Alternatives Considered:**
- Streamlit (similar, chose Gradio for flexibility)
- FastAPI + HTML/JS (more work)
- Flask + templates (more complex)

**Impact:** Web UI added without major refactoring

---

### ADL-H010: Tkinter for Desktop GUI
**Date:** GUI Implementation Phase  
**Status:** Decided  
**Decision:** Tkinter for desktop GUI (optional)

**Rationale:**
- ✅ Built into Python (no extra dependencies)
- ✅ Cross-platform (Windows/Linux/Mac)
- ✅ Native look and feel
- ✅ Simple for basic GUI needs

**Limitations Accepted:**
- Less modern than Qt/PyQt
- Simpler UI capabilities
- Sufficient for this use case

**Impact:** Desktop GUI option without external dependencies

---

### ADL-H011: Typer for CLI Framework
**Date:** Project Inception  
**Status:** Decided  
**Decision:** Typer over Click/argparse

**Rationale:**
- ✅ Type hints for automatic validation
- ✅ Modern Python (3.10+)
- ✅ Automatic help generation
- ✅ Rich integration for beautiful output

**Impact:** Type-safe CLI with excellent user experience

---

## TTS Engine Decisions

### ADL-H012: Multi-Engine TTS Support
**Date:** Project Inception  
**Status:** Decided  
**Decision:** Support multiple TTS engines, not locked to one

**Engines Supported:**
1. gTTS (Google TTS) - Free, British voices, cloud-based
2. Coqui TTS - Open source, voice cloning, local
3. ElevenLabs - Premium quality, cloud API
4. Azure Speech - Professional, cloud API
5. Piper TTS - Fast, lightweight, offline

**Rationale:**
- ✅ Flexibility for different use cases
- ✅ Free options for testing
- ✅ Premium options for production
- ✅ Local options for privacy

**Implementation:**
- Engine abstraction layer in `TTSEngine` class
- Configurable per script/config file
- Easy to add new engines

**Impact:** Users choose based on quality/cost/privacy needs

---

### ADL-H013: gTTS as Default/Preferred Engine
**Date:** Current State  
**Status:** Decided  
**Decision:** gTTS currently preferred (from conversation)

**Rationale:**
- ✅ Free and unlimited
- ✅ Good quality for podcasts
- ✅ No API keys needed
- ✅ Fast generation (cloud-based)
- ✅ British female voices available

**Current Status:**
- Primary: gTTS (free, British female)
- Secondary: Coqui (for SSML pause support)
- Future: Premium engines when migrating

**Impact:** Zero-cost operation currently

---

### ADL-H014: TTS Caching Strategy
**Date:** Early Development  
**Status:** Decided  
**Decision:** Cache TTS output by script hash

**Rationale:**
- ✅ Avoid regenerating same text
- ✅ Faster iteration during development
- ✅ Save API costs (for paid services)
- ✅ Consistent output for same input

**Implementation:**
- Hash-based cache keys (script text hash)
- Cache directory: `data/cache/tts/`
- Automatic cache management (retention policy)

**Impact:** Significant time/cost savings for repeated scripts

---

## Video/Audio Processing Decisions

### ADL-H015: H.264 Baseline Profile for Universal Compatibility
**Date:** October 2025 (Video Compatibility Fix)  
**Status:** Decided  
**Decision:** H.264 baseline profile + level 3.1 for maximum compatibility

**Context:**
- Original videos used "high" profile (default)
- Windows Media Player codec errors
- Playback issues at variable speeds

**Decision:**
- **Profile:** `baseline` (maximum compatibility)
- **Level:** `3.1` (universal playback, upgraded from 3.0)
- **Pixel Format:** `yuv420p` (standard)
- **Container:** Explicit `mp4` format
- **FastStart:** `+faststart` flag for web optimization

**Rationale:**
- ✅ Plays on ALL devices without codecs
- ✅ Works in web browsers
- ✅ Mobile device compatibility
- ✅ Variable speed playback support

**Trade-offs:**
- Slightly larger files (~5% increase)
- Slightly lower compression
- Visual quality: No noticeable difference

**Impact:** Universal playback on any device

---

### ADL-H016: NVENC GPU Encoding with CPU Fallback
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Use NVENC (GPU) encoding when available, fallback to CPU libx264

**Rationale:**
- ✅ 5-10x faster with GPU
- ✅ Doesn't compete with CPU for ML tasks
- ✅ Automatic detection and fallback
- ✅ Professional quality output

**Implementation:**
- Auto-detect NVENC availability
- Use `h264_nvenc` encoder when available
- Fallback to `libx264` (CPU) if GPU unavailable
- Clear logging of which encoder is used

**NVENC Settings:**
- Preset: `p7` (fastest) for testing, `p4-p6` for production
- Tune: `1` (high quality, not "hq" string)
- Profile: `baseline`
- Level: `3.1`

**Impact:** 5-10x faster video encoding with GPU

---

### ADL-H017: Keyframe Settings for Seeking/Playback
**Date:** Video Compatibility Fix Phase  
**Status:** Decided  
**Decision:** Regular keyframes for variable speed playback

**Settings:**
- `-g 30`: GOP size (keyframe every 30 frames = 1 second at 30fps)
- `-keyint_min 30`: Minimum keyframe interval
- `-sc_threshold 0`: Disable scene change detection (consistent keyframes)

**Rationale:**
- ✅ Enables smooth seeking
- ✅ Supports variable speed playback (1.25x, 1.5x, 2x)
- ✅ Prevents "moov atom not found" errors
- ✅ Better streaming support

**Impact:** Smooth playback at any speed, reliable seeking

---

### ADL-H018: Audio Format Decisions
**Date:** Early Development  
**Status:** Decided  
**Decisions:**
- **Audio Codec:** AAC (universal compatibility)
- **Audio Bitrate:** 192k (good quality, reasonable size)
- **Sample Rate:** 44100 Hz (standard)
- **Channels:** Stereo (2 channels)

**Rationale:**
- ✅ AAC plays everywhere
- ✅ Good quality-to-size ratio
- ✅ Standard rates ensure compatibility

**Impact:** Consistent audio quality across all outputs

---

### ADL-H019: Quality Presets System
**Date:** Recent (Video Quality Selection)  
**Status:** Decided  
**Decision:** Four-tier quality preset system

**Presets:**
1. **fastest**: 854x480, fastest encoding, testing
2. **fast**: 1280x720, fast encoding
3. **medium**: 1280x720, balanced
4. **high**: 1920x1080, best quality

**Rationale:**
- ✅ Users choose speed vs quality trade-off
- ✅ Fastest preset for testing/iteration
- ✅ High preset for final production

**Implementation:**
- Configurable per video
- CLI flag: `--quality fastest|fast|medium|high`
- UI dropdown selection
- Default: `fastest` for testing

**Impact:** Flexible quality control for different use cases

---

### ADL-H020: Video Resolution and Frame Rate
**Date:** Project Inception  
**Status:** Decided  
**Decisions:**
- **Default Resolution:** 1920x1080 (Full HD)
- **Frame Rate:** 30 FPS (standard)
- **Aspect Ratio:** 16:9 (standard)

**Rationale:**
- ✅ Professional quality
- ✅ Standard format
- ✅ Good for most platforms
- ✅ Reasonable file sizes

**Configurable:** Resolution and FPS can be adjusted per quality preset

**Impact:** Professional output quality

---

### ADL-H021: FastStart Flag for Web Optimization
**Date:** Video Compatibility Fix Phase  
**Status:** Decided  
**Decision:** Always use `+faststart` flag for MP4 files

**Rationale:**
- ✅ Places `moov` atom at beginning of file
- ✅ Instant playback in web browsers
- ✅ Better for streaming
- ✅ No downside

**Implementation:**
- `-movflags +faststart` in all FFmpeg commands
- Ensures proper positioning before container format flag

**Impact:** Videos start playing immediately online

---

### ADL-H022: Audio Visualization Generation Method
**Date:** Visualization Feature Addition  
**Status:** Decided  
**Decision:** FFmpeg-based visualization encoding instead of MoviePy

**Original:** MoviePy (CPU-only, slower)  
**Changed To:** FFmpeg with NVENC (GPU-accelerated)

**Rationale:**
- ✅ 5-10x faster with GPU
- ✅ Better quality
- ✅ Consistent with rest of video pipeline

**Implementation:**
- Generate visualization frames with PIL/librosa
- Encode video with FFmpeg + NVENC
- Fallback to MoviePy if FFmpeg fails

**Impact:** Much faster visualization generation

---

## GUI/Interface Decisions

### ADL-H023: Multiple Interface Options
**Date:** GUI Implementation Phase  
**Status:** Decided  
**Decision:** Support CLI, Web (Gradio), and Desktop (Tkinter)

**Rationale:**
- ✅ CLI for automation/scripts
- ✅ Web for easy access
- ✅ Desktop for offline use
- ✅ Users choose their preference

**Implementation Priority:**
1. CLI (primary, first implemented)
2. Web GUI (optional, Gradio)
3. Desktop GUI (optional, Tkinter)

**Impact:** Flexible access methods for different users

---

### ADL-H024: Web Interface Default Port
**Date:** Web GUI Implementation  
**Status:** Decided  
**Decision:** Port 7861 for Gradio web interface

**Rationale:**
- ✅ Non-standard port (avoids conflicts)
- ✅ Gradio default port range
- ✅ Easy to remember
- ✅ Configurable if needed

**Impact:** Consistent access URL

---

### ADL-H025: Video Quality Selection in UI
**Date:** Recent (Quality Presets)  
**Status:** Decided  
**Decision:** Quality dropdown in both Web and Desktop UIs

**Options:**
- "Fastest (Testing)" → `fastest` preset
- "Fast (720p)" → `fast` preset
- "Medium (720p)" → `medium` preset
- "High (1080p)" → `high` preset

**Default:** "Fastest (Testing)"

**Rationale:**
- ✅ Users can choose quality
- ✅ Clear naming (includes resolution)
- ✅ Fastest default for testing

**Impact:** User control over encoding speed/quality

---

## Quality & Compatibility Decisions

### ADL-H026: Universal Device Compatibility Priority
**Date:** Video Compatibility Fix Phase  
**Status:** Decided  
**Decision:** Prioritize universal compatibility over file size optimization

**Manifestation:**
- H.264 baseline profile (not high)
- Level 3.1 (not higher)
- Standard pixel formats
- Regular keyframes

**Rationale:**
- ✅ "Play on any device without additional downloads, drivers"
- ✅ User requirement for universal playback
- ✅ Better user experience

**Trade-off:** Slightly larger files acceptable for compatibility

---

### ADL-H027: Post-Encoding Verification
**Date:** Video Compatibility Fix Phase  
**Status:** Decided  
**Decision:** Verify video files after encoding

**Checks:**
1. File exists and is not empty
2. Valid MP4 structure (via `ffprobe`)
3. Error reporting if validation fails

**Rationale:**
- ✅ Catch encoding errors early
- ✅ Ensure file integrity
- ✅ Better debugging

**Implementation:**
- `ffprobe` validation after encoding
- Clear error messages if validation fails

**Impact:** Higher confidence in output quality

---

### ADL-H028: Default Video Output Format
**Date:** Project Inception  
**Status:** Decided  
**Decision:** MP4 container format

**Rationale:**
- ✅ Universal compatibility
- ✅ Works everywhere
- ✅ Good compression
- ✅ Industry standard

**Alternatives Considered:**
- MKV (better quality but less compatible)
- AVI (older, larger files)
- WebM (web-focused but less universal)

**Impact:** Wide compatibility out of the box

---

## Performance Optimization Decisions

### ADL-H029: GPU Acceleration Strategy
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Automatic GPU detection and optimization

**Features:**
- Auto-detect NVIDIA CUDA GPUs
- Auto-enable FP16 on compatible GPUs
- Auto-enable TF32 on Ampere+ GPUs
- Auto-enable cuDNN benchmarking
- Auto-clear GPU cache between operations

**Rationale:**
- ✅ Zero configuration for users
- ✅ Maximum performance automatically
- ✅ Works on CPU if GPU unavailable

**Impact:** 10-50x performance improvement with GPU

---

### ADL-H030: FP16 Mixed Precision
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Enable FP16 automatically on RTX/V100+ GPUs

**Rationale:**
- ✅ 2x faster inference
- ✅ Half the memory usage
- ✅ Minimal quality loss
- ✅ Automatic detection

**Auto-enabled:** When Tensor Cores detected (compute capability >= 7.0)

**Impact:** 2x speedup on compatible GPUs

---

### ADL-H031: TF32 Acceleration
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Enable TF32 on Ampere+ GPUs (RTX 30/40 series)

**Rationale:**
- ✅ 8x faster matrix operations
- ✅ Minimal quality impact
- ✅ Automatic on compatible hardware

**Auto-enabled:** When compute capability >= 8.0

**Impact:** Significant speedup on RTX 30/40 series

---

### ADL-H032: cuDNN Benchmarking
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Enable cuDNN benchmark mode for optimal algorithms

**Rationale:**
- ✅ Finds fastest convolution algorithms
- ✅ One-time cost (cached)
- ✅ Significant speedup for repeated operations

**Trade-off:** Slight startup delay on first run per input size

**Impact:** Optimal GPU algorithm selection

---

### ADL-H033: torch.compile for PyTorch 2.0+
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Use `torch.compile` when available (PyTorch 2.0+)

**Rationale:**
- ✅ 20-30% faster inference
- ✅ JIT compilation optimization
- ✅ Automatic when PyTorch 2.0+ detected

**Impact:** Additional performance boost

---

### ADL-H034: Memory Management Strategy
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Aggressive GPU cache clearing

**Implementation:**
- Clear cache between major steps (TTS → Music → Avatar)
- Configurable `clear_cache_between_steps`
- Max memory usage: 90% of VRAM

**Rationale:**
- ✅ Prevent out-of-memory errors
- ✅ Allow larger models
- ✅ Better stability

**Impact:** Can run larger models, fewer OOM errors

---

### ADL-H035: Batch Size Optimization
**Date:** GPU Optimization Phase  
**Status:** Decided  
**Decision:** Auto-adjust batch size based on GPU memory

**Logic:**
- Small GPU (6GB): Batch size 1
- Medium GPU (8-12GB): Batch size 2
- Large GPU (24GB+): Batch size 4

**Rationale:**
- ✅ Optimal performance per GPU
- ✅ Prevents OOM errors
- ✅ Automatic configuration

**Impact:** Best performance for each GPU tier

---

## Testing & QA Decisions

### ADL-H036: Pytest as Test Framework
**Date:** Testing Implementation  
**Status:** Decided  
**Decision:** pytest over unittest/nose2

**Rationale:**
- ✅ Modern Python testing
- ✅ Rich plugin ecosystem
- ✅ Better fixtures and parametrization
- ✅ Industry standard

**Impact:** Comprehensive test suite (286 tests)

---

### ADL-H037: Test Coverage Target
**Date:** Testing Phase  
**Status:** Decided  
**Decision:** 30% minimum coverage enforced, target higher for core modules

**Current Status:**
- Overall: ~31%
- Core modules: 48-100%
- Test suite: 286 passing tests

**Rationale:**
- ✅ Balance between coverage and development speed
- ✅ Focus on critical paths
- ✅ CI/CD enforcement

**Impact:** Maintainable code quality

---

### ADL-H038: CI/CD Pipeline
**Date:** QA Phase  
**Status:** Decided  
**Decision:** GitHub Actions for automated testing

**Features:**
- Multi-platform testing (Ubuntu + Windows)
- Multi-version testing (Python 3.10, 3.11, 3.12)
- Automated formatting (Black)
- Automated linting (Flake8)
- Automated security scanning (Bandit)
- Coverage tracking

**Rationale:**
- ✅ Catch issues early
- ✅ Ensure cross-platform compatibility
- ✅ Maintain code quality automatically

**Impact:** Professional development workflow

---

### ADL-H039: Code Formatting Standard
**Date:** Code Quality Phase  
**Status:** Decided  
**Decision:** Black formatter with strict settings

**Rationale:**
- ✅ Consistent code style
- ✅ Zero configuration
- ✅ Automated in CI/CD
- ✅ Industry standard

**Impact:** Consistent, readable codebase

---

### ADL-H040: Linting Standard
**Date:** Code Quality Phase  
**Status:** Decided  
**Decision:** Flake8 for linting

**Rationale:**
- ✅ Catches common errors
- ✅ Enforces style
- ✅ Fast execution
- ✅ Good Python support

**Impact:** Higher code quality

---

## Storage & Organization Decisions

### ADL-H041: Directory Structure Organization
**Date:** Project Inception  
**Status:** Decided  
**Decision:** Organized directory structure

**Structure:**
```
data/
  ├── scripts/        # Input scripts
  ├── outputs/        # Generated videos
  ├── cache/          # Temporary files (TTS, mixed audio)
  └── models/         # AI models (downloaded)
```

**Rationale:**
- ✅ Clear separation
- ✅ Easy to find outputs
- ✅ Cache management
- ✅ Clean organization

**Impact:** Easy navigation and management

---

### ADL-H042: Output Naming Strategy
**Date:** Early Development  
**Status:** Decided  
**Decision:** Default: timestamp-based names, customizable via `--output`

**Default Format:** `podcast_YYYYMMDD_HHMMSS`

**Rationale:**
- ✅ Unique names (no overwrites)
- ✅ Chronological sorting
- ✅ Custom names for important outputs

**Impact:** No accidental overwrites, easy organization

---

### ADL-H043: Cache Management
**Date:** Early Development  
**Status:** Decided  
**Decision:** Automatic cache cleanup with retention policy

**Settings:**
- Auto-cleanup: Enabled
- Retention: 7 days
- Cache locations: Separate for TTS, music, mixed audio

**Rationale:**
- ✅ Prevents disk space issues
- ✅ Automatic management
- ✅ Configurable retention

**Impact:** Disk space management without manual intervention

---

### ADL-H044: Script Storage Location
**Date:** Recent  
**Status:** Decided  
**Decision:** `Creations/Scripts/` for user scripts

**Rationale:**
- ✅ Clear user-facing location
- ✅ Separate from system files
- ✅ Easy to find

**Output Location:** `Creations/MMedia/` for multimedia outputs

**Impact:** Clear user workflow

---

## Audio/Video Feature Decisions

### ADL-H045: Audio Visualization Feature
**Date:** Visualization Feature Addition  
**Status:** Decided  
**Decision:** Add optional audio-reactive visualization

**Styles Supported:**
- Waveform (default)
- Spectrum
- Circular
- Particles

**Rationale:**
- ✅ Enhances video quality
- ✅ Audio-reactive (dynamic)
- ✅ Optional (flag-based)
- ✅ Multiple styles

**Implementation:**
- Default visualization style: `waveform`
- Colors: Blue primary, Pink secondary
- Can overlay on background or avatar

**Impact:** More engaging videos

---

### ADL-H046: Visualization Default Behavior
**Date:** Recent (Feature Fix)  
**Status:** Decided  
**Decision:** Visualization enabled by default, can be disabled with `--no-visualize`

**Original:** Opt-in (`--visualize` flag)  
**Changed To:** Opt-out (`--visualize` default True)

**Rationale:**
- ✅ Better default experience
- ✅ Users get visual enhancement automatically
- ✅ Can disable if not wanted

**Impact:** Better default output quality

---

### ADL-H047: Background Image Feature
**Date:** Background Feature Addition  
**Status:** Decided  
**Decision:** Support static background images with proper scaling

**Implementation:**
- Default gradient background (1920x1080)
- Custom background image support
- Proper aspect ratio handling (scale + pad)
- Dark blue padding color (`0x141E30`)

**Rationale:**
- ✅ Professional appearance
- ✅ Customizable
- ✅ Maintains aspect ratio
- ✅ Always visible (no cropping)

**Impact:** Professional-looking videos

---

### ADL-H048: Avatar/Lip-Sync Feature Priority
**Date:** Avatar Feature Implementation  
**Status:** Decided  
**Decision:** Avatar generation optional, with graceful fallback

**Priority Order:**
1. Avatar video (if available)
2. Visualization with background
3. Background only
4. Minimal video (black frame + audio)

**Rationale:**
- ✅ Avatar is optional (requires models)
- ✅ Always produces valid output
- ✅ Graceful degradation

**Fallback Strategy:**
- If avatar generation fails → use visualization + background
- If visualization fails → use background only
- If background fails → use minimal video

**Impact:** Robust output generation

---

### ADL-H049: Avatar Engine Preference
**Date:** Avatar Implementation  
**Status:** Decided  
**Decision:** Wav2Lip as default, SadTalker as alternative

**Default:** Wav2Lip
- Fast
- Good lip-sync accuracy
- Lower VRAM requirements

**Alternative:** SadTalker
- More natural head movement
- Better quality
- Higher VRAM requirements

**Rationale:**
- ✅ Wav2Lip works well with 8GB VRAM (RTX 4060)
- ✅ SadTalker available for better quality when resources allow

**Impact:** Flexible avatar options based on hardware

---

### ADL-H050: Visualization Overlay Strategy
**Date:** Recent (Feature Fix)  
**Status:** Decided  
**Decision:** Visualization overlays on background/avatar, doesn't replace it

**Implementation:**
- FFmpeg `blend` filter (70% opacity)
- Visualization on bottom layer
- Background/avatar on top layer
- Combined via blend mode

**Rationale:**
- ✅ Both visible simultaneously
- ✅ Audio-reactive visualization
- ✅ Professional appearance

**Impact:** Rich visual output

---

## Audio Mixing Decisions

### ADL-H051: Simple Ducking Implementation
**Date:** Audio Mixer Implementation  
**Status:** Decided  
**Decision:** Simple volume reduction ducking (not smart VAD-based)

**Implementation:**
- Fixed music reduction: -15dB
- No voice activity detection
- Simple overlay mixing

**Rationale:**
- ✅ Simple and reliable
- ✅ Good enough for most use cases
- ✅ Fast processing
- ✅ No additional dependencies

**Future Enhancement:** Smart ducking with VAD (noted but not prioritized)

**Impact:** Clear voice with background music

---

### ADL-H052: Music Looping Strategy
**Date:** Audio Mixer Implementation  
**Status:** Decided  
**Decision:** Auto-loop music to match voice duration

**Implementation:**
- Calculate loops needed
- Repeat music until longer than voice
- Trim to exact voice length

**Rationale:**
- ✅ Seamless background music
- ✅ Works with any voice length
- ✅ No gaps

**Impact:** Continuous background music

---

### ADL-H053: Music Start Offset Support
**Date:** Audio Mixer Implementation  
**Status:** Decided  
**Decision:** Support `--music-offset` to start music at specific time

**Rationale:**
- ✅ Skip intros/outros
- ✅ Start at preferred section
- ✅ Flexible music usage

**Impact:** Better music selection control

---

## Character & Voice Decisions

### ADL-H054: Character: Vivienne Sterling
**Date:** Project Inception  
**Status:** Decided  
**Decision:** British female presenter named "Vivienne Sterling"

**Characteristics:**
- Name: Vivienne Sterling
- Voice: British Female (Received Pronunciation)
- Personality: Professional, warm, engaging
- Setting: Modern recording studio

**Rationale:**
- ✅ Professional podcast host persona
- ✅ Clear British identity
- ✅ Engaging but not overly enthusiastic

**Impact:** Consistent brand identity

---

## Recent Advanced Script Format Decisions

### ADL-H055: New Script Format (No Backward Compatibility)
**Date:** 2025-11-03  
**Status:** Decided  
**Decision:** Support only new advanced format, no old `[MUSIC:]` format support

**Rationale:**
- ✅ Private alpha (no existing users to break)
- ✅ Clean codebase (no legacy code)
- ✅ Focus on best format from day one
- ✅ Faster development

**New Format Features:**
- Stage directions
- Pacing markers (`[pause Xs]`, `(beat)`)
- Complex sound cues with timing/volume
- Voice direction markers
- Production notes section

**Impact:** Modern, feature-rich script format

---

### ADL-H056: Audio Effects Library - pedalboard + pydub Hybrid
**Date:** 2025-11-03  
**Status:** Decided  
**Decision:** Use pedalboard for professional effects, pydub for mixing

**Rationale:**
- ✅ Professional-grade effects (EQ, compression, reverb, de-esser)
- ✅ Easy integration
- ✅ Best of both worlds (effects + mixing)
- ✅ Maintained by Spotify

**Implementation:**
- pedalboard for audio processing pipeline
- pydub for mixing/timing/format handling
- Easy conversion between formats

**Impact:** Professional audio quality

---

### ADL-H057: Configurable Timing Precision
**Date:** 2025-11-03  
**Status:** Decided  
**Decision:** Hybrid precision system (frame-based for video, time-based for audio)

**Precision Modes:**
- `auto`: Smart default based on media type
  - Video → Frame-based (~33ms at 30fps)
  - Audio → Time-based (100ms)
- `video_sync`: Frame-based for video
- `audio_only`: Time-based (100ms)
- `professional`: 10ms (future)
- `sample_accurate`: ~0.023ms (future)

**Rationale:**
- ✅ Right precision for each use case
- ✅ Future-proof (easy upgrades)
- ✅ Free tools (pydub, librosa, scipy)
- ✅ Configurable per media type

**Impact:** Optimal precision without over-engineering

---

### ADL-H058: Hybrid Pause Implementation
**Date:** 2025-11-03  
**Status:** Decided  
**Decision:** SSML for Coqui, post-process for gTTS

**Strategy:**
- Use SSML pause markers where supported (Coqui)
- Post-process pauses for engines without SSML (gTTS)
- Auto-detect engine capabilities
- Natural-sounding pauses prioritized

**Rationale:**
- ✅ Natural-sounding voice is paramount
- ✅ Works with all engines
- ✅ Best quality per engine
- ✅ Ready for premium engines (SSML-capable)

**Impact:** High-quality pauses for all TTS engines

---

## Implied/Inferred Decisions

### ADL-H059: Default to Quality-First Approach
**Date:** Throughout Project  
**Status:** Implied  
**Decision:** Prioritize quality over speed in default settings

**Manifestations:**
- Default resolution: 1920x1080 (not lower)
- Default audio bitrate: 192k (not lower)
- Baseline profile for compatibility (user requirement)
- Quality presets available (but defaults are good)

**Rationale:**
- ✅ Professional output
- ✅ User satisfaction
- ✅ Can reduce quality if needed

---

### ADL-H060: Error Handling Philosophy
**Date:** Throughout Development  
**Status:** Implied  
**Decision:** Graceful degradation over hard failures

**Manifestations:**
- Fallback chains (FFmpeg → MoviePy, GPU → CPU, etc.)
- Continue without optional features if they fail
- Clear error messages
- Partial success (e.g., voice-only if mixing fails)

**Rationale:**
- ✅ Better user experience
- ✅ System remains usable
- ✅ Clear feedback on what worked/failed

---

### ADL-H061: Documentation-First Approach
**Date:** Throughout Project  
**Status:** Implied  
**Decision:** Comprehensive documentation as project evolves

**Manifestations:**
- Extensive README and guides
- Architecture documentation
- Setup guides for each feature
- Troubleshooting sections
- Decision logs (this document)

**Rationale:**
- ✅ User self-service
- ✅ Knowledge preservation
- ✅ Easier onboarding

---

### ADL-H062: Open Source Component Preference
**Date:** Project Inception  
**Status:** Implied  
**Decision:** Prefer open-source components when possible

**Manifestations:**
- Coqui TTS (open source)
- MusicGen (Meta, open source)
- Wav2Lip/SadTalker (open source)
- Free options available alongside premium

**Rationale:**
- ✅ No vendor lock-in
- ✅ Cost-effective
- ✅ Community support
- ✅ Customizable

---

### ADL-H063: Windows-First Development (Inferred)
**Date:** Throughout Development  
**Status:** Implied  
**Decision:** Primary development on Windows, cross-platform support

**Manifestations:**
- PowerShell scripts
- Windows paths in examples
- Windows-specific troubleshooting
- But Python code is cross-platform

**Rationale:**
- ✅ Developer's primary platform
- ✅ But maintains cross-platform compatibility

---

### ADL-H064: Feature Flag System
**Date:** Feature Evolution  
**Status:** Implied  
**Decision:** Optional features via flags, not hard dependencies

**Manifestations:**
- `--visualize` flag for visualization
- `--background` flag for backgrounds
- `--avatar` flag for lip-sync
- `--audio-only` for audio output
- `--preview` for quick preview

**Rationale:**
- ✅ Flexible output options
- ✅ Faster generation when features not needed
- ✅ User control

---

### ADL-H065: Minimal Default Output
**Date:** Video Composer Implementation  
**Status:** Implied  
**Decision:** Default to minimal video (black frame + audio) unless flags specified

**Rationale:**
- ✅ Fastest generation by default
- ✅ Users explicitly enable features
- ✅ Good for testing

**Changed:** Visualization/avatar now enabled by default in recent update

---

## Decision Categories Summary

### By Category:

**Architecture & Design:** 5 decisions (H001-H005)  
**Technology Stack:** 6 decisions (H006-H011)  
**TTS Engines:** 3 decisions (H012-H014)  
**Video/Audio Processing:** 8 decisions (H015-H022)  
**GUI/Interface:** 3 decisions (H023-H025)  
**Quality & Compatibility:** 3 decisions (H026-H028)  
**Performance Optimization:** 7 decisions (H029-H035)  
**Testing & QA:** 5 decisions (H036-H040)  
**Storage & Organization:** 4 decisions (H041-H044)  
**Audio/Video Features:** 6 decisions (H045-H050)  
**Audio Mixing:** 3 decisions (H051-H053)  
**Character & Voice:** 1 decision (H054)  
**Advanced Script Format:** 4 decisions (H055-H058)  
**Implied/Inferred:** 7 decisions (H059-H065)  

**Total Decisions Documented: 65**

---

## Decisions Not Yet Made (Future)

### Potential Future Decisions:
- Multi-language support approach
- Real-time preview implementation
- Voice cloning training methodology
- Scene transition system
- Subtitle generation engine
- Platform upload automation
- Multi-character dialogue handling

---

## Review and Updates

**This document should be reviewed:**
- When making new architectural decisions
- When revisiting old decisions
- When project requirements change
- Quarterly for relevance

**Last Updated:** 2025-11-03  
**Next Review:** 2026-02-03

---

## Notes

- Some decisions were explicitly documented (e.g., in ADL/ folder)
- Some decisions were inferred from code/configuration
- Some decisions were implied from patterns and conventions
- All decisions reflect the project's evolution and priorities

**This document serves as a complete historical record for:**
- Understanding why things are built the way they are
- Onboarding new developers
- Avoiding repeated discussions
- Making informed future decisions

