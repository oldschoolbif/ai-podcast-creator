# GPU Setup Guide - AI Podcast Creator

## Complete Guide to GPU-Accelerated Features

This guide will help you set up **GPU acceleration** for 10-50x faster podcast generation.

---

## Prerequisites

### ✅ What You Need:

1. **NVIDIA GPU** with 6GB+ VRAM
   - RTX 3050/3060/3070/4060/4070 or better
   - GTX 1060 6GB minimum (older, slower)
   
2. **NVIDIA Driver** 
   - Download latest: https://www.nvidia.com/download/index.aspx
   
3. **CUDA Toolkit**
   - Already included with PyTorch (no separate install needed)
   
4. **Python 3.10+**
   - With virtual environment activated

---

## Step 1: Verify GPU Setup

Run the GPU check script:

```bash
cd AI_Podcast_Creator
python check_gpu.py
```

**Expected Output:**
```
✓ PyTorch version: 2.1.0+cu118
✓ CUDA available: Yes
✓ GPU: NVIDIA GeForce RTX 4060
✓ GPU Memory: 8.0 GB
✓ GPU is ready for AI Podcast Creator!
```

**If GPU not detected:**
- Reinstall PyTorch with CUDA:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
- Check NVIDIA drivers: `nvidia-smi`
- Restart computer after driver install

---

## Step 2: GPU-Accelerated TTS (Coqui XTTS)

### Install Coqui TTS:

```bash
pip install TTS
```

### Update config.yaml:

```yaml
tts:
  engine: "coqui"  # Change from "gtts" to "coqui"
  coqui:
    model: "tts_models/multilingual/multi-dataset/xtts_v2"
    language: "en"
    speaker: "Andrew Chipper"  # Or any built-in speaker
    use_gpu: true
```

### Test:

```bash
python -m src.cli.main create Creations/example_welcome.txt
```

### Performance:
- **CPU**: 2-3 minutes for 2-min script
- **GPU**: 20-40 seconds for 2-min script
- **Speedup**: ~5-10x faster

### Voice Quality:
- ✅ Much more natural than gTTS
- ✅ British accent available
- ✅ Emotional expression
- ✅ Better prosody

---

## Step 3: GPU-Accelerated Music Generation (MusicGen)

### Install AudioCraft:

```bash
pip install audiocraft
```

### Update config.yaml:

```yaml
music:
  engine: "musicgen"  # Change from "library" to "musicgen"
  musicgen:
    model: "facebook/musicgen-medium"  # or "small" for faster, "large" for better
    duration: 10  # seconds per generation
    temperature: 1.0
    top_k: 250
    use_gpu: true
```

### Test with music generation:

```bash
python -m src.cli.main create Creations/example_educational.txt
```

(The example_educational.txt has `[MUSIC: ...]` tags)

### Performance:
- **CPU**: 10-20 minutes per music clip
- **GPU (RTX 4060)**: 1-2 minutes per music clip
- **Speedup**: ~10x faster

### Model Sizes:
| Model | Size | VRAM | Quality | Speed |
|-------|------|------|---------|-------|
| `musicgen-small` | 1.5GB | 4GB | Good | Fast |
| `musicgen-medium` | 3GB | 6GB | Better | Medium |
| `musicgen-large` | 6GB | 12GB | Best | Slow |

**For RTX 4060 (8GB VRAM):** Use `medium`

---

## Step 4: GPU-Accelerated Avatar Animation (SadTalker)

### Install SadTalker:

```bash
# Clone SadTalker repository
cd external
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

# Install dependencies
pip install -r requirements.txt

# Download pretrained models (~5GB)
bash scripts/download_models.sh

cd ../..
```

### Update config.yaml:

```yaml
avatar:
  engine: "sadtalker"  # Change from "none" to "sadtalker"
  source_image: "src/assets/avatars/default_female.jpg"
  sadtalker:
    checkpoint_dir: "external/SadTalker/checkpoints"
    config_dir: "external/SadTalker/src/config"
    still_mode: false  # true for less head movement
    expression_scale: 1.0  # 0.5-2.0, higher = more expressive
    enhancer: "gfpgan"  # Face enhancement
    use_gpu: true
```

### Test with avatar:

```bash
python -m src.cli.main create Creations/example_welcome.txt
```

### Performance:
- **CPU**: 30-60 minutes for 2-min video
- **GPU (RTX 4060)**: 3-5 minutes for 2-min video
- **Speedup**: ~10-15x faster

### VRAM Usage:
- SadTalker: ~6-7GB VRAM
- With TTS running: ~8GB total (tight fit on 8GB GPU)

**Tip:** Generate TTS first, then avatar separately if you have <12GB VRAM

---

## Step 5: Full GPU Pipeline Test

### Update config.yaml for FULL GPU mode:

```yaml
tts:
  engine: "coqui"
  coqui:
    model: "tts_models/multilingual/multi-dataset/xtts_v2"
    language: "en"
    use_gpu: true

music:
  engine: "musicgen"
  musicgen:
    model: "facebook/musicgen-medium"
    duration: 10
    use_gpu: true

avatar:
  engine: "sadtalker"
  use_gpu: true
```

### Generate full GPU-accelerated podcast:

```bash
python -m src.cli.main create Creations/example_educational.txt
```

