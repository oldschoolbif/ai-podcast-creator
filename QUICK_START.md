# Quick Start Guide - AI Podcast Creator

Get your first podcast video in 5 minutes!

## Installation (Basic Version)

### 1. Install Prerequisites

**FFmpeg** (required):
```bash
# Windows (with Chocolatey)
choco install ffmpeg

# Linux
sudo apt install ffmpeg

# Mac
brew install ffmpeg
```

**Python 3.10+**:
```bash
python --version  # Should be 3.10 or higher
```

### 2. Install Python Dependencies

```bash
cd AI_Podcast_Creator

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install basic version dependencies
pip install -r requirements-basic.txt
```

### 3. Initialize

```bash
python -m src.cli.main init
```

This creates necessary directories and database.

## Create Your First Podcast

### Example 1: Simple Script (No Music)

```bash
python -m src.cli.main create Creations/example_welcome.txt
```

Output: `data/outputs/example_welcome.mp4`

### Example 2: With Music Description

```bash
python -m src.cli.main create Creations/example_tech_news.txt "upbeat energetic electronic music"
```

### Example 3: With Your Own Music File

```bash
python -m src.cli.main create Creations/example_welcome.txt --music-file your_music.mp3
```

### Example 4: Custom Output Name

```bash
python -m src.cli.main create my_script.txt "calm ambient" -o episode_001
```

### Example 5: Preview Audio Only (No Video)

```bash
python -m src.cli.main create my_script.txt --preview
```

## Command Syntax

```bash
python -m src.cli.main create <script_file> [music_description] [options]
```

**Arguments:**
- `script_file` - Path to your text script (required)
- `music_description` - Text description of music (optional)

**Options:**
- `-o, --output` - Custom output name
- `--music-file` - Use existing music file instead of generating
- `--skip-music` - Don't include music
- `--preview` - Generate audio only (faster)

## Writing Scripts

Create a `.txt` file with your podcast content:

**Basic script:**
```
# My First Podcast

Hello and welcome to my podcast!

Today we're going to talk about something interesting.

Thank you for listening!
```

**Script with music cues:**
```
# My Podcast Episode

[MUSIC: upbeat intro, energetic]

Hello and welcome!

[MUSIC: soft ambient background]

Here's the main content...

[MUSIC: fade out]
```

## Check System Status

```bash
python -m src.cli.main status
```

Shows:
- Python version
- FFmpeg installation
- GPU availability (if any)
- Downloaded models

## Troubleshooting

### "FFmpeg not found"
Install FFmpeg (see step 1 above)

### "ModuleNotFoundError: No module named 'gtts'"
```bash
pip install -r requirements-basic.txt
```

### "Permission denied" errors
```bash
# Windows: Run as administrator
# Linux/Mac: Check folder permissions
chmod -R 755 AI_Podcast_Creator/
```

### Slow generation / No GPU
This is normal for the basic version! Uses Google TTS (cloud) and CPU-based video generation.

For faster processing:
- Install full version with GPU support
- Use cloud APIs (ElevenLabs, D-ID)

### Video won't play
Try a different media player:
- Windows: VLC Media Player
- Mac: IINA or VLC
- Linux: VLC or mpv

## What's Generated

For basic version:
- ✅ British female voice (Google TTS)
- ✅ Background music mixing (if provided)
- ✅ Simple video with gradient background
- ✅ Character name overlay
- ✅ 1920x1080 HD video

**Not included in basic version:**
- ❌ Animated talking head (requires GPU models)
- ❌ AI music generation (requires large models)
- ❌ Voice cloning (requires training)

## Customization

### Change Voice Settings

Edit `config.yaml`:
```yaml
character:
  name: "Your Character Name"
```

### Change Video Quality

Edit `config.yaml`:
```yaml
video:
  resolution: [1920, 1080]
  fps: 30
  bitrate: "8000k"
```

### Add Custom Background

1. Create a 1920x1080 JPG image
2. Place it at: `src/assets/backgrounds/studio_01.jpg`
3. Or edit path in `config.yaml`

## Next Steps

### For Better Quality:
1. Use ElevenLabs for premium TTS ($5/mo)
2. Add GPU support for faster processing
3. Install full version with avatar animation

### For Production:
1. Add custom backgrounds
2. Use professional music tracks
3. Enable watermarking
4. Add subtitles (future feature)

## Common Workflows

### Daily news podcast:
```bash
# 1. Write today's news in news_2024_10_27.txt
# 2. Generate
python -m src.cli.main create news_2024_10_27.txt "news theme music" -o news_oct_27
# 3. Upload to YouTube/podcast platform
```

### Educational series:
```bash
# Create multiple episodes
python -m src.cli.main create lesson_01.txt "educational background" -o lesson_01
python -m src.cli.main create lesson_02.txt "educational background" -o lesson_02
python -m src.cli.main create lesson_03.txt "educational background" -o lesson_03
```

### Batch processing:
```bash
# Linux/Mac script
for script in scripts/*.txt; do
    python -m src.cli.main create "$script" "ambient music"
done
```

## Getting Help

```bash
# Show all commands
python -m src.cli.main --help

# Show command help
python -m src.cli.main create --help

# Check version
python -m src.cli.main version
```

## Support

- Read [README.md](README.md) for full documentation
- Check [INSTALLATION.md](INSTALLATION.md) for detailed setup
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

**You're ready to create!** 🎙️

Start with the example scripts, then write your own content and watch it come to life!

