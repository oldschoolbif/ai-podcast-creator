# Creations Folder - Example Scripts & Templates

This folder contains sample scripts and templates to help you get started with AI Podcast Creator.

## 📝 Example Scripts

### Quick Test
- **example_short_demo.txt** - 30-second quick test (fastest way to verify installation)

### Getting Started
- **example_welcome.txt** - Welcome message showcasing the system
- **example_tech_news.txt** - News-style podcast example

### Content Types
- **example_educational.txt** - Educational content (Solar System)
- **example_storytelling.txt** - Narrative fiction (The Lost Library)
- **example_meditation.txt** - Calm meditation guide

### Templates
- **template_blank.txt** - Empty template to start your own script

## 🚀 How to Use

### Test the System:
```bash
python -m src.cli.main create Creations/example_short_demo.txt
```

### Try Different Examples:
```bash
# Welcome message
python -m src.cli.main create Creations/example_welcome.txt

# Tech news
python -m src.cli.main create Creations/example_tech_news.txt "news theme"

# Educational
python -m src.cli.main create Creations/example_educational.txt "educational background"

# Storytelling
python -m src.cli.main create Creations/example_storytelling.txt --music-file mysterious.mp3

# Meditation
python -m src.cli.main create Creations/example_meditation.txt "meditation sounds"
```

### Create Your Own:
```bash
# Copy the template
cp Creations/template_blank.txt Creations/my_podcast.txt

# Edit my_podcast.txt with your content

# Generate
python -m src.cli.main create Creations/my_podcast.txt
```

## 📋 Script Format

### Basic Structure:
```markdown
# Title

[MUSIC: description]

Your content here...

[MUSIC: different music]

More content...
```

### Music Cue Format:
```markdown
[MUSIC: upbeat intro, energetic]
[MUSIC: soft ambient background, calming]
[MUSIC: dramatic build-up]
[MUSIC: fade out]
```

## 💡 Tips

1. **Start with short_demo** - Fastest way to test (30 seconds)
2. **Use descriptive music cues** - Even if not generating AI music, helps with planning
3. **Keep paragraphs short** - Better for narration pacing
4. **Test with --preview** - Listen to audio before generating video
5. **Customize the template** - Make it your own!

## 🎯 Content Ideas

### News & Updates
- Daily news briefings
- Industry updates
- Company announcements
- Product launches

### Education
- Tutorial series
- Language lessons
- Historical facts
- Science explanations

### Entertainment
- Short stories
- Poetry readings
- Comedy scripts
- Audio dramas

### Wellness
- Meditation guides
- Affirmations
- Sleep stories
- Motivation

### Business
- Podcast intros
- Product descriptions
- Training materials
- Presentations

## 📊 Script Length Guidelines

| Length | Words | Time | Best For |
|--------|-------|------|----------|
| Short | 50-100 | 30s-1min | Tests, intros |
| Medium | 200-300 | 2-3min | News, updates |
| Long | 500-800 | 5-7min | Education, stories |
| Extended | 1000+ | 10min+ | Deep dives, series |

## 🎬 Generated Videos

After running the commands, find your videos in:
```
data/outputs/
```

Each example will create:
- MP4 video file (1920x1080)
- Named after the script file
- Ready to upload to YouTube, Spotify, etc.

## ✏️ Editing Scripts

Use any text editor:
- Notepad (Windows)
- TextEdit (Mac)
- nano/vim (Linux)
- VS Code (all platforms)

Save as `.txt` with UTF-8 encoding.

## 🔄 Iterating

1. Generate first version
2. Watch/listen to output
3. Edit script for improvements
4. Regenerate (uses cache for speed)
5. Repeat until perfect!

## 📚 More Examples

Want to contribute examples? Create your own scripts and share them!

Good examples to add:
- Product reviews
- Interview formats
- Q&A sessions
- Listicles
- How-to guides

## 🆘 Troubleshooting

### Script not found
```bash
# Make sure you're in the AI_Podcast_Creator directory
cd AI_Podcast_Creator
python -m src.cli.main create Creations/example_welcome.txt
```

### Want different output name
```bash
python -m src.cli.main create Creations/example_welcome.txt -o my_custom_name
```

### Preview before full video
```bash
python -m src.cli.main create Creations/example_welcome.txt --preview
```

---

**Happy Creating!** 🎙️✨

Your generated videos will appear in `data/outputs/`

