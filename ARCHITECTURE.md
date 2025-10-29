# AI Podcast Creator - System Architecture

## Project Overview

AI_Podcast_Creator is an automated video podcast generation system that converts text scripts into professional video podcasts featuring a British female AI presenter named "Vivienne Sterling" in a professional recording studio environment.

## Character Profile

**Name**: Vivienne Sterling  
**Voice**: British Female (Received Pronunciation)  
**Appearance**: Professional podcast host  
**Setting**: Modern recording studio with professional audio equipment, acoustic panels, warm lighting

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                    (Typer/Click-based)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Script Processor                           │
│   - Parse script text                                        │
│   - Extract audio cues/soundtrack descriptions               │
│   - Segment content for processing                           │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┴───────────┐
            ▼                        ▼
┌───────────────────────┐  ┌─────────────────────────┐
│   TTS Generator       │  │  Music Generator        │
│   - ElevenLabs API or │  │  - AudioCraft/MusicGen  │
│   - Coqui TTS or      │  │  - Background music     │
│   - Azure TTS         │  │  - Sound effects        │
│   - British Female    │  │                         │
└───────────┬───────────┘  └────────┬────────────────┘
            │                       │
            └───────────┬───────────┘
                        ▼
            ┌───────────────────────┐
            │   Audio Compositor    │
            │   - Mix voice + music │
            │   - Balance levels    │
            │   - FFmpeg processing │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Avatar Generator     │
            │  - Wav2Lip or         │
            │  - SadTalker or       │
            │  - D-ID API           │
            │  - Lip-sync to audio  │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Video Compositor     │
            │  - Add background     │
            │  - Overlay avatar     │
            │  - Add effects        │
            │  - FFmpeg/MoviePy     │
            └───────────┬───────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │   Output Manager      │
            │   - Save video        │
            │   - Generate metadata │
            │   - Archive assets    │
            └───────────────────────┘
```

## Core Components

### 1. CLI Interface
- **Purpose**: User interaction layer
- **Framework**: Typer (modern Python CLI)
- **Commands**:
  - `create` - Create new podcast from script
  - `list` - List all generated podcasts
  - `preview` - Preview audio before video generation
  - `config` - Configure settings (voice, background, etc.)
  - `status` - Check generation status

### 2. Script Processor
- **Purpose**: Parse and structure input
- **Features**:
  - Parse markdown/text scripts
  - Extract soundtrack markers: `[MUSIC: description]`
  - Identify segments and timing
  - Validate script format

### 3. TTS Engine
- **Purpose**: Convert text to British female speech
- **Options** (in order of recommendation):
  1. **ElevenLabs API** - Premium quality, many British voices
  2. **Azure Speech Service** - Good quality, en-GB voices
  3. **Coqui TTS** - Open source, XTTS v2 model
  4. **piper-TTS** - Fast, lightweight, offline

### 4. Music Generator
- **Purpose**: Generate background music from descriptions
- **Options**:
  1. **MusicGen** (Meta) - Text-to-music generation
  2. **AudioCraft** - Audio generation toolkit
  3. **Mubert API** - Royalty-free AI music
  4. **Pre-curated library** - Fallback option

### 5. Audio Compositor
- **Purpose**: Mix voice and music
- **Tools**:
  - **pydub** - Simple audio manipulation
  - **FFmpeg** - Professional audio processing
  - Auto-ducking (lower music when voice plays)

### 6. Avatar/Talking Head Generator
- **Purpose**: Create animated presenter
- **Options** (in order of recommendation):
  1. **SadTalker** - Open source, high quality
  2. **Wav2Lip** - Open source, accurate lip-sync
  3. **D-ID API** - Commercial, very high quality
  4. **Rhubarb Lip-Sync** - 2D animation focused
  5. **Custom with Stable Diffusion + animation**

### 7. Video Compositor
- **Purpose**: Combine all elements into final video
- **Tools**:
  - **FFmpeg** - Core video processing
  - **MoviePy** - Python video editing
  - Background image/video management
  - Overlay effects and transitions

### 8. Storage & Database
- **Purpose**: Manage scripts and outputs
- **Structure**:
  - SQLite for metadata
  - File system for media assets
  - Project organization

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (optional web interface)
- **CLI**: Typer
- **Database**: SQLite

### AI/ML Components
- **TTS**: ElevenLabs/Azure/Coqui
- **Music**: MusicGen/AudioCraft
- **Avatar**: SadTalker/Wav2Lip
- **GPU**: CUDA support recommended

### Media Processing
- **FFmpeg**: Video/audio processing
- **MoviePy**: Python video editing
- **PIL/Pillow**: Image processing
- **pydub**: Audio manipulation

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **Redis**: Job queue (for async processing)
- **Celery**: Task queue

## Data Flow

1. **Input**: User provides script via CLI
2. **Parse**: Extract main content and music cues
3. **TTS**: Generate voice audio from script
4. **Music**: Generate/select background music
5. **Audio Mix**: Combine voice + music with ducking
6. **Avatar**: Generate talking head video synced to audio
7. **Compose**: Combine avatar + background + effects
8. **Output**: Save final video + metadata

## Script Format

```markdown
# Episode Title

[MUSIC: upbeat intro, electronic, energetic]

Hello and welcome to today's episode...

[MUSIC: soft ambient background, calming]

Let me tell you about an interesting topic...

[MUSIC: crescendo, dramatic build-up]

And that's when everything changed...

[MUSIC: fade out]
```

## File Structure

```
AI_Podcast_Creator/
├── src/
│   ├── cli/
│   │   └── main.py           # CLI entry point
│   ├── core/
│   │   ├── script_parser.py  # Script processing
│   │   ├── tts_engine.py     # TTS generation
│   │   ├── music_generator.py # Music generation
│   │   ├── audio_mixer.py    # Audio composition
│   │   ├── avatar_generator.py # Avatar generation
│   │   └── video_composer.py # Video composition
│   ├── models/
│   │   └── database.py       # Data models
│   ├── utils/
│   │   ├── config.py         # Configuration
│   │   └── helpers.py        # Utility functions
│   └── assets/
│       ├── backgrounds/      # Studio backgrounds
│       ├── avatars/          # Avatar images
│       └── presets/          # Music presets
├── data/
│   ├── scripts/              # Input scripts
│   ├── outputs/              # Generated videos
│   └── cache/                # Temporary files
├── tests/
│   └── ...                   # Unit tests
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
└── config.yaml
```

## GPU Requirements

- **Minimum**: 6GB VRAM (for TTS + basic avatar)
- **Recommended**: 12GB+ VRAM (for all features)
- **CPU Fallback**: Available but slower

## Scalability Considerations

1. **Async Processing**: Use Celery for background jobs
2. **Caching**: Cache TTS outputs, music segments
3. **Batch Processing**: Support multiple scripts
4. **Cloud Ready**: Design for cloud deployment (AWS/Azure)

## Future Enhancements

1. Multiple character support
2. Multi-language support
3. Real-time preview web interface
4. Podcast platform integration (YouTube, Spotify)
5. Voice cloning capability
6. Custom avatar training
7. Scene transitions and multiple camera angles
8. Guest co-host support

