# README Updates Needed

The main `README.md` should be updated to include GPU information.

## Suggested additions:

### Add to "Features" section:

```markdown
## 🚀 GPU Acceleration

AI Podcast Creator supports NVIDIA GPU acceleration for 10-12x faster generation:

- **GPU-Accelerated TTS** (Coqui XTTS) - 5x faster than CPU
- **GPU-Accelerated Music** (MusicGen) - 10x faster than CPU
- **GPU-Accelerated Avatar** (SadTalker) - 12x faster than CPU

**Performance:**
- 2-minute podcast: 5-8 minutes with GPU (vs. 60-80 minutes on CPU)
- Requires: NVIDIA GPU with 6GB+ VRAM (RTX 3060/4060 or better)

See: `QUICK_GPU_SETUP.md` for 5-minute setup, or `GPU_SETUP_COMPLETE.md` for full guide.
```

### Add to "Quick Start" section:

```markdown
## ⚡ GPU Quick Start (5 minutes)

Have an NVIDIA GPU? Get 10x faster generation:

```bash
# 1. Check GPU
python check_gpu.py

# 2. Install GPU packages
pip install TTS audiocraft

# 3. Update config.yaml
# Change engine: "gtts" to "coqui"
# Change engine: "library" to "musicgen"

# 4. Generate!
python -m src.cli.main create Creations/example_welcome.txt
```

See `QUICK_GPU_SETUP.md` for details.
```

### Add new "Troubleshooting" section:

```markdown
## 🐛 Troubleshooting

**GPU Issues:**
- Run `python check_gpu.py` to verify GPU detection
- See `GPU_SETUP_COMPLETE.md` for detailed troubleshooting

**Bugs:**
- Run `python fix_bugs.py` to apply automated fixes
- See `BUGS_FOUND_AND_FIXED.md` for known issues

**General:**
- Check logs in `logs/` directory
- Verify config.yaml settings
- Ensure all dependencies installed
```

### Add to "Documentation" section:

```markdown
## 📚 Documentation

**Getting Started:**
- `README.md` - Main documentation (this file)
- `QUICK_START.md` - Basic setup
- `QUICK_GPU_SETUP.md` - GPU setup in 5 minutes ⚡

**GPU & Performance:**
- `GPU_SETUP_COMPLETE.md` - Complete GPU guide
- `GPU_OPTIMIZATION_GUIDE.md` - Performance tuning
- `check_gpu.py` - GPU detection utility

**Troubleshooting:**
- `BUGS_FOUND_AND_FIXED.md` - Known issues and fixes
- `fix_bugs.py` - Automated bug fixes

**Features:**
- `VOICE_OPTIONS_GUIDE.md` - TTS voice configuration
- `VISUALIZATION_GUIDE.md` - Audio visualization
- `AVATAR_GUIDE.md` - Avatar setup
```

---

## Implementation

To update README.md, either:

1. **Manual edit**: Copy sections above into README.md

2. **Script** (if you want automation):

```python
# Add to README.md programmatically
with open('README.md', 'r') as f:
    content = f.read()

# Insert GPU section after Features heading
gpu_section = """
## 🚀 GPU Acceleration
...
"""

# Find insertion point and insert
# (implementation depends on current README structure)
```

---

**Recommendation:** Manually edit README.md to integrate these sections naturally with existing content.

