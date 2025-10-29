# 🎙️ AI Podcast Creator - START HERE

## ⭐ **QUICK START** → See `YOUR_VOICES_QUICK_START.md`

Your voices are curated and ready to use!

---

## ✅ What You Have

### **Your Selected Voices:**
- **3 gTTS Female voices** (British, American, Irish) - Natural, FREE
- **18 Coqui Male voices** - All options, FREE  
- **ElevenLabs integration** - Premium quality (10k chars/month free)

### **Voice Demos:**
- `D:\gTTSFemaleVoices\` - Your 3 female voices
- `D:\CoquiMaleVoices\` - Your 18 male voices

### **Easy Toggle:**
Just change `--config` flag to switch voices!

---

## 🚀 Create Your First Podcast

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# British female voice (default)
python3 -m src.cli.main create \
  "Creations/your_script.txt" \
  --audio-only \
  -o my_podcast

# Output: data/outputs/my_podcast.mp3
```

---

## 📋 Your Config Files

| Voice | Config File |
|-------|-------------|
| British Female (default) | `config.yaml` |
| American Female | `config_gtts_american.yaml` |
| Irish Female | `config_gtts_irish.yaml` |
| Coqui Male (18 options) | `config_male_natural.yaml` |
| ElevenLabs Adam | `config_elevenlabs_adam.yaml` |
| ElevenLabs Antoni | `config_elevenlabs_antoni.yaml` |

---

## 🎯 Features

- ✅ **Natural TTS** - gTTS female voices (very natural, free)
- ✅ **Male voices** - 18 Coqui options (free, GPU-accelerated)
- ✅ **Premium option** - ElevenLabs (human-quality)
- ✅ **Background music** - Mix audio with music tracks
- ✅ **Audio ducking** - Lower music during speech
- ✅ **Audio-only MP3** - For podcast distribution
- ✅ **Video MP4** - For YouTube/social media
- ✅ **GPU accelerated** - RTX 4060 (fast generation)
- ✅ **Cache management** - Clean up temporary files
- ✅ **Windows compatible** - H.264 baseline profile

---

## 📚 Documentation

### **Essential Guides:**
- **`YOUR_VOICES_QUICK_START.md`** ⭐ - Your curated voices (START HERE!)
- **`ELEVENLABS_SETUP.md`** - Set up premium voices (5 min)
- **`VOICE_TOGGLE_GUIDE.md`** - Switch between voice options
- **`AUDIO_ONLY_GUIDE.md`** - MP3 export for podcasts

### **Advanced:**
- **`GPU_OPTIMIZATION_GUIDE.md`** - GPU setup and tuning
- **`CACHE_MANAGEMENT.md`** - Clean up files
- **`AUDIO_VIDEO_QUICK_REF.md`** - Format comparison

### **Architecture:**
- **`ARCHITECTURE.md`** - System design
- **`REQUIREMENTS.md`** - Dependencies
- **`TOOLS_AND_LIBRARIES.md`** - Tool reference

---

## 🎬 Common Commands

### **Audio-Only MP3 (For Podcasts):**
```bash
# British female (default)
python3 -m src.cli.main create "script.txt" --audio-only -o podcast

# With music
python3 -m src.cli.main create "script.txt" "music.mp3" \
  --music-offset 20 --audio-only -o podcast

# Different voice
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_american.yaml -o podcast
```

### **Video MP4 (For YouTube):**
```bash
# Just remove --audio-only flag
python3 -m src.cli.main create "script.txt" -o podcast_video
```

### **Change Voice:**
```bash
# British female (default)
--config config.yaml

# American female
--config config_gtts_american.yaml

# Irish female
--config config_gtts_irish.yaml

# Coqui male
--config config_male_natural.yaml

# ElevenLabs (premium)
--config config_elevenlabs_adam.yaml
```

---

## 🛠️ System Status

### **✅ Installed & Configured:**
- Python 3.10 with virtual environment
- gTTS (free female voices)
- Coqui TTS (free male voices)
- ElevenLabs SDK (premium voices)
- FFmpeg with NVENC (GPU video encoding)
- MoviePy (video composition)
- Pydub (audio mixing)
- All dependencies installed

### **✅ GPU Acceleration:**
- NVIDIA RTX 4060 (8GB) detected
- CUDA 12.1 operational
- FP16 mixed precision enabled
- TF32 acceleration enabled
- NVENC hardware encoding enabled

### **✅ File Organization:**
- Scripts: `Creations/` folder
- Outputs: `data/outputs/` folder
- Cache: `data/cache/` folder (auto-managed)
- Demos: `D:\gTTSFemaleVoices\`, `D:\CoquiMaleVoices\`

---

## 💡 Tips

### **For Testing:**
Use free voices (gTTS or Coqui) - iterate until perfect

### **For Production:**
Use ElevenLabs free tier (10k chars/month) for best quality

### **For High Volume:**
Use gTTS female (unlimited, very natural)

### **When ElevenLabs Runs Out:**
Fall back to gTTS female - still excellent quality!

---

## 🎯 Next Steps

1. **Listen to your voice demos**:
   - `D:\gTTSFemaleVoices\` (3 female options)
   - `D:\CoquiMaleVoices\` (18 male options)

2. **Create your first podcast**:
   - Put script in `Creations/` folder
   - Run: `python3 -m src.cli.main create "script.txt" --audio-only -o podcast`

3. **Set up ElevenLabs** (optional):
   - See `ELEVENLABS_SETUP.md`
   - Get 10k free characters/month
   - Human-quality male voices

4. **Explore options**:
   - Try different voices
   - Add background music
   - Generate videos (remove `--audio-only`)

---

## 📞 Quick Help

### **Command not working?**
```bash
# Make sure you're in the right directory and venv is activated:
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate
```

### **Want to change Coqui voice?**
Edit `config_male_natural.yaml` and change the `speaker:` line to any of your 18 voices.

### **Need to clean up cache?**
```bash
python3 -m src.cli.main cleanup --cache-only --force
```

### **Want both audio and video?**
Generate twice - once with `--audio-only`, once without!

---

## ✅ You're Ready!

**Everything is configured, tested, and ready for production!**

→ **Start with**: `YOUR_VOICES_QUICK_START.md`

---

*Last updated: October 28, 2025*
*All test files cleaned up - production ready!*
