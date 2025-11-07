# Test Coverage Review & Prioritization

## Current Status

**Overall Patch Coverage: 32.31%** (1345 lines missing coverage)

### File-by-File Breakdown

| File | Coverage | Missing Lines | Priority | Complexity |
|------|----------|---------------|----------|------------|
| `src/core/audio_visualizer.py` | 33.02% | 615 | **HIGH** | Very High |
| `src/core/avatar_generator.py` | 37.19% | 331 | **HIGH** | High |
| `src/cli/main.py` | 29.72% | 261 | **MEDIUM** | Medium |
| `src/core/face_generator.py` | 0.00% | 71 | **LOW** | Low |

---

## Detailed Analysis

### 1. `audio_visualizer.py` (615 missing lines, 33.02% coverage)

**What's Currently Tested:**
- ✅ Basic waveform frame generation
- ✅ Initialization with default config
- ✅ Some advanced feature initialization (orientation, rotation, amplitude, instances)
- ✅ Small audio handling

**What's Missing:**
- ❌ Edge cases for waveform drawing (`_draw_waveform_opencv`)
  - Invalid orientation_offset values (< 0, > 100)
  - Rotation at various angles (45°, 90°, 180°, 270°)
  - Amplitude multiplier edge cases (0.0, negative, very large values)
  - Multiple instances with intersection enabled
  - Empty/zero audio chunks
  - Very large audio chunks
- ❌ Error handling
  - Missing OpenCV (fallback to PIL)
  - Invalid audio file paths
  - Corrupted audio files
  - Memory errors with large files
- ❌ Streaming methods
  - `_generate_waveform_frames_streaming_chunked`
  - `_generate_waveform_frames_streaming_chunked_from_array`
  - Frame generation with different chunk sizes
- ❌ Video generation
  - `_stream_frames_to_video` (FFmpeg process handling)
  - `_frames_to_video` (fallback method)
  - Error recovery during video encoding
- ❌ Configuration edge cases
  - Invalid color values
  - Invalid position strings
  - Invalid percentage values (< 0, > 100)
- ❌ Special features
  - Randomization (`_randomize_config`)
  - Opacity and blend modes
  - Different waveform styles (bars, dots, filled)
- ❌ Duration calculation
  - `_get_audio_duration_ffmpeg` error cases
  - Timeout handling
  - Invalid file formats

**Impact:** **CRITICAL** - This is the core waveform functionality. Low coverage means new bugs could slip through.

**Estimated Effort:** 8-12 hours (many edge cases and integration scenarios)

---

### 2. `avatar_generator.py` (331 missing lines, 37.19% coverage)

**What's Currently Tested:**
- ✅ Basic avatar generation
- ✅ Missing source image handling
- ✅ Missing audio handling
- ✅ D-ID API error cases
- ✅ Wav2Lip script creation
- ✅ Import error handling

**What's Missing:**
- ❌ FFmpeg duration calculation (`_get_audio_duration_ffmpeg`)
  - Timeout scenarios
  - Invalid audio files
  - Missing ffprobe
- ❌ Wav2Lip generation edge cases
  - Model download failures (network errors, disk full)
  - Wav2Lip subprocess errors
  - Invalid Wav2Lip output
  - Large video file handling
- ❌ Fallback video creation
  - `_create_fallback_video` with various audio durations
  - Error handling in fallback path
- ❌ Model path resolution
  - None model path handling
  - Invalid model file paths
  - Model file corruption
- ❌ Temporary directory handling
  - Disk space errors
  - Permission errors
  - Cleanup failures

**Impact:** **HIGH** - Avatar generation is a core feature. Errors here break the main workflow.

**Estimated Effort:** 4-6 hours (mainly error paths and edge cases)

---

### 3. `cli/main.py` (261 missing lines, 29.72% coverage)

**What's Currently Tested:**
- ❌ **Very little CLI testing exists**

**What's Missing:**
- ❌ CLI command parsing and validation
  - `generate` command with all waveform parameters
  - `create` command with various options
  - Invalid argument combinations
  - Missing required arguments
- ❌ Waveform CLI parameter application
  - `_apply_waveform_cli_overrides` function
  - Parameter validation (ranges, types)
  - Parameter conflicts resolution
- ❌ Error handling in CLI
  - File not found errors
  - Permission errors
  - Invalid config files
  - GPU availability messages
- ❌ Progress indicators
  - Rich progress bars
  - Error message formatting
- ❌ Face generation CLI
  - `generate_face` command
  - Output path handling
  - Description validation

**Impact:** **MEDIUM** - CLI is user-facing, but errors are usually caught early. However, poor error messages hurt UX.

**Estimated Effort:** 4-6 hours (straightforward but requires CLI testing setup)

---

### 4. `face_generator.py` (71 missing lines, 0.00% coverage)

**What's Currently Tested:**
- ❌ **Nothing** - 0% coverage

**What's Missing:**
- ❌ Face generation
  - `generate` method with various descriptions
  - Custom prompts
  - Output path handling
- ❌ Error handling
  - Missing diffusers library
  - GPU/CPU fallback
  - Model download failures
  - Generation failures
- ❌ Prompt generation
  - `_description_to_prompt` method
  - Various description formats
  - Edge cases (empty, very long, special characters)
