# 🎛️ Voice Engine Toggle Guide - Switch Between A, B, C

## 🎯 Your Three Options

### **Option A: gTTS Female** (Free, Natural, Female Only)
- ✅ **Quality**: 9/10 - Very natural
- ✅ **Gender**: Female only
- ✅ **Cost**: FREE unlimited
- ✅ **Accents**: British, American, Australian, Irish, etc.
- ✅ **Your verdict**: "Much more natural/human"

### **Option B: Coqui Male** (Free, Okay Quality, 18 Males)
- ⚠️ **Quality**: 7/10 - "Obviously generated"
- ✅ **Gender**: 18 male voices + 15 female
- ✅ **Cost**: FREE unlimited
- ✅ **Offline**: Works without internet
- ✅ **GPU**: Accelerated on your RTX 4060

### **Option C: ElevenLabs** (Premium, Human Quality, Male & Female)
- ⭐ **Quality**: 10/10 - Truly human-sounding
- ✅ **Gender**: Multiple males & females
- ⚠️ **Cost**: 10,000 chars/month FREE (~7 min), then $5+/month
- ✅ **Speed**: Fastest generation
- ⭐ **Your solution for natural male voice!**

---

## ⚡ Quick Toggle Commands

### **Option A: gTTS Female** (Default)

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# British female (default)
python3 -m src.cli.main create "script.txt" --audio-only -o podcast

# American female
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_american.yaml -o podcast

# Australian female
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_australian.yaml -o podcast

# Irish female
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_gtts_irish.yaml -o podcast
```

---

### **Option B: Coqui Male** (Free Alternative)

```bash
# Damien Black (British, deep) - You already tested
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_male_natural.yaml -o podcast

# Try other voices - edit config_male_natural.yaml:
# Change: speaker: "Damien Black"
# To any of these:
#   - Viktor Eka (British, smooth)
#   - Torcull Diarmuid (British, mature)
#   - Dionisio Schuyler (American, clear)
#   - Royston Min (American, professional)
#   - Badr Odhiambo (British, unique)
#   ... (18 total male voices)
```

**All 18 Coqui male voices are being generated now in D:\CoquiMaleVoices\**

---

### **Option C: ElevenLabs** (Premium Natural Male)

**First-time setup** (5 minutes):
```bash
# 1. Get API key from https://elevenlabs.io
# 2. Create .env file
cp env.example .env

# 3. Edit .env and add:
# ELEVENLABS_API_KEY=sk_your_key_here
nano .env
```

**Then use**:
```bash
# Adam (American male, deep, mature)
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_elevenlabs_adam.yaml -o podcast

# Antoni (British male, warm, friendly)
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_elevenlabs_antoni.yaml -o podcast
```

---

## 📋 Config File Reference

| Voice Type | Config File | Engine | Cost |
|------------|-------------|--------|------|
| **British Female** | `config.yaml` or `config_gtts_british.yaml` | gTTS | FREE |
| **American Female** | `config_gtts_american.yaml` | gTTS | FREE |
| **Australian Female** | `config_gtts_australian.yaml` | gTTS | FREE |
| **Irish Female** | `config_gtts_irish.yaml` | gTTS | FREE |
| **Coqui Male (any)** | `config_male_natural.yaml` | Coqui | FREE |
| **ElevenLabs Adam** | `config_elevenlabs_adam.yaml` | ElevenLabs | 10k chars free |
| **ElevenLabs Antoni** | `config_elevenlabs_antoni.yaml` | ElevenLabs | 10k chars free |

---

## 🎯 Recommended Workflow

### **Strategy: Maximize Free Tier**

#### Step 1: Testing & Drafts (Use Free)
```bash
# Use gTTS female or Coqui male for testing
python3 -m src.cli.main create "draft_v1.txt" --audio-only -o test1
python3 -m src.cli.main create "draft_v2.txt" --audio-only -o test2
# Iterate until perfect
```

#### Step 2: Final Production (Use ElevenLabs)
```bash
# Once script is perfect, use ElevenLabs for final
python3 -m src.cli.main create "final.txt" --audio-only \
  --config config_elevenlabs_adam.yaml -o podcast_final
```

#### Step 3: When Free Tier Runs Out
```bash
# Fall back to gTTS female (very natural!)
python3 -m src.cli.main create "script.txt" --audio-only -o podcast
```

---

## 💰 Cost Breakdown

### **Free Forever Options**:
- **gTTS Female**: Unlimited, 9/10 quality
- **Coqui Male**: Unlimited, 7/10 quality

### **ElevenLabs Free Tier**:
- **10,000 characters/month** = ~7 minutes of audio
- **Example**:
  - 2-min podcast ≈ 300 chars → **33 podcasts/month FREE**
  - 5-min podcast ≈ 750 chars → **13 podcasts/month FREE**
  - 10-min podcast ≈ 1,500 chars → **6 podcasts/month FREE**

### **ElevenLabs Paid** (if you need more):
- **$5/month**: 30,000 chars (~20 min audio, ~40 short podcasts)
- **$22/month**: 100,000 chars (~67 min audio, ~133 short podcasts)

---

## 🎙️ Quality Comparison

### **Listen and Compare**:

**Female Voices** (gTTS - New fixed versions):
- `D:\demo_NEW_british.mp3` - British ⭐ Your favorite
- `D:\demo_NEW_american.mp3` - American
- `D:\demo_NEW_australian.mp3` - Australian
- `D:\demo_NEW_irish.mp3` - Irish

**Male Voices** (Coqui - All 18 being generated):
- `D:\CoquiMaleVoices\coqui_male_*.mp3` - 18 different males
- Listen to ALL, find your favorite!

**Premium Male** (ElevenLabs - Test after setup):
- Generate test sample with config_elevenlabs_adam.yaml
- Instantly hear the difference!

---

## 🔄 Quick Switching

### **During Development**:
```bash
# Set an alias to make it easier
alias podcast-free="python3 -m src.cli.main create"
alias podcast-premium="python3 -m src.cli.main create --config config_elevenlabs_adam.yaml"

