# Decision 3: Timing Precision for Audio Timeline

**Date:** 2025-11-03  
**Status:** Decided  
**Decider:** Development Team  
**Decision Date:** 2025-11-03

---

## Context

We need to build a precise audio timeline that synchronizes:
- TTS-generated speech
- Pause markers (`[pause Xs]`, `(beat)`)
- Sound cues with timing (`fade in 2s → underlay for 5s`)
- Multiple music segments (intro, underscore, emotional lift, outro)
- Volume automation (fade curves, dB adjustments)

**Critical question:** What level of timing precision do we need, and how do we achieve it?

---

## Requirements

1. **Synchronization**: Sound cues must align with script positions
2. **Accuracy**: Fade timings (e.g., "fade in 2s") should be precise
3. **TTS Integration**: Map script character positions to audio timestamps
4. **Performance**: Timeline building should be fast
5. **Flexibility**: Support various timing specifications (seconds, milliseconds, beats)

---

## Options Considered

### Option A: Millisecond Precision (High Accuracy)

**Description:**
- Target: ±10ms accuracy for all timing operations
- Use precise sample-accurate positioning
- Calculate timestamps based on exact sample positions
- Store timing as milliseconds or samples

**Implementation:**
```python
class TimelineComposer:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.millisecond_precision = True
    
    def add_pause(self, duration_ms: float):
        # Convert to exact sample count
        samples = int(duration_ms * self.sample_rate / 1000)
        # Exact sample accuracy
        ...
    
    def position_sound_cue(self, script_position: int, audio_timeline: list):
        # Map character position to exact timestamp in milliseconds
        timestamp_ms = self._calculate_exact_timestamp(script_position)
        # Position with millisecond accuracy
        ...
```

**Pros:**
- ✅ **Highest accuracy**: Professional-grade precision
- ✅ **Sample-accurate**: Can align to exact audio samples
- ✅ **Flexible**: Supports any timing specification
- ✅ **Professional**: Meets broadcast standards
- ✅ **No drift**: Exact positioning prevents timing drift

**Cons:**
- ❌ **Complexity**: More complex calculations
- ❌ **Overkill**: May be unnecessary for podcast use case
- ❌ **Processing overhead**: More computation for precision

**Implementation Complexity:** Medium-High  
**Time Estimate:** 3-4 days (timeline builder + TTS mapping + testing)

---

### Option B: Sub-second Precision (100ms accuracy)

**Description:**
- Target: ±100ms accuracy (0.1 seconds)
- Round timing to nearest 100ms
- Use frame-based positioning (at 30fps, ~33ms per frame)
- Simpler calculations, good enough for human perception

**Implementation:**
```python
class TimelineComposer:
    def __init__(self, precision_ms: int = 100):
        self.precision_ms = precision_ms
    
    def add_pause(self, duration_s: float):
        # Round to nearest 100ms
        rounded_ms = round(duration_s * 1000 / self.precision_ms) * self.precision_ms
        ...
    
    def position_sound_cue(self, script_position: int):
        # Round timestamp to 100ms precision
        timestamp_ms = round(self._calculate_timestamp(script_position) / 100) * 100
        ...
```

**Pros:**
- ✅ **Simpler implementation**: Less complex calculations
- ✅ **Fast**: Quick timeline building
- ✅ **Good enough**: Human ear can't distinguish <100ms differences
- ✅ **Sufficient**: Adequate for podcast/voice content
- ✅ **Easier testing**: Less precision = easier to validate

**Cons:**
- ❌ **Lower precision**: May cause slight misalignment
- ❌ **Rounding errors**: Can accumulate over long timelines
- ❌ **Less professional**: Doesn't meet strict broadcast standards

**Implementation Complexity:** Low-Medium  
**Time Estimate:** 2-3 days (simpler timeline builder)

---

### Option C: Hybrid Approach (Variable Precision)

**Description:**
- Use sub-second (100ms) for most operations
- Use millisecond precision for critical timing (fades, exact cue placement)
- Configurable precision per operation type
- Smart precision selection based on operation

**Implementation:**
```python
class TimelineComposer:
    def __init__(self):
        self.default_precision = 100  # 100ms for general use
        self.critical_precision = 10  # 10ms for fades/cues
    
    def add_pause(self, duration_s: float):
        # Sub-second precision is fine for pauses
        return self._round_to_precision(duration_s, self.default_precision)
    
    def add_fade(self, duration_s: float):
        # Millisecond precision for fades
        return self._round_to_precision(duration_s, self.critical_precision)
    
    def position_sound_cue(self, script_position: int):
        # Critical: needs precision for alignment
        return self._round_to_precision(
            self._calculate_timestamp(script_position),
            self.critical_precision
        )
```

