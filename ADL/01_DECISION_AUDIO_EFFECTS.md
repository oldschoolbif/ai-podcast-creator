# Decision 1: Audio Effects Library Choice

## Current State

**What you already have:**
- ✅ `pydub` (0.25.1) - Basic audio manipulation, mixing, format conversion
- ✅ `librosa` (0.10.2) - Audio analysis, feature extraction
- ✅ `soundfile` (0.12.1) - Audio I/O (reading/writing files)
- ✅ `scipy` (1.11.0) - Signal processing utilities
- ✅ `numpy` (1.23.0) - Numerical computing

**Current limitations:**
- `pydub` can do basic effects but requires manual implementation of:
  - EQ (equalization)
  - Compression
  - Reverb
  - De-esser
- You'd need to build these from scratch using `scipy`/`numpy`

---

## Required Features (from script format)

Looking at your test script, you need:

1. **EQ (Equalization)**
   - Low-cut at 90Hz
   - Presence boost at 4kHz (+2dB)
   - Smooth curves, no artifacts

2. **Compression**
   - Threshold: -3dB
   - Ratio: 3:1
   - Attack/Release: 5ms/50ms

3. **Reverb**
   - Small room space
   - Subtle (10% wet)
   - Natural decay

4. **De-esser**
   - Frequency-specific (6kHz range)
   - Light processing on "s" and "ch"
   - Threshold: -20dB

5. **Volume Automation**
   - Fade in/out (linear/logarithmic curves)
   - Precise dB control (+/-XdB)
   - Dynamic ducking

---

## Option Comparison

### Option A: Add `pedalboard` (Spotify's Library)

**What it is:**
- Professional audio effects library from Spotify
- Industry-standard algorithms
- Python-native, GPU-accelerated where possible

**Pros:**
- ✅ **Professional quality**: Production-ready effects
- ✅ **Complete feature set**: All effects you need out-of-the-box
- ✅ **Easy to use**: Simple API, well-documented
- ✅ **Active maintenance**: Spotify actively maintains it
- ✅ **Performance**: Optimized C++ backend
- ✅ **License**: MIT (permissive)
- ✅ **Community**: Growing adoption in audio Python projects

**Cons:**
- ❌ **New dependency**: Adds ~10-15MB to installation
- ❌ **Learning curve**: New API to learn (but simple)
- ❌ **Potential overkill**: Might be more than you need if only doing basic processing

**Installation:**
```bash
pip install pedalboard>=0.7.0
```

**Example Usage:**
```python
from pedalboard import Pedalboard, Compressor, Reverb, LowpassFilter, Gain

board = Pedalboard([
    LowpassFilter(cutoff_frequency_hz=90),  # Low-cut
    Compressor(threshold_db=-3, ratio=3.0),
    Reverb(room_size=0.3, wet_level=0.1),
    Gain(gain_db=2.0)  # Presence boost
])

processed_audio = board(audio_array, sample_rate)
```

**Size Impact:**
- Library size: ~10-15MB
- Runtime memory: +5-10MB
- Build time: No compilation needed (wheels available)

---

### Option B: Extend Current Stack (librosa + scipy)

**What it is:**
- Build effects using existing `librosa` + `scipy` + `numpy`

**Pros:**
- ✅ **No new dependencies**: Use what you have
- ✅ **Full control**: Implement exactly what you need
- ✅ **Lightweight**: No additional installation size
- ✅ **Educational**: You understand every step

**Cons:**
- ❌ **Time investment**: 2-3 days to implement all effects properly
- ❌ **Quality concerns**: Need to ensure professional-grade algorithms
- ❌ **Maintenance burden**: You maintain the code
- ❌ **Testing complexity**: More code to test and debug
- ❌ **Error-prone**: Audio DSP is complex; easy to introduce artifacts

**Example Implementation:**
```python
import numpy as np
from scipy import signal
from librosa import effects

def apply_eq(audio, sample_rate, low_cut_hz=90, boost_hz=4000, boost_db=2.0):
    # Low-cut filter
    b, a = signal.butter(4, low_cut_hz, 'high', fs=sample_rate)
    audio = signal.filtfilt(b, a, audio)
    
    # Presence boost (simplified - would need proper parametric EQ)
    # This is more complex than it seems...
    return audio

def apply_compression(audio, threshold_db=-3, ratio=3.0):
    # Compression is complex - involves envelope detection, gain reduction
    # Multiple implementation approaches...
    # This could take hours to get right
    return audio
```

**Estimated Development Time:**
- EQ: 4-6 hours
- Compression: 8-12 hours
- Reverb: 6-10 hours
- De-esser: 4-8 hours
- **Total: 22-36 hours** (3-5 days)

---

### Option C: Hybrid Approach (pedalboard + pydub)

**What it is:**
- Use `pedalboard` for effects
- Keep `pydub` for mixing/timing/format handling

**Pros:**
- ✅ **Best of both**: Professional effects + easy mixing
- ✅ **Incremental adoption**: Can add `pedalboard` gradually
- ✅ **Flexibility**: Use right tool for each job

**Cons:**
- ⚠️ **Coordination**: Need to convert between formats
  - `pydub` uses AudioSegment objects
  - `pedalboard` uses numpy arrays
  - Easy conversion but adds minor complexity

