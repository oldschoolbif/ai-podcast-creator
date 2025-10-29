# 🎙️ gTTS Voice Options Guide

## What is gTTS?

Google Text-to-Speech (gTTS) uses Google's TTS API - the same voices you hear in Google Translate.

**Pros**:
- ✅ Very natural sounding
- ✅ Completely free (no API key needed)
- ✅ Fast generation
- ✅ Reliable (Google infrastructure)
- ✅ Multiple accents available

**Cons**:
- ⚠️ Only female voice
- ⚠️ Requires internet connection
- ⚠️ Limited control over speed/pitch

---

## Available Accents

gTTS uses the `tld` (top-level domain) parameter to control accent:

| TLD | Accent | Character | Sample |
|-----|--------|-----------|--------|
| **co.uk** | **British (UK)** ⭐ | **Professional, clear** | **Default (Sophia)** |
| com | American (US) | Neutral, standard | General purpose |
| com.au | Australian | Friendly, casual | Casual content |
| co.in | Indian | Clear, formal | Tech tutorials |
| ca | Canadian | Similar to US | North American |
| co.za | South African | Unique, clear | International |
| ie | Irish | Soft, warm | Storytelling |
| co.nz | New Zealand | Similar to AU | Casual content |

---

## Configuration

### British (UK) - Your Original Voice ⭐

**File**: `config.yaml` (default)

```yaml
character:
  name: "Sophia Sterling"
  voice_type: "British Female"
  accent: "Received Pronunciation (RP)"
  personality: "Professional, articulate, trustworthy"

tts:
  engine: "gtts"
  
  gtts_tld: "co.uk"  # British accent
```

**Best for**: Professional content, news, formal podcasts

---

### American (US)

**File**: `config_gtts_american.yaml`

```yaml
character:
  name: "Madison Taylor"
  voice_type: "American Female"
  accent: "General American"
  personality: "Clear, neutral, professional"

tts:
  engine: "gtts"
  gtts_tld: "com"  # American accent
```

**Best for**: Tech content, tutorials, general podcasts

---

### Australian

**File**: `config_gtts_australian.yaml`

```yaml
character:
  name: "Olivia Brisbane"
  voice_type: "Australian Female"
  accent: "Australian"
  personality: "Friendly, approachable, energetic"

tts:
  engine: "gtts"
  gtts_tld: "com.au"  # Australian accent
```

**Best for**: Casual content, lifestyle, entertainment

---

### Indian

**File**: `config_gtts_indian.yaml`

```yaml
character:
  name: "Priya Sharma"
  voice_type: "Indian Female"
  accent: "Indian English"
  personality: "Clear, articulate, knowledgeable"

tts:
  engine: "gtts"
  gtts_tld: "co.in"  # Indian accent
```

**Best for**: Tech tutorials, educational content, IT topics

---

### Irish

**File**: `config_gtts_irish.yaml`

```yaml
character:
  name: "Siobhan O'Connor"
  voice_type: "Irish Female"
  accent: "Irish"
  personality: "Warm, engaging, storyteller"

tts:
  engine: "gtts"
  gtts_tld: "ie"  # Irish accent
```

**Best for**: Storytelling, audiobooks, creative content

---

## How to Switch Back to British Female

### Option 1: Use Default Config (Already Set)

```bash
python3 -m src.cli.main create "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --music-offset 20 \
  -o my_podcast
```

This uses `config.yaml` which is already set to British female!

---

### Option 2: Explicitly Specify Config

```bash
python3 -m src.cli.main create "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --music-offset 20 \
  --config config.yaml \
  -o my_podcast
```

---

## Quick Comparison Test

Want to hear all the accents? Run this:

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# British (your favorite)
python3 -m src.cli.main create "Creations/example_short_demo.txt" --skip-music --config config_gtts_british.yaml -o test_british

# American
python3 -m src.cli.main create "Creations/example_short_demo.txt" --skip-music --config config_gtts_american.yaml -o test_american

# Australian
python3 -m src.cli.main create "Creations/example_short_demo.txt" --skip-music --config config_gtts_australian.yaml -o test_australian

# Indian
python3 -m src.cli.main create "Creations/example_short_demo.txt" --skip-music --config config_gtts_indian.yaml -o test_indian

# Irish
python3 -m src.cli.main create "Creations/example_short_demo.txt" --skip-music --config config_gtts_irish.yaml -o test_irish
```

---

## Technical Details

### How gTTS Works

```python
from gtts import gTTS

# British accent
tts = gTTS(text="Hello world", lang='en', tld='co.uk')

# American accent
tts = gTTS(text="Hello world", lang='en', tld='com')
```

The `tld` parameter tells Google which regional TTS model to use.

---

## Limitations

**What gTTS CAN'T do**:
- ❌ Male voices (only female)
- ❌ Control speaking speed
- ❌ Control pitch/tone
- ❌ Offline generation (needs internet)
- ❌ Voice cloning
- ❌ Multiple speakers in one script

**What gTTS CAN do**:
- ✅ Natural-sounding female speech
- ✅ Multiple accents/regions
- ✅ Free and unlimited
- ✅ Fast generation
- ✅ Very reliable

---

## Recommendations

### Best gTTS Accents by Use Case:

**Professional Content** (news, business):
- ⭐ **British (co.uk)** - Most professional
- ✅ American (com) - Neutral, clear

**Tech/Tutorial Content**:
- ⭐ **American (com)** - Standard for tech
- ✅ Indian (co.in) - Great for tech tutorials

**Casual/Lifestyle Content**:
- ⭐ **Australian (com.au)** - Friendly, approachable
- ✅ Irish (ie) - Warm, engaging

**International Audience**:
- ⭐ **American (com)** - Most universally understood
- ✅ British (co.uk) - Professional, international

---

## Pro Tip: Mixing Accents

You can use different accents for different content types!

**Example workflow**:
```bash
# Professional news → British
python3 -m src.cli.main create "news.txt" "music.mp3" --config config_gtts_british.yaml

# Tech tutorial → American
python3 -m src.cli.main create "tutorial.txt" "music.mp3" --config config_gtts_american.yaml

# Casual vlog → Australian  
python3 -m src.cli.main create "vlog.txt" "music.mp3" --config config_gtts_australian.yaml
```

---

## Bottom Line

**Your instinct was right!** The gTTS British female voice (your "first voice") is actually:
- ✅ More natural than free Coqui
- ✅ More natural than pyttsx3
- ✅ Completely free
- ✅ Zero setup required
- ✅ Very reliable

**The only limitation**: Female voice only.

If you ever need a male voice that sounds as natural as gTTS female, you'll need **ElevenLabs** (premium). But for female voices, **gTTS is your best free option**! 🎯

---

*Created: October 28, 2025*  
*Current config already uses British female (co.uk)*