### Expected Timeline (RTX 4060, 2-min podcast):
1. **TTS Generation**: 30 seconds
2. **Music Generation**: 1-2 minutes
3. **Audio Mixing**: 5 seconds
4. **Avatar Animation**: 3-5 minutes
5. **Video Composition**: 30 seconds

**Total**: ~5-8 minutes (vs. 45-90 minutes on CPU!)

---

## Optimization Tips

### Memory Management:

**For 8GB VRAM GPUs (like RTX 4060):**

Generate in stages to avoid OOM (Out of Memory):

```bash
# Stage 1: Audio only (uses ~3GB VRAM)
python -m src.cli.main create script.txt --preview

# Stage 2: Add avatar to existing audio (uses ~7GB VRAM)
# (This requires separate avatar command - TODO: implement)
```

**Or use smaller models:**

```yaml
music:
  musicgen:
    model: "facebook/musicgen-small"  # 1.5GB instead of 3GB
```

### Speed Optimizations:

1. **Enable FP16 (Mixed Precision):**
   - Automatically enabled on RTX 2060+
   - 2x faster with minimal quality loss

2. **Enable TF32 (RTX 3000/4000):**
   - Automatically enabled on Ampere+ GPUs
   - Up to 8x faster matrix operations

3. **Use torch.compile (PyTorch 2.0+):**
   - Automatically enabled for MusicGen
   - 10-20% speedup

4. **Clear GPU cache between generations:**
   - Automatically handled by gpu_utils.py

---

## Troubleshooting

### "CUDA out of memory" Error:

**Solution 1:** Use smaller models
```yaml
music:
  musicgen:
    model: "facebook/musicgen-small"
```

**Solution 2:** Generate in stages
```bash
# Generate audio first
python -m src.cli.main create script.txt --skip-music --preview

# Generate music separately
# (Add music later in video editor)
```

**Solution 3:** Close other GPU applications
```bash
# Check GPU usage
nvidia-smi

# Close browsers, games, other AI apps
```

### "RuntimeError: No CUDA GPUs are available":

**Check drivers:**
```bash
nvidia-smi
```

**Reinstall PyTorch with CUDA:**
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### SadTalker Not Found:

```bash
# Make sure it's in the right place
cd AI_Podcast_Creator
git clone https://github.com/OpenTalker/SadTalker.git external/SadTalker
cd external/SadTalker
bash scripts/download_models.sh
```

### Slow Performance Despite GPU:

**Check if actually using GPU:**
```python
python check_gpu.py
```

**Verify GPU is being used during generation:**
```bash
# In another terminal while generating
watch -n 1 nvidia-smi
```

You should see GPU Utilization at 80-100% during generation.

---

## Performance Comparison

### gTTS (Basic) vs. Coqui (GPU):

| Feature | gTTS | Coqui GPU |
|---------|------|-----------|
| Quality | Good | Excellent |
| Accent | British (limited) | Any (customizable) |
| Speed | 10s | 30s |
| Emotion | None | Natural |
| Voice Clone | No | Yes (advanced) |
| Cost | Free | Free |
| GPU | Not used | Required |

### CPU vs. GPU (2-minute podcast):

| Component | CPU Time | GPU Time | Speedup |
|-----------|----------|----------|---------|
| TTS | 2-3 min | 20-40s | 5x |
| Music | 15-20 min | 1-2 min | 10x |
| Avatar | 40-60 min | 3-5 min | 12x |
| **Total** | **60-80 min** | **5-8 min** | **10-12x** |

---

## Recommended Configurations

### RTX 4060 / 3060 (8GB VRAM):

```yaml
tts:
  engine: "coqui"
music:
  engine: "musicgen"
  musicgen:
    model: "facebook/musicgen-medium"  # ✓ Fits
avatar:
  engine: "sadtalker"  # ✓ Works but tight on memory
```

### RTX 4070 / 3070 (12GB VRAM):

```yaml
tts:
  engine: "coqui"
music:
  engine: "musicgen"
  musicgen:
    model: "facebook/musicgen-large"  # ✓ Better quality
avatar:
  engine: "sadtalker"  # ✓ Plenty of headroom
```

### RTX 4090 / 3090 (24GB VRAM):

```yaml
# Use all features simultaneously
# Consider batch processing multiple podcasts
# Or use higher quality settings
```

---

## Next Steps

1. ✅ **Run GPU check**: `python check_gpu.py`
2. ✅ **Enable one feature at a time**: Start with TTS
3. ✅ **Test each feature**: Make sure it works before adding next
4. ✅ **Optimize**: Find best quality/speed balance for your GPU
5. ✅ **Create content**: Generate amazing podcasts!

---

## Support

**Issues? Check:**
1. `python check_gpu.py` - Verify GPU setup
2. `nvidia-smi` - Check GPU status
3. Config file - Verify `use_gpu: true` for each feature
4. Logs - Read error messages carefully

**Common Fixes:**
- Restart computer after driver update
- Close other GPU applications
- Use smaller models if OOM errors
- Generate in stages for 6-8GB GPUs

---

**Your RTX 4060 is perfect for AI Podcast Creator!** 🚀

You should be able to run all features with medium-quality models.

Happy podcasting! 🎙️

