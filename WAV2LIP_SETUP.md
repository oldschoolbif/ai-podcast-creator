# 🎬 Animated Lip-Sync Setup Guide (Wav2Lip)

## Overview

This guide will help you set up **Wav2Lip** for full animated lip-sync on your podcast avatars. After setup, the avatar's mouth will move perfectly in sync with the speech!

**Current Status**: Static avatar works ✅  
**After Setup**: Animated lip-sync works ✅

---

## 📋 Prerequisites

- **GPU**: NVIDIA GPU with 4GB+ VRAM (you have RTX 4060 ✅)
- **CUDA**: Installed (you have CUDA 12.1 ✅)
- **FFmpeg**: Installed ✅
- **Python**: 3.8+ with venv activated ✅

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Install Wav2Lip dependencies
pip install opencv-python
pip install librosa==0.9.2
pip install batch-face

# Optional: Face detection improvement
pip install facexlib
```

### Step 2: Download Pre-Trained Model

**Option A: Direct Download (Recommended)**

```bash
# Create models directory
mkdir -p models

# Download model directly (using wget or browser)
cd models

# Try wget
wget https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth \
  -O s3fd.pth

# Download Wav2Lip GAN model (manual)
# Visit: https://github.com/Rudrabha/Wav2Lip
# Download: wav2lip_gan.pth (98 MB)
# Save to: /mnt/d/dev/AI_Podcast_Creator/models/wav2lip_gan.pth
```

**Option B: Clone Repository**

```bash
cd /mnt/d/dev/AI_Podcast_Creator
mkdir -p external
cd external

# Clone Wav2Lip
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip

# Follow their download instructions
bash scripts/download_models.sh
```

### Step 3: Create Inference Script

Create `scripts/wav2lip_simple.py`:

```python
#!/usr/bin/env python3
"""
Simple Wav2Lip inference for AI Podcast Creator
"""
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint_path', required=True)
    parser.add_argument('--face', required=True)
    parser.add_argument('--audio', required=True)
    parser.add_argument('--outfile', required=True)
    parser.add_argument('--device', default='cuda')
    args = parser.parse_args()
    
    try:
        # Import Wav2Lip (will need to add to path)
        sys.path.insert(0, str(Path(__file__).parent.parent / 'external' / 'Wav2Lip'))
        from inference import main as wav2lip_inference
        
        # Run inference
        wav2lip_inference(args)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## 🎬 Test Installation

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Test with short demo
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --skip-music \
  -o test_lipsync

# If successful, you should see animated lip movement!
```

---

## 🔧 Alternative: Simpler Wav2Lip Integration

If the full Wav2Lip setup is too complex, here's a simplified approach:

### Use Wav2Lip as a Library

```bash
pip install git+https://github.com/Rudrabha/Wav2Lip.git
```

### Update Avatar Generator

Edit `src/core/avatar_generator.py` to use Wav2Lip directly (already partially implemented).

---

## 📊 Performance Expectations

With your RTX 4060:

| Video Length | Generation Time | Quality |
|--------------|----------------|---------|
| 10 seconds | ~5-10 seconds | High |
| 30 seconds | ~15-30 seconds | High |
| 1 minute | ~30-60 seconds | High |
| 5 minutes | ~3-5 minutes | High |

**GPU Memory Usage**: 2-4 GB VRAM

---

## 🎨 Model Options

### wav2lip.pth (Base Model)
- Faster generation
- Good quality
- Recommended for testing

### wav2lip_gan.pth (GAN Model) ✅ Recommended
- Higher quality
- Better visual results
- Slightly slower

**Current Config**: Uses `wav2lip_gan` (best quality)

---

## 🐛 Troubleshooting

### Issue: "No module named 'cv2'"

```bash
pip install opencv-python opencv-contrib-python
```

### Issue: "Model not found"

Check that `models/wav2lip_gan.pth` exists:

```bash
ls -lh models/wav2lip_gan.pth
```

If missing, download manually from:
- https://github.com/Rudrabha/Wav2Lip/releases

###Issue: "Face not detected"

Use a clearer source image:
- Frontal face view
- Good lighting
- No obstructions
- 512x512+ resolution

### Issue: "CUDA out of memory"

Reduce resolution or use smaller image:

```yaml
# config.yaml
video:
  resolution: [1280, 720]  # Instead of 1920x1080
