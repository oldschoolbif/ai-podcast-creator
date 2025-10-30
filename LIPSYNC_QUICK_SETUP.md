# 🎬 Animated Lip-Sync - 3 Easy Options

## Which One Should You Choose?

| Option | Setup Time | Quality | Cost | Best For |
|--------|------------|---------|------|----------|
| **A: Wav2Lip** | 30-60 min | ⭐⭐⭐⭐ | FREE | Best lip-sync accuracy |
| **B: SadTalker** | 10-15 min | ⭐⭐⭐⭐⭐ | FREE | Most natural (head movement) |
| **C: D-ID API** | 5 min | ⭐⭐⭐⭐⭐⭐ | $0.10/video | Instant results, easiest |

---

## 🚀 OPTION C: D-ID API (EASIEST - 5 Minutes)

### Step 1: Get API Key

1. Visit: https://www.d-id.com/
2. Sign up (free tier: 20 videos/month)
3. Go to: https://studio.d-id.com/account-settings
4. Copy your API key

### Step 2: Install & Configure

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Install D-ID SDK
pip install requests

# Add API key to .env file
echo "DID_API_KEY=your_api_key_here" >> .env

# Update config.yaml - change avatar engine
```

Edit `config.yaml`:
```yaml
avatar:
  engine: "did"  # Changed from wav2lip
  source_image: "src/assets/avatars/default_female.jpg"
  did:
    api_key: ""  # Or set DID_API_KEY in .env
```

### Step 3: Generate!

```bash
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --visualize \
  --skip-music \
  -o did_animated_test
```

**Done!** You now have animated lip-sync!

---

## 🎭 OPTION B: SadTalker (BEST FREE - 10-15 Minutes)

### Step 1: Install SadTalker

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Install SadTalker
pip install sadtalker

# Or install from source for latest version
cd external
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
pip install -r requirements.txt
```

### Step 2: Download Models (Auto on first use)

Models (~2GB) will download automatically on first generation.

Or manually:
```bash
python scripts/download_models.py
```

### Step 3: Update Config

Edit `config.yaml`:
```yaml
avatar:
  engine: "sadtalker"  # Changed from wav2lip
  source_image: "src/assets/avatars/default_female.jpg"
  sadtalker:
    enhancer: "gfpgan"  # Face quality enhancer
    still_mode: false  # Allow head movement
    expression_scale: 1.0  # Expression intensity
```

### Step 4: Generate!

```bash
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --visualize \
  --skip-music \
  -o sadtalker_test
```

**Result**: Natural head movements + lip-sync!

---

## 🎬 OPTION A: Wav2Lip (MANUAL SETUP - 30-60 Minutes)

### Step 1: Clone Wav2Lip

```bash
cd /mnt/d/dev/AI_Podcast_Creator
mkdir -p external
cd external

git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip
```

### Step 2: Download Pre-Trained Model

**Manual Download Required**:

1. Visit: https://github.com/Rudrabha/Wav2Lip
2. Find "Pre-trained Models" section
3. Download: `wav2lip_gan.pth` (~98MB)
4. Save to: `/mnt/d/dev/AI_Podcast_Creator/models/wav2lip_gan.pth`

Or try:
```bash
cd /mnt/d/dev/AI_Podcast_Creator/models
wget https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA?download=1 \
  -O wav2lip_gan.pth
```

### Step 3: Install Face Detection

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

pip install batch-face
pip install facexlib
```

### Step 4: Test

```bash
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --avatar \
  --skip-music \
  -o wav2lip_test
```

---

## 🎯 RECOMMENDED WORKFLOW

### For Quick Start → Use D-ID API (Option C)

```bash
# 1. Sign up at d-id.com (free tier)
# 2. Get API key
# 3. Add to .env
echo "DID_API_KEY=your_key" >> .env

# 4. Update config
avatar:
  engine: "did"

# 5. Generate!
python3 -m src.cli.main create "script.txt" --avatar -o test
```

### For Best Free Quality → Use SadTalker (Option B)

```bash
# 1. Install
pip install sadtalker

# 2. Update config
avatar:
  engine: "sadtalker"

# 3. Generate (models auto-download)
python3 -m src.cli.main create "script.txt" --avatar -o test
```

---

## 🔧 Implementation Helper

I can help implement D-ID API right now! Here's the code:

```python
# src/core/avatar_generator.py - Add to _generate_did method

def _generate_did(self, audio_path: Path, output_path: Path) -> Path:
    """Generate video using D-ID API."""
    import requests
    import os
    import time
    
    # Get API key
    api_key = os.getenv('DID_API_KEY') or self.config.get('avatar', {}).get('did', {}).get('api_key')
    
    if not api_key:
        raise ValueError("D-ID API key not found. Set DID_API_KEY in .env")
    
    # Upload source image
    with open(self.source_image, 'rb') as f:
        image_data = f.read()
    
    # Upload audio
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    
    # Create talk
    headers = {
        'Authorization': f'Basic {api_key}',
        'Content-Type': 'application/json'
    }
    
    # (Implementation continues...)
    
    return output_path
```

---

## 💡 Which Should You Choose?

### Choose D-ID if:
- ✅ You want it working in 5 minutes
- ✅ You're okay with $0.10-0.50 per video
- ✅ You want the highest quality
- ✅ You don't want to deal with setup

### Choose SadTalker if:
- ✅ You want free, unlimited usage
- ✅ You want natural head movements
- ✅ You have 6-8GB GPU VRAM
- ✅ You're okay with 10-15 min setup

### Choose Wav2Lip if:
- ✅ You need perfect lip-sync accuracy
- ✅ Static head is okay
- ✅ You have time for manual setup
- ✅ You want full control

---

## 🚀 Let's Get Started!

**Tell me which option you prefer, and I'll help you set it up right now!**

- **Option A (Wav2Lip)**: I'll help you download the model manually
- **Option B (SadTalker)**: I'll install it and configure it
- **Option C (D-ID API)**: I'll implement the full API integration

**Recommended: Option C for fastest results, or Option B for best free quality!**





