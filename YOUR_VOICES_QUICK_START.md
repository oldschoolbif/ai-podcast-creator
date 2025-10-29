# 🎙️ Your Voice Quick Start Guide

## ⭐ NEW: Audio Visualization! 🎨
Add `--visualize` flag to any command for vibrant audio-reactive backgrounds!  
See `VISUALIZATION_GUIDE.md` for details.

---

## Your Curated Voice Selection

You've tested and selected your favorite voices! Here's how to use them.

---

## 🎯 Your 3 Voice Options

### **Option 1: gTTS Female Voices** (FREE, Natural) ⭐
You kept: **British, American, Irish**

**Demos in**: `D:\gTTSFemaleVoices\`
- `demo_NEW_british.mp3` - British Female (Sophia Sterling)
- `demo_NEW_american.mp3` - American Female (Madison Taylor)
- `demo_NEW_irish.mp3` - Irish Female (Siobhan O'Connor)

---

### **Option 2: Coqui Male Voices** (FREE, All 18)
You kept: **All 18 male voices**

**Demos in**: `D:\CoquiMaleVoices\`
- All 18 voices (from Abrahan Mack to Zacharie Aimilios)

---

### **Option 3: ElevenLabs** (PREMIUM, Human Quality)
Available when you need the best: **Adam, Antoni**

**Free tier**: 10,000 chars/month (~13 short podcasts)
**Setup**: See `ELEVENLABS_SETUP.md`

---

## ⚡ Quick Commands

### Use gTTS Female (Default):
```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# British (default)
python3 -m src.cli.main create "script.txt" --audio-only -o podcast

# American
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_american.yaml -o podcast

# Irish
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_irish.yaml -o podcast
```

---

### Use Coqui Male:
```bash
# Uses speaker set in config_male_natural.yaml
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_male_natural.yaml -o podcast
```

**To change the Coqui voice**: Edit `config_male_natural.yaml` and change the `speaker:` line to any of your 18 voices.

---

### Use ElevenLabs (After Setup):
```bash
# Adam (American male, deep)
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_elevenlabs_adam.yaml -o podcast

# Antoni (British male, warm)
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_elevenlabs_antoni.yaml -o podcast
```

---

### Use Visualization (NEW! 🎨):
```bash
# Add --visualize flag for audio-reactive backgrounds
python3 -m src.cli.main create "script.txt" --visualize -o podcast
# Waveform style (blue/pink, reacts to voice)

# Different visualization styles:
python3 -m src.cli.main create "script.txt" --visualize \
  --config config_viz_spectrum.yaml -o podcast
# Frequency bars (green/yellow)

# See VISUALIZATION_GUIDE.md for all 4 styles!
```

---

### Use Talking Head Avatar (NEW! 🎭):
```bash
# Add --avatar flag for AI female face presenter
python3 -m src.cli.main create "script.txt" --avatar -o podcast
# Currently: Static avatar (image + audio sync)

# Combine avatar + visualization:
python3 -m src.cli.main create "script.txt" --avatar --visualize -o podcast
# Professional video podcast with face + reactive background!

# See AVATAR_GUIDE.md for animated lip-sync setup!
```

---

## 📋 Your Config Files

| Voice Type | Config File |
|------------|-------------|
| **British Female** | `config.yaml` or `config_gtts_british.yaml` |
| **American Female** | `config_gtts_american.yaml` |
| **Irish Female** | `config_gtts_irish.yaml` |
| **Coqui Male (any of 18)** | `config_male_natural.yaml` |
| **ElevenLabs Adam** | `config_elevenlabs_adam.yaml` |
| **ElevenLabs Antoni** | `config_elevenlabs_antoni.yaml` |

---

## 🎬 Complete Example

### Create a podcast with British female voice and music:
```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

python3 -m src.cli.main create \
  "Creations/your_script.txt" \
  "Creations/your_music.mp3" \
  --music-offset 20 \
  --audio-only \
  -o my_podcast

# Output: data/outputs/my_podcast.mp3
```

---

## 🔄 Switch Voices Anytime

Just change the `--config` flag:

```bash
# British female (default)
python3 -m src.cli.main create "script.txt" --audio-only -o podcast

# American female
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_american.yaml -o podcast

# Irish female
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_irish.yaml -o podcast

# Coqui male
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_male_natural.yaml -o podcast

# ElevenLabs (premium)
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_elevenlabs_adam.yaml -o podcast
```

---

## 📁 Your Voice Demos

**Listen anytime**:
- **Female voices**: `D:\gTTSFemaleVoices\` (3 voices)
- **Male voices**: `D:\CoquiMaleVoices\` (18 voices)

---

## 💡 Recommended Workflow

### For Free Unlimited Podcasts:
1. **Use gTTS female** for most content (very natural!)
2. **Use Coqui male** when you need a male voice

### For Premium Quality:
1. **Test with gTTS** (free)
2. **Final version with ElevenLabs** (10k chars/month free)
3. **Fall back to gTTS** when free tier runs out

---

## ✅ That's It!

**Simple toggle system** - just change `--config` to switch voices!

**Your curated voices**:
- ✅ 3 gTTS females (natural, free)
- ✅ 18 Coqui males (free, all options)
- ✅ ElevenLabs ready (premium, human quality)

**All test files cleaned up** - system is ready for production! 🎉

---

*Last updated: October 28, 2025*
*Your selected voices only - clean and ready to use!*

