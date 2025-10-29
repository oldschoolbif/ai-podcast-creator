# 🎬 Audio & Video Quick Reference

## 📁 Your Demo Files (D:\)

### 🎵 Audio-Only (MP3) - NEW! ⭐
Perfect for podcasts, portability, smaller files
- `demo_british_female.mp3` (153KB) - Sophia Sterling 🇬🇧
- `demo_american_female.mp3` (153KB) - Madison Taylor 🇺🇸
- `demo_australian_female.mp3` (153KB) - Olivia Brisbane 🇦🇺
- `demo_irish_female.mp3` (153KB) - Siobhan O'Connor 🇮🇪

### 📹 Video (MP4) - Windows Compatible
For YouTube, social media, visual content
- `demo_british_female_compatible.mp4` (255KB) - Sophia Sterling 🇬🇧
- `demo_american_female_compatible.mp4` (252KB) - Madison Taylor 🇺🇸
- `demo_australian_female_compatible.mp4` (249KB) - Olivia Brisbane 🇦🇺
- `demo_irish_female_compatible.mp4` (250KB) - Siobhan O'Connor 🇮🇪

---

## ⚡ Quick Commands

### Generate Audio-Only MP3:
```bash
cd /mnt/d/dev/AI_Podcast_Creator && source venv/bin/activate

# British (default)
python3 -m src.cli.main create "script.txt" --audio-only -o podcast

# American
python3 -m src.cli.main create "script.txt" --audio-only --config config_gtts_american.yaml -o podcast

# With music
python3 -m src.cli.main create "script.txt" "music.mp3" --audio-only -o podcast
```

### Generate Video MP4:
```bash
# British (default)
python3 -m src.cli.main create "script.txt" -o podcast

# American
python3 -m src.cli.main create "script.txt" --config config_gtts_american.yaml -o podcast

# With music
python3 -m src.cli.main create "script.txt" "music.mp3" -o podcast
```

---

## 🎯 When to Use Each Format

| Use Case | Format | Command Flag |
|----------|--------|--------------|
| **Podcast platforms** (Spotify, Apple Podcasts) | MP3 | `--audio-only` |
| **YouTube, TikTok, Instagram** | MP4 | (no flag) |
| **Quick voice testing** | MP3 | `--audio-only --skip-music` |
| **Import to video editor** | MP3 | `--audio-only` |
| **Website background audio** | MP3 | `--audio-only` |
| **Social media visual posts** | MP4 | (no flag) |
| **E-learning, presentations** | Both | Generate both! |

---

## 📊 Format Comparison

| Feature | MP3 (Audio-Only) | MP4 (Video) |
|---------|------------------|-------------|
| **File Size** | ~1.2 MB/min | ~2.2 MB/min |
| **Generation Speed** | Faster (40% less) | Slower (video encoding) |
| **Quality** | VBR ~190 kbps | Same audio + video |
| **Compatibility** | All audio players | All video players |
| **Portability** | Excellent (small) | Good (larger) |
| **Use for podcasts** | ✅ Perfect | ⚠️ Overkill |
| **Use for social media** | ⚠️ Limited | ✅ Perfect |
| **Edit in DAW/Audacity** | ✅ Perfect | ⚠️ Extract first |

---

## 💡 Pro Workflow

### For Podcast Distribution:
1. Generate audio-only MP3
2. Upload to Spotify, Apple Podcasts, etc.
3. Done! (No video needed)

### For YouTube + Podcasts:
1. Generate audio-only MP3 → upload to podcast platforms
2. Generate video MP4 (same script) → upload to YouTube
3. Best of both worlds!

### For Quick Iteration:
1. Test with audio-only (fast!)
2. Listen, refine script
3. Final version: generate both formats

---

## 🎵 MP3 Specifications
- **Codec**: LAME MP3 (libmp3lame)
- **Quality**: VBR Q2 (~190 kbps)
- **Sample Rate**: 44.1 kHz
- **Channels**: Stereo
- **Metadata**: ID3v2.3 tags included
- **Size**: ~40% smaller than video

## 📹 MP4 Specifications
- **Video Codec**: H.264 Baseline
- **Audio Codec**: AAC 192 kbps
- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 fps
- **Compatibility**: Universal (Windows, Mac, mobile, web)

---

## 📚 Full Documentation

- **AUDIO_ONLY_GUIDE.md** - Complete audio-only reference
- **VIDEO_COMPATIBILITY_FIXED.md** - Video codec details
- **VOICE_DEMOS_SUMMARY.md** - All voice options
- **GTTS_VOICE_OPTIONS.md** - Voice accent guide

---

## ✅ You're All Set!

**8 demo files ready** (4 audio + 4 video)  
**4 voice accents** (British, American, Australian, Irish)  
**2 output formats** (MP3 audio-only, MP4 video)  
**100% Windows compatible** ✅

Pick your format, pick your voice, create your content! 🎙️🎬

---

*Created: October 28, 2025*




