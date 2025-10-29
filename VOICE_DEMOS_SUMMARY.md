# 🎙️ gTTS Voice Demos - All Accents

## ✅ 4 Demo Videos Created

All demos use the same script (`example_short_demo.txt`) so you can directly compare voices.

### 📹 Demo Files (on D:\)

| # | File | Character | Accent | Personality | Best For |
|---|------|-----------|--------|-------------|----------|
| 1️⃣ | **`demo_british_female.mp4`** ⭐ | **Sophia Sterling** | **British (UK)** | **Professional, articulate** | **Your favorite! News, formal** |
| 2️⃣ | `demo_american_female.mp4` | Madison Taylor | American (US) | Clear, neutral | Tech, tutorials, general |
| 3️⃣ | `demo_australian_female.mp4` | Olivia Brisbane | Australian | Friendly, energetic | Casual, lifestyle |
| 4️⃣ | `demo_irish_female.mp4` | Siobhan O'Connor | Irish | Warm, engaging | Storytelling, creative |

---

## 🎬 What to Do Next

### 1. Listen to All 4 Demos

Open each file in your video player and compare:
- **British** - Your original favorite (most professional)
- **American** - Most widely understood (neutral)
- **Australian** - Friendliest, most casual
- **Irish** - Most engaging for stories

### 2. Choose Your Favorite

Pick the one that fits your podcast style best!

### 3. Create Your Real Podcast

```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

# Option A: Use default (British) ⭐
python3 -m src.cli.main create \
  "Creations/your_script.txt" \
  "Creations/your_music.mp3" \
  -o my_podcast

# Option B: Specify accent
python3 -m src.cli.main create \
  "Creations/your_script.txt" \
  "Creations/your_music.mp3" \
  --config config_gtts_american.yaml \
  -o my_podcast
```

---

## 🎯 Quick Comparison

**Same script, 4 different voices:**

### 🇬🇧 British (Sophia Sterling) - Default ⭐
- **Sound**: Professional BBC broadcaster
- **Use for**: News, business, formal content
- **Your verdict**: "Much more natural/human" ✅

### 🇺🇸 American (Madison Taylor)
- **Sound**: Standard American newscaster
- **Use for**: Tech content, tutorials, general podcasts
- **Note**: Most universally understood accent

### 🇦🇺 Australian (Olivia Brisbane)
- **Sound**: Friendly, approachable
- **Use for**: Casual vlogs, lifestyle, entertainment
- **Note**: Great for relaxed, conversational content

### 🇮🇪 Irish (Siobhan O'Connor)
- **Sound**: Warm storyteller
- **Use for**: Audiobooks, creative content, narratives
- **Note**: Most engaging for story-driven content

---

## ⚡ Config Files for Each Voice

| Voice | Config File | Command Flag |
|-------|-------------|--------------|
| British ⭐ (default) | `config.yaml` or `config_gtts_british.yaml` | No flag needed or `--config config_gtts_british.yaml` |
| American | `config_gtts_american.yaml` | `--config config_gtts_american.yaml` |
| Australian | `config_gtts_australian.yaml` | `--config config_gtts_australian.yaml` |
| Irish | `config_gtts_irish.yaml` | `--config config_gtts_irish.yaml` |

---

## 📋 Complete Command Examples

### British Female (Your Favorite) ⭐
```bash
# Uses default config.yaml
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --music-offset 20 \
  -o tech_news_british
```

### American Female
```bash
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --music-offset 20 \
  --config config_gtts_american.yaml \
  -o tech_news_american
```

### Australian Female
```bash
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --music-offset 20 \
  --config config_gtts_australian.yaml \
  -o tech_news_australian
```

### Irish Female
```bash
python3 -m src.cli.main create \
  "Creations/example_tech_news.txt" \
  "Creations/skynet-sky-cassette-main-version-41446-01-52.mp3" \
  --music-offset 20 \
  --config config_gtts_irish.yaml \
  -o tech_news_irish
```

---

## 🌍 Other Available Accents

You can also use these TLD values (edit `gtts_tld` in config):

| TLD | Accent | Character Idea |
|-----|--------|----------------|
| `co.in` | Indian English | Tech tutorial voice |
| `ca` | Canadian | Similar to American |
| `co.za` | South African | International appeal |
| `co.nz` | New Zealand | Similar to Australian |

---

## 💡 Pro Tips

### Mixing Voices for Different Content Types

**Create multiple configs for different series:**

```bash
# News series → British
python3 -m src.cli.main create "news_001.txt" "news_music.mp3" --config config_gtts_british.yaml

# Tech tutorials → American
python3 -m src.cli.main create "tutorial_001.txt" "tech_music.mp3" --config config_gtts_american.yaml

# Lifestyle vlogs → Australian
python3 -m src.cli.main create "vlog_001.txt" "casual_music.mp3" --config config_gtts_australian.yaml
```

### Batch Processing Multiple Scripts

```bash
# Loop through all scripts with same voice
for script in Creations/*.txt; do
  basename=$(basename "$script" .txt)
  python3 -m src.cli.main create "$script" "music.mp3" -o "output_$basename"
done
```

---

## 🎯 Your Current Setup

✅ **Default voice**: British Female (Sophia Sterling)  
✅ **Config file**: `config.yaml`  
✅ **Available voices**: 4 pre-configured + 4 more available  
✅ **Quality**: Natural, free, fast ⭐  

**No changes needed** - your system is ready to use British female by default!

---

## 📚 Related Documentation

- **GTTS_VOICE_OPTIONS.md** - Technical details on all accents
- **GTTS_TEST_RESULTS.md** - Test results and quick commands
- **VOICE_QUALITY_OPTIONS.md** - Comparison of all TTS engines
- **VOICE_QUICK_REF.md** - Quick reference guide

---

## ✨ Summary

**4 natural female voices available**:
1. 🇬🇧 British (professional) ⭐ - Your favorite!
2. 🇺🇸 American (neutral)
3. 🇦🇺 Australian (friendly)
4. 🇮🇪 Irish (warm)

**All free, all natural, all ready to use!** 🎙️

Listen to the demos and pick your favorite. The British voice is already your default, so you're all set! 🎉

---

*Created: October 28, 2025*  
*Demo files: D:\demo_british_female.mp4, demo_american_female.mp4, demo_australian_female.mp4, demo_irish_female.mp4*