**Pros:**
- ✅ **Balanced**: Right precision for each operation
- ✅ **Performance**: Fast where precision isn't critical
- ✅ **Accuracy**: Precise where it matters
- ✅ **Flexible**: Can adjust precision per use case

**Cons:**
- ❌ **Complexity**: Two precision levels to manage
- ❌ **Decision logic**: Need to decide which operations need precision

**Implementation Complexity:** Medium  
**Time Estimate:** 3-4 days (timeline builder + precision logic)

---

### Option D: Frame-based Precision (Video-aligned)

**Description:**
- Align to video frame boundaries (30fps = ~33ms)
- Audio timing matches video frame timing
- Useful for video sync, simpler mental model
- Round to nearest frame boundary

**Implementation:**
```python
class TimelineComposer:
    def __init__(self, video_fps: int = 30):
        self.video_fps = video_fps
        self.frame_duration_ms = 1000 / video_fps  # ~33.33ms per frame
    
    def align_to_frame(self, timestamp_ms: float):
        # Round to nearest video frame
        frames = round(timestamp_ms / self.frame_duration_ms)
        return frames * self.frame_duration_ms
```

**Pros:**
- ✅ **Video sync**: Perfect alignment with video frames
- ✅ **Simple model**: Easy to understand (frames, not milliseconds)
- ✅ **Good precision**: 33ms is more than adequate for audio
- ✅ **Natural fit**: Works well for video podcast use case

**Cons:**
- ❌ **Less flexible**: Tied to video frame rate
- ❌ **Audio-only limitation**: Not ideal if audio-only output needed
- ❌ **Frame rate dependency**: Changes with video FPS

**Implementation Complexity:** Low  
**Time Estimate:** 2-3 days (frame-aligned timeline)

---

## Decision Criteria

Rate each option (1-5 scale) on:

### 1. Accuracy Requirements
- **Option A (Millisecond)**: ⭐⭐⭐⭐⭐ (Highest precision)
- **Option B (Sub-second)**: ⭐⭐⭐ (Adequate for human perception)
- **Option C (Hybrid)**: ⭐⭐⭐⭐ (Balanced precision)
- **Option D (Frame-based)**: ⭐⭐⭐⭐ (Good for video sync)

### 2. Implementation Complexity
- **Option A**: ⭐⭐ (Most complex)
- **Option B**: ⭐⭐⭐⭐⭐ (Simplest)
- **Option C**: ⭐⭐⭐ (Moderate complexity)
- **Option D**: ⭐⭐⭐⭐ (Simple, frame-aligned)

### 3. Performance
- **Option A**: ⭐⭐⭐ (More computation)
- **Option B**: ⭐⭐⭐⭐⭐ (Fastest)
- **Option C**: ⭐⭐⭐⭐ (Fast where it matters)
- **Option D**: ⭐⭐⭐⭐ (Fast, frame calculations)

### 4. Use Case Fit
- **Option A**: ⭐⭐⭐ (Overkill for podcasts?)
- **Option B**: ⭐⭐⭐⭐⭐ (Perfect for podcasts)
- **Option C**: ⭐⭐⭐⭐ (Good balance)
- **Option D**: ⭐⭐⭐⭐⭐ (Perfect if video-focused)

### 5. Maintainability
- **Option A**: ⭐⭐⭐ (Complex code)
- **Option B**: ⭐⭐⭐⭐⭐ (Simple to maintain)
- **Option C**: ⭐⭐⭐ (Two systems to maintain)
- **Option D**: ⭐⭐⭐⭐ (Simple frame logic)

### 6. Future Flexibility
- **Option A**: ⭐⭐⭐⭐⭐ (Supports any use case)
- **Option B**: ⭐⭐⭐⭐ (May need upgrade later)
- **Option C**: ⭐⭐⭐⭐ (Flexible)
- **Option D**: ⭐⭐⭐ (Tied to video frames)

---

## Scoring Matrix

| Criterion | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Accuracy | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Complexity | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Performance | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Use Case Fit | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Maintainability | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Flexibility | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Total** | **21/30** | **27/30** | **23/30** | **24/30** |

---

## Questions to Consider

### 1. Primary Use Case
**Q:** Is this primarily for video podcasts or audio-only?
- **Video podcasts**: → Option D (frame-aligned) or Option C
- **Audio-only**: → Option B or Option C
- **Both**: → Option C (flexible)

### 2. Timing Accuracy Needs
**Q:** Do you need professional broadcast-level precision?
- **Yes (broadcast)**: → Option A
- **No (podcast/streaming)**: → Option B or C
- **Maybe later**: → Option C (start flexible)

