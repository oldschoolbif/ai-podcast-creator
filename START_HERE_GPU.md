# 🚀 START HERE - GPU Setup for AI Podcast Creator

**Welcome! This guide will get you up and running with GPU-accelerated podcast generation in under 10 minutes.**

---

## What You Get with GPU

### Performance Boost:
- **10-12x faster generation** 🚀
- 2-minute podcast in **5-8 minutes** (vs. 60-80 minutes on CPU)
- Near real-time generation for short clips

### Better Quality:
- Natural-sounding voices (Coqui XTTS)
- AI-generated custom music (MusicGen)
- Smooth animated avatars (SadTalker)

---

## Prerequisites Check ✅

### Do you have:
1. ✅ NVIDIA GPU (RTX 3060/4060 or better)?
2. ✅ 6GB+ VRAM?
3. ✅ Windows 10/11 with latest NVIDIA drivers?

**If YES to all:** Continue! You're ready for GPU acceleration.

**If NO:** The system still works on CPU, just 10x slower.

---

## Quick Setup (10 Minutes)

### Step 1: Check GPU (30 seconds)

```bash
cd AI_Podcast_Creator
python check_gpu.py
```

**Expected output:**
```
✓ PyTorch version: 2.1.0+cu118
✓ CUDA available: Yes
✓ GPU: NVIDIA GeForce RTX 4060
✓ GPU Memory: 8.0 GB
✓ GPU is ready for AI Podcast Creator!
```

❌ **If GPU not detected:**
1. Check NVIDIA drivers: https://www.nvidia.com/download/index.aspx
2. Reinstall PyTorch:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. Restart computer
4. Run `python check_gpu.py` again

---

### Step 2: Apply Bug Fixes (1 minute)

```bash
python fix_bugs.py
```

This fixes known issues automatically.

---

### Step 3: Install GPU Packages (3 minutes)

```bash
# Install TTS for natural voices
pip install TTS

# Install AudioCraft for music generation
pip install audiocraft
```

**Note:** First-time model downloads happen during first use (5-10 minutes).

---

### Step 4: Update Configuration (2 minutes)

Edit `config.yaml` and change:

**For GPU-accelerated TTS:**
```yaml
tts:
  engine: "coqui"  # Change from "gtts"
  coqui:
    model: "tts_models/multilingual/multi-dataset/xtts_v2"
    language: "en"
    speaker: "Andrew Chipper"
    use_gpu: true
```

**For GPU-accelerated Music:**
```yaml
music:
  engine: "musicgen"  # Change from "library"
  musicgen:
    model: "facebook/musicgen-medium"  # Use "small" for 6GB GPUs
    duration: 10
    use_gpu: true
```

**Save the file.**

---

### Step 5: Test It! (3 minutes)

```bash
python -m src.cli.main create Creations/example_welcome.txt
```

**Expected:**
- GPU usage spikes (check with `nvidia-smi` in another terminal)
- Generation completes in 1-3 minutes (without avatar)
- Output in `data/outputs/`

✅ **Success!** You now have GPU-accelerated podcast creation!

---

## What's Next?

### Basic Usage (NOW):
You can now create podcasts at GPU speed:

```bash
python -m src.cli.main create your_script.txt
```

### Advanced: Avatar Animation (OPTIONAL, +30 min):
For GPU-accelerated animated avatars, see Section 4 of `GPU_SETUP_COMPLETE.md`

This requires:
- Cloning SadTalker repository
- Downloading 5GB of models
- Additional configuration

---

## Troubleshooting

### "CUDA out of memory" Error:

**Solution 1:** Use smaller music model
```yaml
music:
  musicgen:
    model: "facebook/musicgen-small"  # 1.5GB instead of 3GB
```

**Solution 2:** Close other GPU apps (browsers, games, etc.)

**Solution 3:** Generate without music first, add later

---

### "Still using CPU" / Slow Generation:

1. Verify GPU detected: `python check_gpu.py`
2. Check config.yaml has:
   - `engine: "coqui"` (not "gtts")
   - `engine: "musicgen"` (not "library")
   - `use_gpu: true`
3. Watch GPU usage while generating: `nvidia-smi`

---

### Models downloading too slow:

This is normal on first run (5-10 minutes). Models are cached for future use.

---

## Performance You Should See

### With RTX 4060 (8GB VRAM):

| Task | CPU Time | GPU Time | Your Results |
|------|----------|----------|--------------|
| TTS (2 min) | 2-3 min | 20-40s | ___ |
| Music (10s) | 15-20 min | 1-2 min | ___ |
| **Total** | **60-80 min** | **2-3 min** | ___ |

**Fill in "Your Results" after testing!**

---

## Quick Reference

### Check GPU status:
```bash
python check_gpu.py
nvidia-smi
```

### Apply bug fixes:
```bash
python fix_bugs.py
```

### Generate podcast:
```bash
python -m src.cli.main create script.txt
```

### Use GUI instead:
```bash
python launch_web_gui.py
# Opens at http://localhost:7860
```

---

## Documentation Quick Links

- 📖 **Main README**: [README.md](README.md)
- ⚡ **This Guide**: START_HERE_GPU.md (you are here)
- 🚀 **5-Min Setup**: [QUICK_GPU_SETUP.md](QUICK_GPU_SETUP.md)
- 📚 **Complete Guide**: [GPU_SETUP_COMPLETE.md](GPU_SETUP_COMPLETE.md)
- 🐛 **Bugs & Fixes**: [BUGS_FOUND_AND_FIXED.md](BUGS_FOUND_AND_FIXED.md)

---

## Support

**Still stuck?**

1. Run: `python check_gpu.py`
2. Check: [GPU_SETUP_COMPLETE.md](GPU_SETUP_COMPLETE.md) Troubleshooting section
3. Review: [BUGS_FOUND_AND_FIXED.md](BUGS_FOUND_AND_FIXED.md)
4. Search: Existing GitHub issues
5. Create: New GitHub issue with output from `check_gpu.py`

---

## Success Checklist

- [ ] Ran `python check_gpu.py` → GPU detected ✓
- [ ] Ran `python fix_bugs.py` → Fixes applied ✓
- [ ] Installed TTS and AudioCraft packages ✓
- [ ] Updated config.yaml with GPU settings ✓
- [ ] Tested generation → Works at GPU speed ✓
- [ ] Committed changes to GitHub ✓

**All checked?** You're ready to create amazing podcasts! 🎙️✨

---

## Pro Tips

1. **Cache is your friend**: Generated audio/music is cached. Regenerating the same script is instant!

2. **Start small**: Test with short scripts first (30 seconds) to verify GPU is working.

3. **Monitor GPU**: Keep `nvidia-smi` open in another terminal to see GPU usage.

4. **Quality vs Speed**: Use `musicgen-small` for speed, `musicgen-medium` for quality.

5. **GPU at 100%**: If GPU utilization is at 100%, that's GOOD! It means it's working hard.

---

**Ready? Run this now:**

```bash
cd AI_Podcast_Creator
python check_gpu.py
```

Then follow the steps above! 🚀

---

*Your GPU is about to make podcast creation 10x faster. Let's go!* 🎙️⚡

