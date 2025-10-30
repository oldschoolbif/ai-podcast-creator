# Quick GPU Setup - 5 Minutes to GPU Power!

**For users with NVIDIA GPU who want to get started FAST.**

---

## ⚡ 5-Minute Setup

### Step 1: Check GPU (30 seconds)

```bash
cd AI_Podcast_Creator
python check_gpu.py
```

✅ If you see "GPU is ready", continue!  
❌ If not, install NVIDIA drivers first: https://www.nvidia.com/download/index.aspx

---

### Step 2: Install GPU Dependencies (2 minutes)

```bash
# Install all GPU features at once
pip install TTS audiocraft

# OR install individually:
pip install TTS           # For GPU-accelerated TTS
pip install audiocraft    # For GPU-accelerated music
```

---

### Step 3: Update Config (1 minute)

Edit `config.yaml`:

```yaml
tts:
  engine: "coqui"  # Change from "gtts"
  
music:
  engine: "musicgen"  # Change from "library"
  
# Avatar setup is optional (more complex)
```

---

### Step 4: Test It! (1 minute)

```bash
python -m src.cli.main create Creations/example_welcome.txt
```

**Expected:** GPU-accelerated generation in ~1-2 minutes!

---

## That's It!

You now have:
- ✅ GPU-accelerated TTS (Coqui)
- ✅ GPU-accelerated Music (MusicGen)
- ⚠️ Avatar still uses static image (optional advanced setup)

**For full animated avatar setup**, see: `GPU_SETUP_COMPLETE.md`

---

## Performance You'll Get

### Before (CPU):
- 2-min podcast = 60-80 minutes

### After (GPU):
- 2-min podcast = 2-3 minutes without avatar
- 2-min podcast = 5-8 minutes with avatar

**20x faster!** 🚀

---

## Quick Troubleshooting

**"CUDA out of memory":**
- Close other GPU apps
- Use smaller music model:
  ```yaml
  music:
    musicgen:
      model: "facebook/musicgen-small"
  ```

**"Model not found":**
- First run downloads models (5-10 minutes)
- Be patient!

**"Still using CPU":**
- Check `config.yaml` has `engine: "coqui"` not `"gtts"`
- Run `python check_gpu.py` to verify GPU detected

---

Happy podcasting! 🎙️

For detailed setup and avatar animation, see: `GPU_SETUP_COMPLETE.md`


