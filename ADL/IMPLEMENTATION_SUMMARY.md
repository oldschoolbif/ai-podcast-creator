# Implementation Summary - Advanced Script Format

**Date:** 2025-11-03  
**Status:** Ready for Implementation

---

## Decisions Made

| # | Topic | Decision | Key Points |
|---|-------|----------|------------|
| 1 | Audio Effects Library | **pedalboard + pydub hybrid** | Professional effects, easy integration |
| 2 | Backward Compatibility | **New format only** | Clean codebase, no legacy support needed |
| 3 | Timing Precision | **Configurable (C+D hybrid)** | Frame-based for video, time-based for audio, future-proof |
| 4 | Pause Implementation | **Hybrid approach** | SSML for Coqui, post-process for gTTS, quality-focused |

---

## Architecture Overview

### New Components to Create

1. **`ScriptParserAdvanced`** - Parse new script format
   - Stage directions
   - Pacing markers (`[pause Xs]`, `(beat)`)
   - Sound cues with parameters
   - Voice direction markers
   - Production notes

2. **`TimelineComposer`** - Precise audio timeline builder
   - Configurable precision (frame-based or time-based)
   - Media type detection (audio/video)
   - Future precision upgrades

3. **`PauseProcessor`** - Pause insertion
   - SSML support for Coqui
   - Post-processing for gTTS
   - Natural-sounding pauses

4. **`SoundCueProcessor`** - Complex sound cue handler
   - Fade in/out curves
   - Volume automation (+/-XdB)
   - Layered sounds
   - Precise timing

5. **`AudioProcessor`** - Professional audio effects
   - EQ (low-cut, presence boost)
   - Compression
   - Reverb
   - De-esser
   - Using `pedalboard`

6. **`EnhancedAudioMixer`** - Advanced mixing
   - Multiple music segments
   - Fade curves
   - Dynamic ducking
   - Volume automation

---

## Implementation Phases

### Phase 1: Core Parsing & Timeline (Week 1)
**Priority: High**

- [ ] Enhanced script parser (`ScriptParserAdvanced`)
- [ ] Timeline composer with configurable precision
- [ ] Character position mapping
- [ ] Basic pause insertion (post-process for gTTS)

**Estimated Time:** 3-4 days

---

### Phase 2: Pause Quality & SSML (Week 1-2)
**Priority: High**

- [ ] Optimize post-processing pauses (crossfades, character mapping)
- [ ] Add SSML support for Coqui
- [ ] Engine detection and routing
- [ ] Beat pause handling

**Estimated Time:** 2-3 days

---

### Phase 3: Sound Cues & Mixing (Week 2)
**Priority: High**

- [ ] Sound cue processor
- [ ] Fade curve implementation
- [ ] Volume automation
- [ ] Enhanced audio mixer with multiple segments

**Estimated Time:** 3-4 days

---

### Phase 4: Audio Processing (Week 2-3)
**Priority: Medium**

- [ ] Install and integrate `pedalboard`
- [ ] Audio processor with EQ, compression, reverb, de-esser
- [ ] Configuration from production notes
- [ ] Audio effects chain

**Estimated Time:** 2-3 days

---

### Phase 5: Integration & Testing (Week 3)
**Priority: High**

- [ ] Integration of all components
- [ ] End-to-end testing with test script
- [ ] Quality validation
- [ ] Performance optimization

**Estimated Time:** 2-3 days

---

## Dependencies to Add

```txt
# Add to requirements.txt
pedalboard>=0.7.0  # Professional audio effects
```

**Note:** All other dependencies already present (pydub, librosa, soundfile, scipy, numpy)

---

## Configuration Additions

Add to `config.yaml`:

```yaml
# Timeline configuration
timeline:
  precision_mode: "auto"  # auto, audio_only, video_sync, professional
  video_fps: 30
  default_beat_duration: 0.5  # seconds for (beat) markers

# Audio processing
audio_processing:
  enabled: true
  eq:
    low_cut_hz: 90
    presence_boost_hz: 4000
    presence_boost_db: 2.0
  compression:
    threshold_db: -3
    ratio: 3.0
    attack_ms: 5
    release_ms: 50
  reverb:
    room_size: 0.3
    wet_level: 0.1
  deesser:
    enabled: true
    threshold_db: -20
    frequency_hz: 6000

# TTS pause handling
tts:
  pause_processing:
    method: "hybrid"  # hybrid, ssml_only, post_process_only
    crossfade_ms: 10  # For post-processing
    use_room_tone: false  # Optional enhancement
```

---

## File Structure

```
src/core/
  ├── script_parser_advanced.py    # NEW: Advanced parser
  ├── timeline_composer.py           # NEW: Timeline builder
  ├── pause_processor.py             # NEW: Pause insertion
  ├── sound_cue_processor.py          # NEW: Sound cue handler
  ├── audio_processor.py             # NEW: Audio effects (pedalboard)
  ├── enhanced_audio_mixer.py        # NEW: Advanced mixing
  └── [existing files]

src/utils/
  └── audio_effects.py               # NEW: Audio effect utilities
```

---

## Quality Focus Areas

### 1. Natural-Sounding Pauses (gTTS)
- Accurate character-to-time mapping
- Short crossfades (5-10ms)
- Smooth pause boundaries
- Optional room tone for longer pauses

### 2. SSML Integration (Coqui)
- Proper SSML formatting
- Break timing accuracy
- Voice-appropriate pause durations

### 3. Audio Effects (pedalboard)
- Professional-grade algorithms
- Subtle processing (don't over-process)
- Preserve natural voice characteristics
- Configurable per script

### 4. Timeline Precision
- Frame-based for video (perfect sync)
- Time-based for audio (adequate precision)
- Smooth transitions between segments

---

## Testing Strategy

1. **Unit Tests**: Each component independently
2. **Integration Tests**: Full pipeline with test script
3. **Quality Tests**: Audio quality validation
4. **Performance Tests**: Timeline building speed
5. **Compatibility Tests**: Both TTS engines (gTTS, Coqui)

---

## Next Steps

1. ✅ All decisions finalized
2. ⏭️ Begin Phase 1 implementation
3. ⏭️ Create test script with all features
4. ⏭️ Iterate and refine

---

## Notes

- **TTS Priority**: gTTS currently, but architecture ready for Coqui and future premium engines
- **Quality First**: Natural-sounding voice is paramount - all implementations prioritize quality
- **Future-Proof**: Architecture allows easy upgrades (precision, engines, effects)
- **Free Tools**: All dependencies are free/open-source (pedalboard, pydub, librosa)

---

## Estimated Total Timeline

**Total Estimated Time:** 12-17 days (2.5-3.5 weeks)

**Breakdown:**
- Phase 1: 3-4 days
- Phase 2: 2-3 days
- Phase 3: 3-4 days
- Phase 4: 2-3 days
- Phase 5: 2-3 days

**Ready to begin implementation!** 🚀