```

### Issue: "Lip sync quality is poor"

1. Use `wav2lip_gan.pth` (better quality)
2. Ensure high-quality audio input
3. Use a high-quality source image
4. Try a different face angle/photo

---

## 🎯 Optimization Tips

### 1. Face Quality Enhancement

Enable GFPGAN for face enhancement:

```bash
pip install gfpgan
```

Update config:

```yaml
avatar:
  wav2lip:
    enhance_face: true
    enhancer: "gfpgan"
```

### 2. Batch Processing

Process multiple scripts in sequence:

```bash
for script in Creations/*.txt; do
  python3 -m src.cli.main create "$script" \
    --avatar --visualize -o "$(basename "$script" .txt)"
done
```

### 3. GPU Memory Optimization

```yaml
processing:
  use_fp16: true  # Already enabled
  batch_size: 1   # Reduce if OOM errors
```

---

## 📚 Advanced Configuration

### Custom Face Detector

```yaml
avatar:
  wav2lip:
    face_detector: "blazeface"  # Options: s3fd, blazeface, sfd
    face_det_batch_size: 8
    wav2lip_batch_size: 128
```

### Quality vs Speed

```yaml
avatar:
  wav2lip:
    quality: "high"    # Options: fast, high, best
    fps: 25           # Reduce for faster generation
    resolution: "hd"   # Options: sd, hd, fhd
```

---

## 🔄 Fallback Strategy

The system is designed with graceful fallbacks:

1. **Preferred**: Animated Wav2Lip (requires setup)
2. **Fallback 1**: Static avatar + audio (current)
3. **Fallback 2**: Visualization only (no avatar)

You can use static avatars now and upgrade to animated later!

---

## 🎬 Example Workflows

### Simple Animated Avatar

```bash
python3 -m src.cli.main create \
  "script.txt" \
  --avatar \
  -o animated_podcast
```

### Avatar + Visualization

```bash
python3 -m src.cli.main create \
  "script.txt" \
  --avatar \
  --visualize \
  -o complete_podcast
```

### Ultimate: Avatar + Viz + Music

```bash
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  "Creations/music.mp3" \
  --avatar \
  --visualize \
  --music-offset 20 \
  -o ultimate_podcast
```

---

## 💡 Alternative Options

If Wav2Lip setup is challenging:

### Option A: Use D-ID API (Easiest)

```bash
# Install D-ID SDK
pip install d-id

# Add API key to .env
echo "DID_API_KEY=your_key_here" >> .env

# Update config
avatar:
  engine: "did"
```

**Cost**: ~$0.10-0.50 per video  
**Quality**: Highest  
**Setup**: Easiest

### Option B: Use SadTalker (Best Quality)

```bash
pip install sadtalker

# Models auto-download on first use
avatar:
  engine: "sadtalker"
```

**Quality**: Best natural movement  
**Setup**: Medium difficulty  
**GPU**: Requires 6-8GB VRAM

---

## ✅ Verification

After setup, verify Wav2Lip works:

```bash
# Check model exists
ls -lh models/wav2lip_gan.pth

# Check dependencies
python3 -c "import cv2, librosa; print('✓ Dependencies OK')"

# Test generation
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --skip-music \
  -o lipsync_test
  
# Watch the output!
```

---

## 🎯 Success Indicators

✅ No "Wav2Lip model not available" warning  
✅ No "Using static avatar fallback" message  
✅ Avatar's mouth moves with speech in output video  
✅ Generation takes longer (~2-5x) but looks better  

---

## 📖 Resources

- **Wav2Lip GitHub**: https://github.com/Rudrabha/Wav2Lip
- **Wav2Lip Paper**: https://arxiv.org/abs/2008.10010
- **Model Downloads**: Check GitHub releases
- **Issues**: https://github.com/Rudrabha/Wav2Lip/issues

---

## 🚀 Next Steps

1. **Start with static**: Your current setup works great!
2. **Try the setup**: Follow steps above when ready
3. **Test with short clips**: Use `example_short_demo.txt`
4. **Scale up**: Move to longer podcasts once working

**Remember**: Static avatars are perfectly fine for podcasts! Most podcast videos use static images. Animated lip-sync is a premium enhancement.

---

**Your system is ready for animated lip-sync! Just need to complete the Wav2Lip setup when you're ready.** 🎬✨