**Example:**
```python
from pydub import AudioSegment
import numpy as np
from pedalboard import Pedalboard, Compressor

# Load with pydub
audio = AudioSegment.from_file("input.mp3")

# Convert to numpy for pedalboard
samples = np.array(audio.get_array_of_samples())
sample_rate = audio.frame_rate

# Apply effects
board = Pedalboard([Compressor()])
processed = board(samples, sample_rate)

# Convert back to pydub
processed_audio = AudioSegment(
    processed.tobytes(),
    frame_rate=sample_rate,
    channels=audio.channels,
    sample_width=audio.sample_width
)
```

---

## Decision Criteria

Rate each option (1-5 scale) on:

### 1. Development Speed
- **Option A (pedalboard)**: ⭐⭐⭐⭐⭐ (Use immediately)
- **Option B (build from scratch)**: ⭐⭐ (3-5 days development)
- **Option C (hybrid)**: ⭐⭐⭐⭐ (Quick integration)

### 2. Code Quality & Reliability
- **Option A**: ⭐⭐⭐⭐⭐ (Production-tested)
- **Option B**: ⭐⭐⭐ (Depends on your implementation)
- **Option C**: ⭐⭐⭐⭐⭐ (Best of both)

### 3. Maintenance Burden
- **Option A**: ⭐⭐⭐⭐⭐ (Maintained by Spotify)
- **Option B**: ⭐⭐ (You maintain everything)
- **Option C**: ⭐⭐⭐⭐ (Split maintenance)

### 4. Performance
- **Option A**: ⭐⭐⭐⭐⭐ (Optimized C++ backend)
- **Option B**: ⭐⭐⭐⭐ (scipy/numpy optimized, but you optimize)
- **Option C**: ⭐⭐⭐⭐⭐ (Same as A)

### 5. Feature Completeness
- **Option A**: ⭐⭐⭐⭐⭐ (All effects ready)
- **Option B**: ⭐⭐⭐ (Build as needed, may miss edge cases)
- **Option C**: ⭐⭐⭐⭐⭐ (Same as A)

### 6. Learning Curve
- **Option A**: ⭐⭐⭐⭐ (Simple API, good docs)
- **Option B**: ⭐⭐ (Need DSP knowledge)
- **Option C**: ⭐⭐⭐⭐ (Moderate, mostly pedalboard)

### 7. Installation Size Impact
- **Option A**: ⭐⭐⭐ (Adds ~15MB)
- **Option B**: ⭐⭐⭐⭐⭐ (No additional size)
- **Option C**: ⭐⭐⭐ (Same as A)

---

## Questions to Consider

### 1. Time Budget
**Q:** How quickly do you need this feature working?
- **If "immediately/asap"**: → Option A or C
- **If "can spend a week"**: → Option B is viable
- **If "flexible"**: → Option A or C (better long-term)

### 2. Quality Requirements
**Q:** Is this for production podcasts or experimentation?
- **Production**: → Option A or C (proven quality)
- **Experimentation**: → Option B (learning experience)

### 3. Team/Resources
**Q:** Do you have DSP (Digital Signal Processing) expertise?
- **Yes**: → Option B is feasible
- **No**: → Option A or C (use proven solutions)

### 4. Future Maintenance
**Q:** Will you need to add more effects later?
- **Yes**: → Option A or C (easy to extend)
- **No**: → Option B (one-time implementation)

### 5. Platform/Deployment
**Q:** Are there constraints on dependency size?
- **No constraints**: → Option A or C
- **Minimal dependencies needed**: → Option B

---

## My Recommendation

**Option C: Hybrid Approach (pedalboard + pydub)**

**Reasoning:**
1. ✅ **Fastest to implement**: Can start using immediately
2. ✅ **Professional quality**: Production-ready effects
3. ✅ **Leverages existing**: Keeps `pydub` for what it does well
4. ✅ **Low risk**: Proven library from Spotify
5. ✅ **Future-proof**: Easy to extend with more effects
6. ✅ **Maintenance**: Library maintained by Spotify team

**Trade-offs accepted:**
- Adds ~15MB dependency (minimal in modern systems)
- Small learning curve for `pedalboard` API (but well-documented)

---

## Alternative Consideration

**If dependency size is critical:**

Consider **Option B** but start with just **compression** and **EQ**:
- Implement those two first (1-2 days)
- Use simpler reverb (convolution-based with impulse response)
- De-esser can be simpler (high-shelf filter + gate)
- **Total: 2-3 days** vs. 3-5 days for full implementation

Then evaluate if you need `pedalboard` later.

---

## Next Steps After Decision

**If you choose Option A or C:**
1. Add `pedalboard>=0.7.0` to `requirements.txt`
2. Create `src/core/audio_processor.py` using pedalboard
3. Test with sample audio
4. Integrate into pipeline

**If you choose Option B:**
1. Create `src/core/audio_processor.py`
2. Implement effects one at a time (EQ first, then compression, etc.)
3. Test each effect thoroughly
4. Consider using reference implementations from audio DSP textbooks

---

## Your Decision

**Please consider:**
1. What's your time budget? ⏱️
2. What's your quality bar? 🎯
3. Do you have DSP expertise? 🧠
4. What's your dependency tolerance? 📦

**Share your answers and I'll help you finalize the choice!**

