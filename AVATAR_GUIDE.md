# 🎭 Talking Head Avatar - Complete Guide

## Overview

Add AI-generated talking head avatars to your podcasts! The avatar's lips will sync perfectly to your generated speech, creating professional video podcasts with a human-like presenter.

---

## 🚀 Quick Start (Static Avatar for Now)

Until you set up full avatar generation, the system will create videos with a **static avatar image** and your audio:

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Generate podcast with static avatar
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --skip-music \
  -o my_first_avatar_test
```

**Result**: A video with your avatar image and synced audio (no lip movement yet).

---

## 🎨 Three Avatar Engine Options

### **Option A: Wav2Lip** (Recommended - Best Lip-Sync Quality)

**Pros**:
- ✅ Excellent lip synchronization
- ✅ GPU accelerated
- ✅ Open source and free
- ✅ Works offline

**Cons**:
- ⚠️ Complex setup (requires manual installation)
- ⚠️ Large model download (~50-100MB)
- ⚠️ Less natural head movement

**Best for**: Production-quality lip-sync when you need perfect mouth movements.

---

### **Option B: SadTalker** (Best Natural Movement)

**Pros**:
- ✅ Natural head movements and expressions
- ✅ Realistic facial animation
- ✅ GPU accelerated
- ✅ Open source and free

**Cons**:
- ⚠️ Very complex setup
- ⚠️ Large model downloads (~2GB+)
- ⚠️ Requires more GPU memory

**Best for**: When you want the most natural-looking talking head with head movements and expressions.

---

### **Option C: D-ID API** (Easiest - Commercial)

**Pros**:
- ✅ Zero setup - just API key
- ✅ Highest quality results
- ✅ Cloud-based (no GPU needed)
- ✅ Fast generation

**Cons**:
- ⚠️ Requires paid API key
- ⚠️ Costs money per generation
- ⚠️ Requires internet connection

**Best for**: Quick prototyping or when you have budget for commercial API.

---

## 📦 Installation

### Option A: Wav2Lip Setup

#### 1. Install Dependencies

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Install Wav2Lip requirements
pip install librosa==0.9.2
pip install opencv-python
pip install batch-face
```

#### 2. Clone Wav2Lip Repository

```bash
# Clone into external libs folder
mkdir -p external
cd external
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip

# Download pre-trained model
wget "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip_gan.pth" \
  -O ../../models/wav2lip_gan.pth
```

#### 3. Test Installation

```bash
cd /mnt/d/dev/AI_Podcast_Creator
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --skip-music \
  -o wav2lip_test
```

---

### Option B: SadTalker Setup

#### 1. Install SadTalker

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Install SadTalker
pip install sadtalker

# Or clone from source for latest version
cd external
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
pip install -r requirements.txt
```

#### 2. Download Models

```bash
# Models are auto-downloaded on first use (~2GB)
# Or manually download:
mkdir -p models/sadtalker
cd models/sadtalker
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.1/checkpoints.zip
unzip checkpoints.zip
```

#### 3. Update Config

Edit `config.yaml`:

```yaml
avatar:
  engine: "sadtalker"  # Changed from wav2lip
  source_image: "src/assets/avatars/default_female.jpg"
```

---

### Option C: D-ID API Setup

#### 1. Get API Key

1. Sign up at [D-ID](https://www.d-id.com/)
2. Go to API keys section
3. Generate a new API key

#### 2. Install D-ID SDK

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

pip install d-id
```

#### 3. Configure

Add to `.env`:

```bash
DID_API_KEY=your_api_key_here
```

Edit `config.yaml`:

```yaml
avatar:
  engine: "did"  # Changed from wav2lip
  did:
    api_key: ""  # Or use .env
```

---

## 🎨 Customizing Your Avatar

### Use Your Own Avatar Image

Replace the default avatar with any female (or male) face photo:

```bash
# Copy your image
cp /path/to/your/avatar.jpg src/assets/avatars/my_avatar.jpg

# Update config.yaml
avatar:
  source_image: "src/assets/avatars/my_avatar.jpg"
```

**Image Requirements**:
- Format: JPG or PNG
- Size: 512x512 or higher (will be auto-resized)
- Face: Frontal view, well-lit, clear face
- Expression: Neutral or slight smile
- Quality: High resolution for best results

**Tips for Best Results**:
- ✅ Use professional headshots
- ✅ Good lighting, no shadows on face
- ✅ Face should fill ~60-80% of frame
- ✅ Neutral background
- ❌ Avoid sunglasses, masks, or obstructions
- ❌ Avoid extreme angles or side profiles

---

## 🎬 Usage Examples

### Basic Avatar Generation

```bash
# Simple avatar video
python3 -m src.cli.main create \
  "script.txt" \
  --avatar \
  -o my_avatar_podcast
```

### Avatar + Visualization Background

