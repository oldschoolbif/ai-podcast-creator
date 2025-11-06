# Quick Decision Summary

**Last Updated:** 2025-11-03

## Recent Decisions (Advanced Script Format)

| # | Topic | Decision | Key Points |
|---|-------|----------|------------|
| 1 | Audio Effects | **pedalboard + pydub** | Professional effects, easy integration |
| 2 | Backward Compatibility | **New format only** | Clean codebase, alpha phase advantage |
| 3 | Timing Precision | **Configurable (C+D hybrid)** | Frame-based for video, time-based for audio |
| 4 | Pause Implementation | **Hybrid (SSML + post-process)** | Natural pauses, universal compatibility |

## Historical Decisions (65 Total)

### Most Critical Decisions:

1. **Python 3.10+** - Language choice
2. **PyTorch** - ML framework
3. **FFmpeg + MoviePy fallback** - Video processing strategy
4. **H.264 Baseline Profile** - Universal compatibility
5. **NVENC GPU encoding** - Performance optimization
6. **Multi-engine TTS support** - Flexibility
7. **gTTS as current default** - Free, unlimited, good quality
8. **Modular architecture** - Component swapping
9. **CLI-first with optional GUIs** - Automation-friendly
10. **GPU auto-detection and optimization** - Zero-config performance

### Technology Choices:

- **CLI Framework:** Typer
- **Video Encoding:** FFmpeg (NVENC) → MoviePy fallback
- **Audio Mixing:** pydub
- **Audio Effects:** pedalboard (future)
- **Web GUI:** Gradio
- **Desktop GUI:** Tkinter
- **Database:** SQLite
- **Testing:** pytest
- **Code Quality:** Black + Flake8

### Key Design Principles:

1. **Quality First** - Default to professional settings
2. **Universal Compatibility** - Works everywhere
3. **Graceful Degradation** - Fallbacks for everything
4. **Zero Configuration** - Auto-detect and optimize
5. **User Choice** - Multiple options, configurable

---

## Full Details

- **Recent Decisions:** See `01_DECISION_AUDIO_EFFECTS.md` through `04_DECISION_PAUSE_IMPLEMENTATION.md`
- **Complete History:** See `00_HISTORICAL_DECISIONS.md` (65 decisions documented)
- **Implementation Plan:** See `IMPLEMENTATION_SUMMARY.md`