### 3. Performance Requirements
**Q:** Is timeline building speed critical?
- **Yes, very fast**: → Option B
- **Moderate speed OK**: → Option C or D
- **Precision > speed**: → Option A

### 4. Video Integration
**Q:** Will timing need to sync with video frames?
- **Yes, critical**: → Option D
- **Yes, but flexible**: → Option C
- **No/Maybe**: → Option B or C

### 5. Future Expansion
**Q:** Might you need higher precision later (e.g., music production)?
- **Yes, likely**: → Option A or C
- **Unlikely**: → Option B or D
- **Unknown**: → Option C (start flexible)

---

## Real-World Examples

### Audacity/Descript:
- **Precision**: ~100ms (sub-second)
- **Why**: Good enough for human perception
- **Result**: Fast, reliable timeline building

### Pro Tools/Logic:
- **Precision**: Sample-accurate (millisecond/sub-millisecond)
- **Why**: Professional music production
- **Result**: More complex but highest quality

### Video Editors (Premiere/Final Cut):
- **Precision**: Frame-accurate (~33ms at 30fps)
- **Why**: Sync with video
- **Result**: Perfect audio-video alignment

---

## My Recommendation

**Option B: Sub-second Precision (100ms accuracy)**

**Rationale:**
1. ✅ **Perfect for podcasts**: Human ear can't distinguish <100ms differences
2. ✅ **Simplest implementation**: Faster development, easier maintenance
3. ✅ **Best performance**: Fast timeline building
4. ✅ **Adequate accuracy**: More than enough for voice + music mixing
5. ✅ **Future-proof**: Can upgrade to higher precision later if needed

**Alternative if video sync is critical:**
- **Option D: Frame-based** - if perfect video sync is required

**Accepted Trade-offs:**
- Not sample-accurate (acceptable for podcast use)
- Rounding to 100ms (imperceptible to humans)
- May need upgrade later (but simple to do)

**Rejected Options:**
- **Option A**: Overkill for podcasts, adds unnecessary complexity
- **Option C**: Adds complexity without clear benefit for podcast use case

---

## Implementation Notes

If choosing Option B:

### Timeline Structure
```python
class TimelineComposer:
    def __init__(self, precision_ms: int = 100):
        self.precision_ms = precision_ms  # 100ms default
        self.timeline = []  # List of timeline events
    
    def _round_to_precision(self, milliseconds: float) -> float:
        """Round to nearest precision (100ms default)"""
        return round(milliseconds / self.precision_ms) * self.precision_ms
    
    def add_speech(self, text: str, start_time: float):
        # Calculate from TTS duration
        duration = self._estimate_speech_duration(text)
        # Round to precision
        rounded_start = self._round_to_precision(start_time * 1000) / 1000
        ...
    
    def add_pause(self, duration_s: float):
        # Round pause duration
        rounded = self._round_to_precision(duration_s * 1000) / 1000
        self.timeline.append({
            'type': 'pause',
            'duration': rounded,
            'start_time': self._get_current_time()
        })
```

### TTS to Timeline Mapping
```python
def map_script_to_audio(self, script_text: str, tts_audio: AudioSegment):
    """Map script character positions to audio timestamps"""
    # Estimate character-to-time mapping
    # Account for TTS pauses, rate variations
    # Round timestamps to 100ms precision
    ...
```

---

## Consequences

**Positive:**
- ✅ Simple, fast implementation
- ✅ More than accurate enough for podcasts
- ✅ Easy to test and validate
- ✅ Good performance

**Negative:**
- ❌ Not sample-accurate (acceptable trade-off)
- ❌ May need upgrade if requirements change

**Mitigation:**
- Design timeline structure to allow precision upgrade later
- Use configurable precision (can change from 100ms to 10ms if needed)
- Document precision in code for future reference

---

## Follow-up Decisions

Decisions that depend on this:
- [ ] Decision 4: Pause Implementation (TTS-integrated vs post-process)
- [ ] Timeline data structure design
- [ ] Sound cue positioning algorithm

---

## Review Date

**Next Review:** 2025-05-03 (6 months, assess if precision needs increase)

---

## Decision

**Selected Option:** Option C + D Hybrid: Configurable Precision with Use-Case Selection

**Rationale:**
- ✅ **Flexible**: Select precision based on media type (audio-only vs video)
- ✅ **Future-proof**: Architecture allows upgrading to higher precision
- ✅ **Smart defaults**: Frame-based for video (30fps = ~33ms), sub-second for audio
- ✅ **Extensible**: Easy to add millisecond precision later if needed
- ✅ **Free tools**: Uses existing libraries (pydub, librosa) - no cost
- ✅ **Best of both**: Right precision for each use case