# Then use:
podcast-free "script.txt" --audio-only -o test
podcast-premium "script.txt" --audio-only -o final
```

### **Environment Variable Toggle**:
```bash
# Add to your .bashrc or run manually:
export DEFAULT_TTS="gtts"  # or "coqui" or "elevenlabs"

# Then your app could read this (requires code modification)
```

---

## 📊 Decision Matrix

| Need | Recommendation | Config File |
|------|---------------|-------------|
| **Free female voice** | gTTS British | `config.yaml` (default) |
| **Free male voice** | Coqui (test all 18!) | `config_male_natural.yaml` |
| **Best male voice** | ElevenLabs Adam | `config_elevenlabs_adam.yaml` |
| **Testing/drafts** | gTTS or Coqui | Any free config |
| **Final production** | ElevenLabs | Any elevenlabs config |
| **High volume** | gTTS female | `config.yaml` |
| **Professional podcast** | ElevenLabs (worth $5/mo) | elevenlabs configs |

---

## 🎬 Complete Examples

### **Example 1: Test with Free, Final with Premium**
```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Test (free)
python3 -m src.cli.main create \
  "Creations/draft_script.txt" \
  "Creations/music.mp3" \
  --audio-only -o test_version

# Listen, refine script, then...

# Final (premium)
python3 -m src.cli.main create \
  "Creations/final_script.txt" \
  "Creations/music.mp3" \
  --audio-only \
  --config config_elevenlabs_adam.yaml \
  -o podcast_episode_01
```

---

### **Example 2: Series with Mixed Voices**
```bash
# Episode 1: Female narrator (free)
python3 -m src.cli.main create "ep01.txt" --audio-only -o ep01_female

# Episode 2: Male narrator (premium)
python3 -m src.cli.main create "ep02.txt" --audio-only \
  --config config_elevenlabs_adam.yaml -o ep02_male

# Episode 3: Different male (free)
python3 -m src.cli.main create "ep03.txt" --audio-only \
  --config config_male_natural.yaml -o ep03_coqui
```

---

### **Example 3: Monthly Budget Strategy**
```bash
# Use ElevenLabs for first 6-7 episodes (your free tier)
for i in {1..6}; do
  python3 -m src.cli.main create "episode_$i.txt" --audio-only \
    --config config_elevenlabs_adam.yaml -o "ep${i}_premium"
done

# Then switch to gTTS female (still natural!)
for i in {7..20}; do
  python3 -m src.cli.main create "episode_$i.txt" --audio-only \
    -o "ep${i}_free"
done
```

---

## 🛠️ Tips & Tricks

### **1. Check ElevenLabs Usage**
```bash
# Log in to elevenlabs.io
# Go to "Usage" → see characters used this month
# Plan your remaining podcasts accordingly
```

### **2. Character Count Estimation**
```bash
# Count characters in your script:
wc -c < Creations/your_script.txt

# Rule of thumb:
# - 2 min podcast ≈ 300 characters
# - 5 min podcast ≈ 750 characters
# - 10 min podcast ≈ 1,500 characters
```

### **3. Batch Generation Strategy**
```bash
# Generate all free voices first
for voice in british american australian irish; do
  python3 -m src.cli.main create "script.txt" --audio-only \
    --config config_gtts_${voice}.yaml -o "test_${voice}"
done

# Listen, pick favorite
# Then do ONE final with ElevenLabs
```

### **4. Voice Consistency**
```bash
# For a podcast series, use the SAME config for all episodes!
VOICE_CONFIG="config_elevenlabs_adam.yaml"

for ep in episode_*.txt; do
  python3 -m src.cli.main create "$ep" --audio-only \
    --config "$VOICE_CONFIG" -o "$(basename $ep .txt)"
done
```

---

## ✅ Summary

### **You Now Have**:
- ✅ **Option A**: 4 gTTS female accents (free, natural)
- ✅ **Option B**: 18 Coqui male voices (free, okay quality) - generating now
- ✅ **Option C**: ElevenLabs premium (10k chars/month free, best quality)

### **Easy Toggle**:
```bash
# Just change --config flag:
--config config.yaml                      # gTTS British female (default)
--config config_gtts_american.yaml        # gTTS American female
--config config_male_natural.yaml         # Coqui male
--config config_elevenlabs_adam.yaml      # ElevenLabs male
```

### **Recommended Path**:
1. **Test**: Use gTTS female (free, natural)
2. **Explore**: Listen to all 18 Coqui males (in D:\CoquiMaleVoices\)
3. **Setup**: Get ElevenLabs free tier (5 min setup)
4. **Decide**: Test ElevenLabs, see if worth $5/month for you
5. **Produce**: Use ElevenLabs for premium content, gTTS for high-volume

---

## 🚀 Next Steps

**Right now**:
1. ✅ ElevenLabs integration is ready
2. ⏳ Coqui male voices are being generated (D:\CoquiMaleVoices\)
3. ✅ gTTS female accents are fixed and ready

**What to do**:
1. **Listen to Coqui males** when generation completes (~10 min)
2. **Sign up for ElevenLabs** (free tier): https://elevenlabs.io
3. **Test all three options** with same script
4. **Pick your favorite** for your podcast!

---

*Last updated: October 28, 2025*
*Toggle system ready - use --config flag to switch voices!*