```bash
# Avatar with audio-reactive background
python3 -m src.cli.main create \
  "script.txt" \
  --avatar \
  --visualize \
  -o avatar_with_viz
```

### Avatar + Background Music

```bash
# Full podcast with avatar, music, and visualization
python3 -m src.cli.main create \
  "script.txt" \
  "music.mp3" \
  --avatar \
  --visualize \
  --music-offset 20 \
  -o complete_podcast
```

### Use Different Config/Avatar

```bash
# Use custom config with different avatar
python3 -m src.cli.main create \
  "script.txt" \
  --avatar \
  --config config_male_avatar.yaml \
  -o male_podcast
```

---

## ⚙️ Configuration Options

### Wav2Lip Settings (config.yaml)

```yaml
avatar:
  engine: "wav2lip"
  source_image: "src/assets/avatars/default_female.jpg"
  wav2lip:
    model: "wav2lip_gan"  # Options: wav2lip, wav2lip_gan
    quality: "high"  # Options: high, fast
    face_detection: "blazeface"  # Face detector
```

### SadTalker Settings

```yaml
avatar:
  engine: "sadtalker"
  source_image: "src/assets/avatars/default_female.jpg"
  sadtalker:
    enhancer: "gfpgan"  # Face quality enhancer
    still_mode: false  # true = less head movement (more stable)
    expression_scale: 1.0  # 0.0-2.0 (expression intensity)
```

### D-ID Settings

```yaml
avatar:
  engine: "did"
  source_image: "src/assets/avatars/default_female.jpg"
  did:
    api_key: ""  # Your D-ID API key
```

---

## 🔧 Troubleshooting

### Issue: "Wav2Lip not installed"

**Solution**: Follow the Wav2Lip installation steps above.

### Issue: "Model not found"

**Solution**: 
```bash
cd models
wget "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip_gan.pth"
```

### Issue: "CUDA out of memory"

**Solution**:
- Use a smaller input image (512x512)
- Close other GPU applications
- Use `quality: "fast"` in config
- Try Wav2Lip instead of SadTalker (uses less memory)

### Issue: "Face not detected"

**Solution**:
- Ensure avatar image has clear, frontal face
- Face should be well-lit and unobstructed
- Try a different source image
- Check image is not corrupted

### Issue: "Lip sync quality is poor"

**Solution**:
- Use Wav2Lip engine (best lip-sync)
- Ensure audio is clear and high quality
- Use `model: "wav2lip_gan"` (better than base model)
- Try a different source image with clearer mouth

---

## 📊 Performance Comparison

| Engine | Quality | Speed | GPU Memory | Setup Difficulty |
|--------|---------|-------|------------|-----------------|
| Wav2Lip | ⭐⭐⭐⭐⭐ Lips | ⚡⚡⚡ Fast | 2-4 GB | Medium |
| SadTalker | ⭐⭐⭐⭐⭐ Overall | ⚡⚡ Slower | 4-8 GB | Hard |
| D-ID | ⭐⭐⭐⭐⭐⭐ Best | ⚡⚡⚡⚡ Cloud | 0 GB (Cloud) | Easy |

---

## 🎯 Which Engine Should I Use?

**Choose Wav2Lip if**:
- You want the best lip synchronization
- You have a mid-range GPU (4GB+ VRAM)
- You're okay with static head (less movement)
- You want good quality without huge downloads

**Choose SadTalker if**:
- You want the most natural-looking results
- You have a powerful GPU (8GB+ VRAM)
- You want head movements and expressions
- You have time for complex setup

**Choose D-ID if**:
- You want to get started immediately
- You have budget for API costs (~$0.10-0.50 per video)
- You don't have a GPU
- You want the absolute best quality

---

## 💡 Tips for Best Results

1. **Source Image Quality**: Use high-quality, professional photos
2. **Lighting**: Well-lit face with no harsh shadows
3. **Expression**: Neutral or slight smile works best
4. **Audio Quality**: Clear speech = better lip-sync
5. **GPU Memory**: Close other applications to free GPU RAM
6. **Test First**: Try short scripts (10-20 seconds) before full podcasts

---

## 🚀 Next Steps

1. **Start with Static**: Test with `--avatar` flag (uses static image for now)
2. **Choose Engine**: Decide which avatar engine fits your needs
3. **Follow Setup**: Complete installation for your chosen engine
4. **Test**: Generate a short test video
5. **Customize**: Add your own avatar images
6. **Combine**: Use with `--visualize` for complete video podcasts

---

## 📚 Related Documentation

- `VISUALIZATION_GUIDE.md` - Audio-reactive backgrounds
- `YOUR_VOICES_QUICK_START.md` - Voice options
- `GPU_OPTIMIZATION_GUIDE.md` - GPU setup and performance

---

**Your avatar feature is ready to use (static mode)! Install Wav2Lip, SadTalker, or D-ID for full lip-sync animation.**