- ❌ Configuration
  - Invalid output directories
  - Permission errors

**Impact:** **LOW** - Face generation is optional and less frequently used. However, 0% coverage is concerning.

**Estimated Effort:** 2-3 hours (straightforward, but requires mocking Stable Diffusion)

---

## Recommendations by Priority (Risk & Importance Based)

### 🔴 **Priority 1: Critical Production Risks (Do First)**
1. **Integration tests for waveform pipeline** (CRITICAL)
   - End-to-end waveform generation with various configs
   - CLI → AudioVisualizer → VideoComposer flow
   - **Why:** Validates the full workflow works together - prevents production failures
   - **Risk:** High - Integration bugs break the entire feature
   - **Impact:** Catches production-breaking issues early
   - **Target:** 80%+ integration test coverage

2. **`audio_visualizer.py` critical error paths** (CRITICAL)
   - Error handling: Missing OpenCV, FFmpeg failures, invalid audio files
   - Boundary conditions: Invalid inputs, edge values, empty data
   - **Why:** Core functionality - errors here break waveform generation completely
   - **Risk:** High - Silent failures or crashes in production
   - **Impact:** Prevents production bugs and improves error messages
   - **Target:** 70%+ coverage (focus on error paths first)

### 🟠 **Priority 2: High-Risk Error Scenarios (Do Second)**
3. **`avatar_generator.py` error paths** (HIGH)
   - FFmpeg duration calculation errors (network timeouts, invalid files)
   - Wav2Lip generation failures (model download, subprocess errors)
   - Model validation and fallback scenarios
   - **Why:** Core feature - errors break main workflow completely
   - **Risk:** High - Avatar generation is a primary feature
   - **Impact:** Improves reliability and error recovery
   - **Target:** 75%+ coverage (focus on error paths)

4. **`audio_visualizer.py` edge cases & boundary conditions** (HIGH)
   - Invalid configuration values (negative, out of range)
   - Large file handling (memory, performance)
   - Streaming failures and recovery
   - **Why:** Prevents edge case bugs in production
   - **Risk:** Medium-High - Edge cases can cause unexpected failures
   - **Impact:** Improves robustness and handles edge cases gracefully
   - **Target:** 70%+ coverage (after critical error paths)

### 🟡 **Priority 3: User Experience & Validation (Do Third)**
5. **`cli/main.py` parameter validation** (MEDIUM)
   - CLI argument parsing and validation
   - Waveform parameter application and conflict resolution
   - Error message quality and user feedback
   - **Why:** Improves user experience and prevents invalid configurations
   - **Risk:** Medium - Poor UX and invalid configs hurt adoption
   - **Impact:** Better UX, easier debugging, prevents user errors
   - **Target:** 60%+ coverage

### 🟢 **Priority 4: Completeness (Do Last)**
6. **`face_generator.py` basic tests** (LOW)
   - Basic generation tests
   - Error handling (missing dependencies, generation failures)
   - **Why:** Optional feature, low usage, but 0% coverage is concerning
   - **Risk:** Low - Optional feature, not critical path
   - **Impact:** Completes test coverage, improves code quality
   - **Target:** 50%+ coverage

---

## Implementation Strategy

### Phase 1: Critical Edge Cases (Week 1)
- ✅ Add error handling tests for `audio_visualizer.py`
- ✅ Add boundary condition tests (invalid inputs, edge values)
- ✅ Add missing dependency tests (OpenCV, FFmpeg)
- **Target:** Increase `audio_visualizer.py` coverage to 60%+

### Phase 2: Avatar & Integration (Week 2)
- ✅ Add error path tests for `avatar_generator.py`
- ✅ Add integration tests for full pipeline
- ✅ Add CLI parameter validation tests
- **Target:** Increase `avatar_generator.py` coverage to 70%+, add integration test suite

### Phase 3: Polish & Completeness (Week 3)
- ✅ Add remaining CLI tests
- ✅ Add face generator tests
- ✅ Add performance/load tests
- **Target:** Overall coverage to 70%+

---

## Test Coverage Goals

| File | Current | Target | Gap |
|------|---------|--------|-----|
| `audio_visualizer.py` | 33.02% | 70% | +37% |
| `avatar_generator.py` | 37.19% | 75% | +38% |
| `cli/main.py` | 29.72% | 60% | +30% |
| `face_generator.py` | 0.00% | 50% | +50% |
| **Overall Patch** | **32.31%** | **70%** | **+38%** |

---

## Questions for Discussion

1. **Priority Order:** Do you agree with the priority ranking? Should we adjust based on your usage patterns?

2. **Coverage Threshold:** Is 70% a reasonable target, or should we aim higher/lower?

3. **Timeline:** Do we need to hit these targets before merging this PR, or can we do it in follow-up PRs?

4. **Focus Areas:** Are there specific features or error scenarios that are more important to you?

5. **Integration vs Unit Tests:** Should we prioritize integration tests (end-to-end) or unit tests (isolated components)?

---

## Next Steps

1. Review and agree on priorities
2. Create test plan for Priority 1 items
3. Start implementing tests incrementally
4. Track coverage improvements with each PR

