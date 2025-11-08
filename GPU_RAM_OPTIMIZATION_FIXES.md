# GPU & RAM Optimization Fixes

**Priority:** 🔴 CRITICAL  
**Target:** Reduce RAM usage from 60GB to <10GB, enable GPU utilization

## Fix 1: Stream Audio Visualizer Frames (CRITICAL)

**Problem:** Loading all 9,000 frames into memory (60GB RAM usage)

**Solution:** Stream frames directly to FFmpeg via pipe

**Implementation:**
- Generate frames on-demand (not all at once)
- Pipe frames to FFmpeg stdin (rawvideo format)
- Never accumulate frames in memory

**Expected Impact:** 60GB → <1GB RAM usage

## Fix 2: Fix NVENC Two-Pass Method (HIGH)

**Problem:** Creating 93GB temp raw YUV file causes failures

**Solution:** Use pipe-based streaming instead of temp file

**Implementation:**
- Pipe filter_complex output directly to NVENC
- Use `subprocess.Popen` with pipes
- Stream data instead of writing to disk

**Expected Impact:** Enable GPU encoding, reduce encoding time from 28min → <5min

## Fix 3: Enable GPU in Wav2Lip (HIGH)

**Problem:** Wav2Lip shows 0% GPU utilization despite GPU available

**Solution:** Verify CUDA in subprocess and add GPU detection

**Implementation:**
- Check CUDA availability in Wav2Lip subprocess
- Add GPU verification after subprocess completes
- Log GPU usage for debugging

**Expected Impact:** GPU utilization during avatar generation

## Fix 4: Stream FFmpeg Output (MEDIUM)

**Problem:** `capture_output=True` buffers all output in memory

**Solution:** Process FFmpeg output line-by-line

**Implementation:**
- Use `subprocess.Popen` with real-time output processing
- Process stderr/stdout as it arrives
- Don't buffer entire output

**Expected Impact:** Reduce memory spikes during encoding

## Implementation Status

- [ ] Fix 1: Stream audio visualizer frames
- [ ] Fix 2: Fix NVENC pipe-based encoding  
- [ ] Fix 3: Enable Wav2Lip GPU detection
- [ ] Fix 4: Stream FFmpeg output processing