**Accepted Trade-offs:**
- More complex implementation (but worth it for flexibility)
- Need precision selection logic
- Configurable system requires documentation

---

## Implementation Strategy

### Architecture Design

```python
class TimelineComposer:
    """Configurable precision timeline builder"""
    
    # Precision presets
    PRECISION_PRESETS = {
        'audio_only': 100,      # 100ms - good for audio podcasts
        'video_sync': 33.33,    # Frame-based at 30fps
        'video_60fps': 16.67,   # Frame-based at 60fps
        'professional': 10,     # 10ms - broadcast quality
        'sample_accurate': 0.023  # ~1 sample at 44.1kHz
    }
    
    def __init__(self, 
                 media_type: str = 'video',  # 'audio' or 'video'
                 precision_mode: str = 'auto',  # 'auto' or specific preset
                 video_fps: int = 30,
                 sample_rate: int = 44100):
        """
        Initialize with configurable precision.
        
        Args:
            media_type: 'audio' or 'video' - determines default precision
            precision_mode: 'auto' (smart default) or preset name
            video_fps: Frame rate for video sync (default: 30)
            sample_rate: Audio sample rate (default: 44100)
        """
        self.media_type = media_type
        self.video_fps = video_fps
        self.sample_rate = sample_rate
        
        # Select precision
        if precision_mode == 'auto':
            if media_type == 'video':
                # Frame-based precision
                self.precision_ms = 1000 / video_fps
                self.precision_type = 'frame_based'
            else:
                # Audio-only: sub-second precision
                self.precision_ms = self.PRECISION_PRESETS['audio_only']
                self.precision_type = 'time_based'
        else:
            # Use specific preset
            self.precision_ms = self.PRECISION_PRESETS.get(
                precision_mode, 
                self.PRECISION_PRESETS['audio_only']
            )
            self.precision_type = 'time_based'
        
        self.timeline = []
    
    def _round_to_precision(self, milliseconds: float) -> float:
        """Round to current precision setting"""
        if self.precision_type == 'frame_based':
            # Round to nearest frame
            frames = round(milliseconds / self.precision_ms)
            return frames * self.precision_ms
        else:
            # Round to time-based precision
            return round(milliseconds / self.precision_ms) * self.precision_ms
    
    def upgrade_precision(self, new_precision_ms: float):
        """Upgrade precision for future expansion"""
        self.precision_ms = new_precision_ms
        # Rebuild timeline with new precision if needed
        self._rebuild_timeline()
```

### Configuration

```yaml
# config.yaml
timeline:
  # Auto-select based on media type
  precision_mode: "auto"  # auto, audio_only, video_sync, professional, sample_accurate
  
  # Manual override (if not using auto)
  # precision_ms: 100  # milliseconds
  
  # Video settings
  video_fps: 30
  
  # Future precision upgrade
  # enable_millisecond: false  # Reserved for future
  # enable_sample_accurate: false  # Reserved for future
```

### Use Case Selection

```python
# Example usage:

# Audio-only podcast
composer = TimelineComposer(media_type='audio', precision_mode='auto')
# → Uses 100ms precision

# Video podcast at 30fps
composer = TimelineComposer(media_type='video', precision_mode='auto')
# → Uses ~33ms frame-based precision

# Video at 60fps
composer = TimelineComposer(media_type='video', video_fps=60, precision_mode='auto')
# → Uses ~16.67ms frame-based precision

# Future: Professional broadcast
composer = TimelineComposer(precision_mode='professional')
# → Uses 10ms precision

# Future: Sample-accurate
composer = TimelineComposer(precision_mode='sample_accurate')
# → Uses ~0.023ms (sample-accurate)
```

---

## Consequences

**Positive:**
- ✅ Flexible precision selection based on use case
- ✅ Future-proof architecture
- ✅ Smart defaults (frame-based for video, time-based for audio)
- ✅ Easy to upgrade precision later
- ✅ Uses free tools (pydub, librosa, scipy)

**Negative:**
- ❌ More complex implementation (precision selection logic)
- ❌ Need to document precision options
- ❌ Slightly more code to maintain

**Mitigation:**
- Clear configuration defaults
- Good documentation of precision modes
- Modular design makes upgrades easy
- Test with different precision modes

---

## Future Expansion Path

The architecture allows easy upgrades:

1. **Current**: 100ms (audio) / 33ms (video frame-based)
2. **Phase 2**: Add 10ms professional mode
3. **Phase 3**: Add sample-accurate mode (if needed)
4. **Phase 4**: Real-time precision adjustment

All upgrades require minimal code changes due to configurable design.

