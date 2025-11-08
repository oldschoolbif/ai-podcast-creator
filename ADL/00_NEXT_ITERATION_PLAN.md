# Next Iteration Plan: Advanced Script Format Support

## Overview
Implement support for professional podcast script formats (Audacity/Descript style) with:
- Stage directions
- Pacing markers (pauses, beats)
- Complex sound cues with timing/volume
- Audio processing pipeline
- Voice direction parsing

---

## Library Recommendations

### 1. Audio Processing & Effects
**Primary Recommendation: `pedalboard`** (Spotify's audio effects library)
- **Why**: Professional-grade audio effects (EQ, compression, reverb, de-esser)
- **Pros**: 
  - GPU-accelerated where possible
  - Industry-standard algorithms
  - Python-native, easy integration
- **Installation**: `pip install pedalboard`
- **Alternatives**:
  - `librosa` + `soundfile` (already in use, good for analysis/manipulation)
  - `pydub` (already in use, good for basic mixing but limited effects)
  - `sox` via `pydub` (powerful but requires external binary)

### 2. Audio Timeline & Composition
**Recommendation: Enhance `pydub` + custom timeline builder**
- **Why**: `pydub` already handles mixing well; we just need better timing control
- **Additional**: Create `TimelineComposer` class for precise audio arrangement
- **Note**: Consider `moviepy` audio segments for complex timelines (already available)

### 3. Sound Effect Management
**Recommendation: `pygame` + audio library management**
- **Why**: Lightweight, cross-platform audio playback/testing
- **For generation**: Continue using MusicGen/other generators
- **For library**: Consider `freesound.org` API or local sound library
- **Alternative**: `pygame.mixer` for quick sound file handling

### 4. TTS Enhancement
**Current**: Coqui XTTS (already in use)
- **Enhancement Needed**: 
  - Pause insertion (post-processing or TTS API)
  - Speed/pace control (WPM targeting)
  - Tone variation support
- **No new library needed** - extend existing TTS engine

### 5. Script Parsing
**Recommendation: Regex + custom parser (built-in Python)**
- **Why**: Script format is text-based, regex sufficient
- **Enhancement**: Add state machine for nested directives
- **Consider**: `parsimonious` or `lark` if parsing gets complex

### 6. Configuration & Presets
**Recommendation: Extend existing YAML config**
- Add presets for:
  - Audio processing chains (EQ/compression/reverb)
  - Music style templates
  - Voice delivery profiles (WPM ranges, tones)

---

## Model Recommendations

### Audio Processing Models (if needed)
**Primary: Use signal processing libraries (not ML models)**
- EQ, compression, reverb are signal processing (not ML)
- **Exception**: AI de-esser might benefit from ML, but traditional DSP works well

### Music Generation
**Current**: MusicGen (already in use)
- **Enhancement**: Better prompt engineering for style matching
- **Consider**: `audiocraft` (Meta's MusicGen suite) for more control

### Sound Effects Generation
**Consider**: `AudioLDM` or `MusicGen` for sound effects
- **Alternative**: Use curated library + AI filtering/search

---

## Required New Dependencies

```python
# Add to requirements.txt:
pedalboard>=0.7.0          # Professional audio effects
soundfile>=0.12.0          # Enhanced audio I/O (already may be present)
numpy>=1.24.0              # Enhanced for audio processing (already present)
librosa>=0.10.0            # Audio analysis (check if already present)
```

**Optional (for advanced features):**
```python
parsimonious>=0.10.0       # Advanced parsing if regex becomes insufficient
pygame>=2.5.0              # Sound testing/debugging (optional)
scipy>=1.10.0              # Signal processing utilities (may already be present)
```

---

## Architecture Changes Needed

### New Components to Create:

1. **`ScriptParserAdvanced`** - Extended parser for new format
   - Parse stage directions
   - Extract pacing markers
   - Parse sound cues with parameters
   - Extract production notes

2. **`TimelineComposer`** - Precise audio timeline builder
   - Map script positions to audio timestamps
   - Insert pauses/silence
   - Schedule sound cues with timing
   - Build final audio timeline

3. **`SoundCueProcessor`** - Complex sound cue handler
   - Parse cue parameters (fade, volume, duration)
   - Generate/retrieve sound effects
   - Apply audio transformations
   - Schedule into timeline

4. **`AudioProcessor`** - Professional audio effects chain
   - EQ (parametric, low-cut, presence boost)
   - Compression (threshold, ratio, attack/release)
   - Reverb (room size, decay)
   - De-esser (frequency-specific)
   - Normalization

5. **`EnhancedAudioMixer`** - Advanced mixing
   - Multiple track support
   - Fade curves (linear/logarithmic)
   - Dynamic ducking (voice-aware)
   - Volume automation
   - Layered sounds

### Components to Enhance:

1. **`ScriptParser`** → **`ScriptParserAdvanced`**
   - Add parsing for new markers
   - Extract metadata from production notes
   - Return structured timeline data

2. **`TTSEngine`** → Add pause insertion
   - Post-process audio to insert silences
   - Or integrate pause commands into TTS generation
   - Support WPM/pace control

3. **`AudioMixer`** → **`EnhancedAudioMixer`**
   - Multiple music segments
   - Precise timing control
   - Fade curves
   - Volume automation

---

## Implementation Priority

### Phase 1: Core Parsing (High Priority)
- ✅ Enhanced script parser
- ✅ Pause insertion in TTS
- ✅ Basic sound cue extraction

### Phase 2: Timeline & Mixing (High Priority)
- ✅ Timeline composer
- ✅ Enhanced audio mixer with timing
- ✅ Basic fade in/out support

### Phase 3: Audio Processing (Medium Priority)
- Audio effects pipeline (EQ, compression, reverb)
- Advanced ducking
- Volume automation

### Phase 4: Advanced Features (Lower Priority)
- Complex layered sounds
- Dynamic music generation per cue
- Voice tone variation

---

## File Structure (New Files)

```
src/core/
  ├── script_parser_advanced.py      # New: Advanced parser
  ├── timeline_composer.py             # New: Timeline builder
  ├── sound_cue_processor.py          # New: Sound cue handler
  ├── audio_processor.py              # New: Audio effects chain
  ├── enhanced_audio_mixer.py         # New: Advanced mixing
  └── [existing files]

src/utils/
  └── audio_effects.py                # New: Audio effect utilities
```

---

## Configuration Additions

Add to `config.yaml`:

```yaml
audio_processing:
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
    damping: 0.5
    wet_level: 0.1
  deesser:
    enabled: true
    threshold_db: -20
    frequency_hz: 6000

sound_cues:
  default_fade_duration: 2.0
  default_volume_db: -12
  sound_library_path: "assets/sounds"

timeline:
  pause_beats_duration: 0.5  # Default duration for (beat) markers
```

---

## Testing Strategy

1. **Unit Tests**: Parser extraction, timeline calculations
2. **Integration Tests**: Full script → audio pipeline
3. **Audio Quality Tests**: Compare processed vs. unprocessed
4. **Timing Tests**: Verify cue placement accuracy

---

## Decision Points

### Before Implementation:

1. **Audio Effects Library**: Confirm `pedalboard` or use alternative?
2. **Pause Implementation**: Post-process or TTS-integrated?
3. **Sound Effects**: Generate with AI or use library?
4. **Timeline Precision**: Target millisecond accuracy or sub-second?
5. **Backward Compatibility**: Support old script format too?

### Questions to Answer:

1. Should we maintain backward compatibility with `[MUSIC: ...]` format?
2. What's the target timing accuracy? (e.g., ±100ms acceptable?)
3. Do we need real-time preview or is batch processing sufficient?
4. Should audio processing be optional/configurable per script?

---

## Estimated Complexity

- **Parsing Enhancements**: Medium (2-3 days)
- **Timeline Composer**: Medium-High (3-4 days)
- **Audio Processing Pipeline**: High (4-5 days)
- **Sound Cue Processor**: Medium (2-3 days)
- **Integration & Testing**: High (3-4 days)

**Total Estimate**: ~2-3 weeks for full implementation

---

## Next Steps

1. ✅ Review and approve library choices
2. ✅ Decide on backward compatibility approach
3. ✅ Confirm timing precision requirements
4. ✅ Begin Phase 1 implementation (parsing)
5. ✅ Iterate with test scripts

