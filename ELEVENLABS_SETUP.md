# 🚀 ElevenLabs Setup Guide - Premium Natural Voices

## ⭐ What You Get

**ElevenLabs** = Best TTS quality available
- ✅ **Truly human-sounding** voices (10/10 quality)
- ✅ **FREE tier**: 10,000 characters/month (~7 minutes of audio)
- ✅ **Multiple male & female voices**
- ✅ **Easy setup** (5 minutes)

---

## 📋 Step-by-Step Setup (5 Minutes)

### Step 1: Sign Up for Free Account

1. Go to: **https://elevenlabs.io**
2. Click "**Sign Up**" (top right)
3. Use email or Google/GitHub login
4. **Confirm your email** (check inbox)

✅ **You now have 10,000 FREE characters/month!**

---

### Step 2: Get Your API Key

1. Log in to https://elevenlabs.io
2. Click your **profile icon** (top right)
3. Go to "**Profile + API key**"
4. Click "**Create API Key**" or copy existing key
5. **Copy the key** (looks like: `sk_1234567890abcdef...`)

---

### Step 3: Add API Key to Your Project

**Option A: Environment Variable (.env file)** ⭐ Recommended

```bash
cd /mnt/d/dev/AI_Podcast_Creator

# Create .env file if it doesn't exist
cp env.example .env

# Edit .env and add your key
nano .env
```

Add this line:
```bash
ELEVENLABS_API_KEY=sk_your_actual_api_key_here
```

Save and exit (Ctrl+X, Y, Enter in nano)

---

**Option B: Directly in Config File** (Less secure)

Edit `config_elevenlabs_adam.yaml`:
```yaml
elevenlabs:
  api_key: "sk_your_actual_api_key_here"  # Replace this
```

---

### Step 4: Test It!

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Test with Adam (American male, deep)
python3 -m src.cli.main create \
  "Creations/example_short_demo.txt" \
  --skip-music \
  --audio-only \
  --config config_elevenlabs_adam.yaml \
  -o test_elevenlabs_adam
```

**Listen to**: `data/outputs/test_elevenlabs_adam.mp3`

**You'll hear the difference immediately!** 🎙️

---

## 🎙️ Available Male Voices

| Voice | Config File | Accent | Style | Best For |
|-------|-------------|--------|-------|----------|
| **Adam** ⭐ | `config_elevenlabs_adam.yaml` | American | Deep, mature | Professional content, narration |
| **Antoni** | `config_elevenlabs_antoni.yaml` | British | Warm, friendly | Podcasts, storytelling |

**More voices available** - these are just the most popular males!

---

## 💰 Pricing & Free Tier

### Free Tier (Forever Free!)
- **10,000 characters/month**
- **~7 minutes of audio**
- **All voices available**
- **No credit card required**

### Example Usage:
| Content Type | Characters | Free Tier Gets You |
|--------------|------------|-------------------|
| 30-second demo | ~100 chars | 100 demos/month |
| 2-minute podcast | ~300 chars | 33 podcasts/month |
| 10-minute podcast | ~1,500 chars | 6-7 podcasts/month |

### Paid Plans (If You Need More):
- **Starter**: $5/month - 30,000 characters
- **Creator**: $22/month - 100,000 characters
- **Pro**: $99/month - 500,000 characters

---

## ⚡ Usage Tips

### Maximize Your Free Tier:

1. **Use for final versions only**
   - Test with gTTS or Coqui (free)
   - Use ElevenLabs for final podcast

2. **Shorter scripts = more podcasts**
   - 5-minute podcast = ~750 characters
   - You get 13 podcasts/month free!

3. **Audio-only is same cost as video**
   - TTS charges by text, not output format
   - Generate audio-only to save processing time

---

## 🔄 Toggle Between Voice Engines

### Use gTTS Female (Free, Natural):
```bash
python3 -m src.cli.main create "script.txt" --audio-only -o podcast
# Uses default: gTTS British female
```

### Use Coqui Male (Free, Okay Quality):
```bash
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_male_natural.yaml -o podcast
# Uses Coqui: Damien Black
```

### Use ElevenLabs Male (Premium, Natural):
```bash
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_elevenlabs_adam.yaml -o podcast
# Uses ElevenLabs: Adam (counts against free tier)
```

---

## 📊 Quality Comparison

| Engine | Quality | Male Voice? | Free? | Speed |
|--------|---------|-------------|-------|-------|
| **gTTS** | 9/10 ⭐ | ❌ Female only | ✅ Unlimited | Fast |
| **Coqui** | 7/10 | ✅ 33 options | ✅ Unlimited | Medium |
| **ElevenLabs** | **10/10** ⭐⭐⭐ | ✅ Multiple | ⚠️ 10k chars/mo | **Fastest** |

---

## 🎯 Recommended Workflow

### For Testing & Iteration:
```bash
# Use free voices
python3 -m src.cli.main create "draft.txt" --audio-only -o test_v1
# Iterate, refine script
python3 -m src.cli.main create "draft_v2.txt" --audio-only -o test_v2
```

### For Final Professional Podcast:
```bash
# Use ElevenLabs
python3 -m src.cli.main create "final.txt" --audio-only \
  --config config_elevenlabs_adam.yaml -o podcast_ep01
