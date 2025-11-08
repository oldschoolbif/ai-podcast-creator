# 🎬 Avatar Setup Guide - Complete Instructions

This guide will help you set up **SadTalker** and **Wav2Lip** for AI-generated lip-syncing avatars with waveform visualization.

---

## 📋 Quick Links

- **SadTalker GitHub**: https://github.com/OpenTalker/SadTalker
- **Wav2Lip GitHub**: https://github.com/Rudrabha/Wav2Lip
- **D-ID API Pricing**: https://studio.d-id.com/pricing

---

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Script (Windows PowerShell)

```powershell
cd D:\dev\AI_Podcast_Creator
.\setup_avatar_models.ps1 -All
```

This will:
- Clone SadTalker repository
- Download Wav2Lip models
- Install dependencies
- Verify installation

### Option 2: Manual Setup

Follow the detailed instructions below.

---

## 1️⃣ SadTalker Setup

### Step 1: Clone Repository

```powershell
cd D:\dev\AI_Podcast_Creator
mkdir external
cd external
git clone https://github.com/OpenTalker/SadTalker.git
```

### Step 2: Install Dependencies

```powershell
cd SadTalker
pip install -r requirements.txt
pip install face-alignment gfpgan basicsr facexlib
```

### Step 3: Download Models

**Option A: Automatic Download (First Use)**
- Models will auto-download on first generation
- Requires internet connection

**Option B: Manual Download**
1. Visit: https://github.com/OpenTalker/SadTalker#model-weights
2. Download required models to `external/SadTalker/checkpoints/`
3. Required files:
   - `checkpoints/auido2pose_ckpt/auido2pose.ckpt`
   - `checkpoints/auido2exp_ckpt/auido2exp.ckpt`
   - `checkpoints/auido2head_ckpt/auido2head.ckpt`
   - `checkpoints/pretrained_models/*.pth`

**Total Size**: ~2-3 GB

### Step 4: Test SadTalker

```powershell
python -m src.cli.main create Creations/Scripts/example_short_demo.txt --avatar -o test_sadtalker
```

**Expected Performance (RTX 4060)**:
- GPU Usage: 70-90%
- Generation Time: 30-60 seconds for 10-second video
- Quality: High quality natural movement

---

## 2️⃣ Wav2Lip Setup

### Step 1: Create Models Directory

```powershell
cd D:\dev\AI_Podcast_Creator
mkdir models
```

### Step 2: Download Models

**Wav2Lip Model (~98 MB)**:
```powershell
cd models
Invoke-WebRequest -Uri "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0.0/wav2lip_gan.pth" -OutFile "wav2lip_gan.pth"
```

**Face Detection Model (~50 MB)**:
```powershell
Invoke-WebRequest -Uri "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" -OutFile "s3fd.pth"
```

### Step 3: Install Dependencies

```powershell
pip install opencv-python opencv-contrib-python librosa==0.9.2 batch-face facexlib
```

### Step 4: Update Config

Edit `config.yaml`:
```yaml
avatar:
  engine: "wav2lip"  # Change from "sadtalker"
```

### Step 5: Test Wav2Lip

```powershell
python -m src.cli.main create Creations/Scripts/example_short_demo.txt --avatar -o test_wav2lip
```

**Expected Performance (RTX 4060)**:
- GPU Usage: 40-60%
- Generation Time: 15-30 seconds for 10-second video
- Quality: Very accurate lip-sync

---

## 3️⃣ D-ID API (Cloud Service)

### Pricing Information

**Official Pricing Page**: https://studio.d-id.com/pricing

**Estimated Costs**:
- **Pay-as-you-go**: ~$0.10-$0.50 per video (varies by resolution/duration)
- **Subscription Plans**: Available on pricing page
- **Free Tier**: Limited credits for testing

### Setup Steps

1. **Sign Up**: Visit https://studio.d-id.com/
2. **Get API Key**: Navigate to API section in dashboard
3. **Configure**:
   ```powershell
   # Add to .env file
   echo "DID_API_KEY=your_api_key_here" >> .env
   ```
4. **Update Config**:
   ```yaml
   avatar:
     engine: "did"
     did:
       api_key: "${DID_API_KEY}"
       presenter_id: "amy-jcwCkr1grs"  # Or choose another
   ```

### Advantages
- ✅ **Easiest Setup**: Just API key
- ✅ **Highest Quality**: Professional-grade output
- ✅ **No Local Resources**: Runs in cloud
- ✅ **Scalable**: Unlimited generation capacity

### Disadvantages
- ❌ **Cost**: Pay per video ($0.10-$0.50 each)
- ❌ **Internet Required**: Must be online
- ❌ **Privacy**: Videos processed in cloud

---

## 🎯 Comparison

| Feature | SadTalker | Wav2Lip | D-ID API |
|---------|-----------|---------|----------|
| **Setup Complexity** | Medium | Low | Very Easy |
| **Local Setup** | Yes (2-3GB) | Yes (200MB) | No |
| **GPU Required** | Yes (6GB+) | Yes (4GB+) | No |
| **Generation Speed** | 30-60s | 15-30s | 30-120s (cloud) |
| **Quality** | High | Very High | Highest |
| **Cost** | Free | Free | $0.10-$0.50/video |
| **Internet** | Optional | Optional | Required |
| **Privacy** | Local | Local | Cloud |

---

## 🧪 Testing Avatar + Waveform

Once either SadTalker or Wav2Lip is set up:

```powershell
python -m src.cli.main create Creations/Scripts/example_short_demo.txt --avatar --visualize -o test_complete
```

This will create:
1. TTS audio (British female voice)
2. Lip-synced avatar video
3. Waveform visualization
4. Final video: Avatar overlaid on waveform with GPU encoding

**Expected Output**:
- Video: `Creations/MMedia/test_complete.mp4`
- Resolution: 1920x1080 @ 30fps
- Codec: H.264 (GPU-accelerated via NVENC)
- Features: Animated avatar + reactive waveform

---

## 🔧 Troubleshooting

### SadTalker: "Model not found"
- Models auto-download on first use (requires internet)
- Or download manually from GitHub releases
- Check: `external/SadTalker/checkpoints/` directory

### Wav2Lip: "Model not found"
- Verify: `models/wav2lip_gan.pth` exists
- Download from: https://github.com/Rudrabha/Wav2Lip/releases
- Check: `models/s3fd.pth` for face detection

### "CUDA out of memory"
- Reduce batch size in config
- Use smaller avatar size
- Close other GPU applications

### "GPU not being used"
- Check PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- Verify CUDA drivers: `nvidia-smi`
- See `SADTALKER_GPU_SETUP.md` for GPU optimization

---

## 📚 Additional Resources

- **SadTalker Documentation**: https://github.com/OpenTalker/SadTalker
- **Wav2Lip Documentation**: https://github.com/Rudrabha/Wav2Lip
- **D-ID API Docs**: https://docs.d-id.com/
- **GPU Optimization Guide**: `GPU_OPTIMIZATION_GUIDE.md`
- **SadTalker GPU Setup**: `SADTALKER_GPU_SETUP.md`
- **Wav2Lip Setup**: `WAV2LIP_SETUP.md`

---

## ✅ Success Checklist

- [ ] SadTalker cloned and dependencies installed
- [ ] Wav2Lip models downloaded
- [ ] Config updated with correct engine
- [ ] Test generation successful
- [ ] Avatar + Waveform combination working
- [ ] GPU encoding confirmed

---

**Ready to create lip-synced avatars with waveform backgrounds!** 🎬✨

