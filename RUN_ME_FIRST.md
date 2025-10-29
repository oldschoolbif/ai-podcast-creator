# 🚀 RUN ME FIRST - AI Podcast Creator

## Quick Installation & First Run

### Step 1: Install FFmpeg (Required)

**Windows:**
```powershell
choco install ffmpeg
```
Or download from: https://ffmpeg.org/download.html

**Linux:**
```bash
sudo apt install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

Verify:
```bash
ffmpeg -version
```

### Step 2: Install Python Dependencies

```bash
# Make sure you're in the AI_Podcast_Creator directory
cd AI_Podcast_Creator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (basic version - no GPU needed)
pip install -r requirements-basic.txt
```

This will take a few minutes...

### Step 3: Initialize

```bash
python -m src.cli.main init
```

### Step 4: Create Your First Podcast!

```bash
python -m src.cli.main create Creations/example_welcome.txt
```

This will:
1. Convert text to British female speech (using Google TTS)
2. Create a video with gradient background
3. Add "Vivienne Sterling" title overlay
4. Save to `data/outputs/`

**Done!** 🎉

Check `data/outputs/` for your video file!

## What Just Happened?

### Basic Version Features:
- ✅ **TTS**: British female voice (Google TTS - free, cloud-based)
- ✅ **Video**: 1920x1080 HD with gradient background
- ✅ **Audio Mixing**: Voice + optional background music
- ✅ **Text Overlay**: Character name on video

### NOT Included in Basic Version:
- ❌ Animated talking head (requires GPU + large models)
- ❌ AI music generation (requires GPU + large models)
- ❌ Voice cloning

## Try More Examples

### With Music Description:
```bash
python -m src.cli.main create Creations/example_tech_news.txt "upbeat electronic music"
```

### With Your Own Music:
```bash
python -m src.cli.main create Creations/example_welcome.txt --music-file your_music.mp3
```

### Preview Audio Only (Faster):
```bash
python -m src.cli.main create Creations/example_tech_news.txt --preview
```

## Create Your Own Script

1. Create a new `.txt` file in `Creations/`:

```
# My First Podcast

Hello everyone! This is my first AI-generated podcast.

I'm excited to share this with you.

Thank you for listening!
```

2. Generate:
```bash
python -m src.cli.main create Creations/my_first.txt
```

## Command Format

```bash
python -m src.cli.main create <script> [music_description] [options]
```

**Examples:**
```bash
# Basic
python -m src.cli.main create script.txt

# With music description
python -m src.cli.main create script.txt "calm ambient music"

# With music file
python -m src.cli.main create script.txt --music-file background.mp3

# Custom output name
python -m src.cli.main create script.txt -o my_episode

# Skip music
python -m src.cli.main create script.txt --skip-music
```

## System Check

```bash
python -m src.cli.main status
```

Shows:
- ✅ Python version
- ✅ FFmpeg installation
- ⚠️ GPU (optional, for advanced features)

## Troubleshooting

### FFmpeg not found
- Make sure FFmpeg is installed
- Add FFmpeg to your system PATH
- Restart terminal after installation

### Module not found errors
```bash
# Ensure virtual environment is activated
# Then reinstall:
pip install -r requirements-basic.txt
```

### Video won't play
- Try VLC Media Player
- Update your media player

### Slow generation
- This is normal! Basic version uses cloud TTS
- Takes ~30-60 seconds for a 2-minute podcast
- For faster processing, upgrade to GPU version

## What Next?

### Read Documentation:
- [QUICK_START.md](QUICK_START.md) - Detailed quick start guide
- [README.md](README.md) - Full user manual
- [INSTALLATION.md](INSTALLATION.md) - Advanced installation

### Customize:
- Edit `config.yaml` to change settings
- Add your own background image
- Adjust video quality

### Upgrade to Full Version:
- Install GPU support (CUDA)
- Add Coqui TTS for better voices
- Enable SadTalker for animated avatars
- Use MusicGen for AI music
- See `requirements.txt` for full dependencies

## Need Help?

```bash
# Show help
python -m src.cli.main --help

# Show command help
python -m src.cli.main create --help

# Check version
python -m src.cli.main version
```

---

**Congratulations!** 🎊 

You've created your first AI podcast! Keep experimenting and creating amazing content!

For more features, check out the full documentation in README.md