```

### For High-Volume Production:
```bash
# Mix and match:
# - Intro/outro: ElevenLabs (premium quality)
# - Main content: gTTS female or Coqui (free)
# - Or upgrade to ElevenLabs paid plan
```

---

## 🔧 Troubleshooting

### Error: "API key not found"
**Solution**: Make sure `.env` file exists and has:
```bash
ELEVENLABS_API_KEY=sk_your_key_here
```

### Error: "Invalid API key"
**Solution**: 
1. Check you copied the full key
2. Go to elevenlabs.io → Profile → regenerate key
3. Update `.env` with new key

### Error: "Quota exceeded"
**Solution**: You've used your 10,000 free characters this month
- Wait until next month (resets monthly)
- OR upgrade to paid plan
- OR use gTTS/Coqui for now

### How to check usage:
1. Log in to elevenlabs.io
2. Go to "**Usage**" (left sidebar)
3. See characters used this month

---

## 🎬 Quick Commands Reference

### Test ElevenLabs (Short Demo):
```bash
cd /mnt/d/dev/AI_Podcast_Creator && source venv/bin/activate
python3 -m src.cli.main create "Creations/example_short_demo.txt" \
  --skip-music --audio-only --config config_elevenlabs_adam.yaml -o elevenlabs_test
```

### Create Full Podcast (with Music):
```bash
python3 -m src.cli.main create "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --music-offset 20 --audio-only \
  --config config_elevenlabs_adam.yaml -o tech_news_premium
```

### Different Voice:
```bash
# Antoni (British male)
python3 -m src.cli.main create "script.txt" --audio-only \
  --config config_elevenlabs_antoni.yaml -o podcast
```

---

## ✅ You're Ready!

**After setup, you have**:
- ✅ 10,000 FREE characters/month (~7 min audio)
- ✅ Premium human-quality male voices
- ✅ Easy toggle between free and premium voices
- ✅ Fallback options when free tier runs out

**Recommended**: Start with ElevenLabs free tier, see if you like it. If you need more, upgrade is only $5/month!

---

## 📚 More Voice Options

Want to see ALL ElevenLabs voices?
1. Go to: https://elevenlabs.io/voice-library
2. Browse hundreds of voices
3. Get voice ID (click voice → copy ID)
4. Add to config:
   ```yaml
   elevenlabs:
     voice_id: "your_voice_id_here"
   ```

---

*Last updated: October 28, 2025*
*Free tier: 10,000 chars/month forever*
*Premium: $5-$99/month for more*




