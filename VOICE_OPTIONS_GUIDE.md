# 🎙️ Voice Options Guide

## Available Voices

You now have **2 TTS engines** configured with multiple voice options!

---

## 1️⃣ Google TTS (gTTS) - Female Voice

**Engine**: `gtts`  
**Gender**: Female  
**Quality**: Good, natural-sounding  
**Speed**: Fast generation (~5 seconds)  
**Internet**: Required (cloud-based)  
**Cost**: Free  

### Available Accents:
- `co.uk` - British English (formal, professional)
- `com` - American English (still female!)
- `com.au` - Australian English
- `co.in` - Indian English
- `ie` - Irish English

### Configuration:
```yaml
tts:
  engine: "gtts"
  gtts_tld: "co.uk"  # British accent
```

---

## 2️⃣ pyttsx3 + espeak-ng - Male Voice ⭐

**Engine**: `pyttsx3`  
**Gender**: Male (and 108 other voices!)  
**Quality**: Robotic but clear  
**Speed**: Very fast (~3 seconds)  
**Internet**: Not required (offline)  
**Cost**: Free  

### Popular Male Voices:
| ID | Voice Name | Description | Best For |
|----|------------|-------------|----------|
| **24** | English (America) | Male, American accent | **Tech/Gaming** ⭐ |
| 23 | English (RP) | Male, British formal | Professional |
| 19 | English (GB) | Male, British | General UK content |
| 20 | English (Scotland) | Male, Scottish | Character/Fun |
| 16 | German | Male | German content |
| 52 | Japanese | Male | Anime/Japan content |

### All 108 Voices Available:
See terminal output - includes male/female voices for:
- 🌍 40+ languages
- 🗣️ Multiple accents per language
- 🎭 Character voices

### Configuration:
```yaml
tts:
  engine: "pyttsx3"
  pyttsx3_voice_id: 24  # Voice number from list
  pyttsx3_rate: 165     # Speaking speed (100-300)
```

---

## 📊 Comparison

| Feature | gTTS (Female) | pyttsx3 (Male) |
|---------|---------------|----------------|
| Gender | Female | Male ⭐ |
| Quality | Natural | Robotic |
| Speed | ~5s | ~3s |
| Internet | Required | Offline ⭐ |
| Accents | 5 variants | 108 languages ⭐ |
| Voice Control | Limited | Full control ⭐ |
| Best for | Professional | Tech/Gaming |

---

## 🎬 Your Test Videos

### Test 1: British Female (gTTS)
**File**: `D:\dean_gpu_test.mp4`
- Voice: Vivienne Sterling (gTTS 'co.uk')
- Music: Subtle (20%/50%)

### Test 2: British Female Louder (gTTS)
**File**: `D:\tech_news_louder.mp4`
- Voice: Vivienne Sterling (gTTS 'co.uk')
- Music: Loud (40%/80%)

### Test 3: FAKE Male (gTTS - Wrong!)
**File**: `D:\tech_news_male_geeky.mp4`
- Voice: Still female! (gTTS 'com')
- Note: gTTS doesn't change gender

### Test 4: REAL Male Voice ⭐
**File**: `D:\tech_news_REAL_male_voice.mp4`
- Voice: Tech Trevor (pyttsx3 Voice 24)
- **Actually male!** American accent
- Music: Loud (40%/80%), starts at 20s
- Size: 1.6 MB

---

## 🎯 How to Choose

### Use **gTTS (Female)** for:
- ✅ Professional presentations
- ✅ Educational content
- ✅ Natural-sounding voice
- ✅ When you have internet
- ✅ Quick setup (already works)

### Use **pyttsx3 (Male)** for:
- ✅ Tech/gaming content
- ✅ Male presenter needed
- ✅ Offline generation
- ✅ Faster generation
- ✅ Unique character voices
- ✅ Multi-language support

---

## 🔧 Quick Commands

### Female Voice (British):
```bash
python3 -m src.cli.main create "script.txt" \
  --music-file "music.mp3" \
  -o output_name
# Uses default config.yaml (gTTS 'co.uk')
```

### Male Voice (American - Tech Geek):
```bash
python3 -m src.cli.main create "script.txt" \
  --music-file "music.mp3" \
  --config config_male_geeky.yaml \
  -o output_name
# Uses pyttsx3 Voice 24
```

### Male Voice (British RP):
Edit `config_male_geeky.yaml`:
```yaml
tts:
  engine: "pyttsx3"
  pyttsx3_voice_id: 23  # Change to 23 for British RP
```

---

## 🎨 Customize Your Own Voice

### Step 1: List Available Voices
```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

python3 -c "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); [print(f'{i}: {v.name}') for i, v in enumerate(voices)]"
```

### Step 2: Pick a Voice Number
Find the voice you want (0-107)

### Step 3: Update Config
Edit your config file:
```yaml
tts:
  engine: "pyttsx3"
  pyttsx3_voice_id: 52  # Example: Japanese
  pyttsx3_rate: 165     # Adjust speed (100-300)
```

### Step 4: Test It
```bash
python3 -m src.cli.main create "Creations/example_short_demo.txt" \
  --skip-music \
  --config your_config.yaml \
  -o voice_test
```

---

## 🎤 Voice Quality Tips

### For Better pyttsx3 Quality:
1. **Adjust rate**: 
   - Too fast = robotic
   - Too slow = boring
   - Sweet spot: 150-170

2. **Keep sentences short**:
   - Better pronunciation
   - More natural pauses

3. **Add punctuation**:
   - Periods, commas matter!
   - Question marks change intonation

4. **Test different voices**:
   - Voice 24 (American) - best for tech
   - Voice 23 (RP) - best for professional
   - Voice 20 (Scotland) - fun character

---

## 🆚 When You Made This Discovery

**Terminal Session Evidence**:
```
✓ Using pyttsx3 voice: English (America) (Voice 24)
Audio saved to data/cache/tts/6ab155e14827b0eda35cae8a33d23f08.wav
```

**Previous (Wrong) Attempt**:
```
✅ Speech generated: data/cache/tts/34e6460442eddc145718d432db966844.mp3
(Used cached female voice!)
```

**Lesson Learned**: 
- gTTS doesn't have male voices (all accents are female)
- Cache can mask voice changes (clear when testing!)
- pyttsx3 + espeak-ng = real voice control

---

## 📦 Requirements

### For gTTS (Female):
```bash
pip install gTTS  # Already installed
```

### For pyttsx3 (Male):
```bash
# Python package (already installed)
pip install pyttsx3

# System dependency (now installed!)
sudo apt install -y espeak-ng
```

---

## 🎯 Recommended Configs

We created 3 configs for you:

1. **`config.yaml`** - Default
   - British female (gTTS)
   - Subtle music
   - Professional

2. **`config_louder_music.yaml`**
   - British female (gTTS)
   - Loud music
   - Energetic

3. **`config_male_geeky.yaml`** ⭐
   - American male (pyttsx3)
   - Loud music
   - Tech/gaming focused

---

## 🎬 Final Result

**Open and compare**:
1. `D:\dean_gpu_test.mp4` - Female, subtle
2. `D:\tech_news_louder.mp4` - Female, loud
3. `D:\tech_news_REAL_male_voice.mp4` - **Male, loud, music offset** ⭐

**The last one is the real male voice!** 🎙️

---

*Voice options fully documented and working!*  
*Created: October 28, 2025*




