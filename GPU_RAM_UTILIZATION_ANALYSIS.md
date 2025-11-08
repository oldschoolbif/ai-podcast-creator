# GPU & RAM Utilization Analysis - Critical Issues

**Date:** 2025-11-03  
**Status:** 🔴 CRITICAL - System instability risk

## Executive Summary

The current implementation has **two critical issues** that pose a serious risk to system stability:

1. **RAM Usage: 95.6% (60.4 GB / 63.2 GB)** - System is dangerously close to OOM (Out of Memory)
2. **GPU Utilization: 0%** - GPU hardware is completely unused, wasting performance

## Problem 1: RAM Explosion During Video Composition

### Root Cause
The audio visualizer (`audio_visualizer.py`) loads **ALL video frames into memory** before processing:

```python
frames = []
for frame_idx in range(num_frames):  # ~9000 frames for 5-minute video
    # ... create frame ...
    frames.append(np.array(img))  # ~6MB per 1080p frame
```

**Math:**
- 5-minute video @ 30fps = **9,000 frames**
- Each 1920x1080 RGB frame = **6.22 MB**
- Total RAM needed = **9,000 × 6.22 MB = ~56 GB**
- Plus overhead, buffers, etc. = **~60 GB** ✅ Matches observed behavior

### Impact
- **System instability** - 95.6% RAM usage risks OOM crashes
- **Performance degradation** - System swaps to disk when RAM is full
- **Scalability failure** - Cannot handle longer videos or multiple concurrent processes

### Solution Required
Switch to **streaming/pipe-based processing**:
- Generate frames on-demand
- Stream directly to FFmpeg via pipe
- Never load all frames into memory

## Problem 2: GPU Not Being Used

### Root Causes

#### 2.1 Wav2Lip GPU Usage: 0%
**Issue:** Despite GPU environment variables, Wav2Lip shows 0% GPU utilization.

**Possible causes:**
- Wav2Lip subprocess not detecting GPU
- PyTorch not finding CUDA in subprocess environment
- Model running on CPU despite GPU availability

**Evidence:** Metrics show 0% GPU utilization during avatar generation (42 seconds).

#### 2.2 FFmpeg NVENC: Not Working
**Issue:** Video composition falls back to CPU (`libx264`) instead of GPU (`h264_nvenc`).

**Evidence:**
- Two-pass NVENC method fails silently
- Falls back to CPU encoding
- CPU encoding takes 28 minutes vs. expected <5 minutes with GPU

**Root cause:** The two-pass method creates a **massive temporary raw YUV file**:
- Raw 1920x1080 @ 30fps for 5 minutes = **~93 GB file**
- This likely fails due to disk space or file size limits
- System may be running out of disk space or hitting file size limits

#### 2.3 FFmpeg Buffering
**Issue:** `subprocess.run(..., capture_output=True)` buffers ALL output in memory.

**Impact:** For long videos, this can consume GBs of RAM just for stderr/stdout.

### Solutions Required
1. **Fix Wav2Lip GPU detection** - Verify CUDA is available in subprocess
2. **Fix NVENC two-pass method** - Use pipe-based streaming instead of temp file
3. **Use streaming subprocess** - Process FFmpeg output in real-time, don't buffer

## Problem 3: Inefficient Processing Pipeline

### Current Flow
```
Audio → Generate ALL frames in memory → Save to disk → FFmpeg reads from disk → Encode
```

### Problems
- **Double I/O**: Write frames to disk, then read them back
- **Memory spike**: All frames in RAM simultaneously
- **No streaming**: Can't start encoding until all frames are generated

### Optimal Flow
```
Audio → Generate frame → Stream to FFmpeg → Encode directly → Output
```

## Recommended Fixes (Priority Order)

### Priority 1: CRITICAL - Fix RAM Explosion
1. **Refactor audio visualizer** to stream frames to FFmpeg via pipe
2. **Remove frame array accumulation** - generate on-demand
3. **Use FFmpeg stdin** for frame input instead of disk files

### Priority 2: HIGH - Enable GPU Encoding
1. **Fix NVENC two-pass method** - use pipe instead of temp file
2. **Add proper error handling** - log why NVENC fails
3. **Verify GPU availability** in FFmpeg subprocess

### Priority 3: MEDIUM - Optimize Wav2Lip GPU
1. **Add GPU verification** after Wav2Lip subprocess
2. **Check PyTorch CUDA availability** in subprocess
3. **Add fallback detection** if GPU not detected

### Priority 4: LOW - General Optimizations
1. **Use streaming subprocess** for FFmpeg (process output line-by-line)
2. **Add memory limits** to prevent OOM
3. **Monitor disk space** before creating large temp files

## Expected Improvements

### After Fixes:
- **RAM Usage:** <10 GB (90% reduction)
- **GPU Utilization:** 80-100% during encoding
- **Video Composition Time:** 28 minutes → **<5 minutes** (5-6x faster)
- **System Stability:** No more OOM risk

## Implementation Plan

See `GPU_RAM_OPTIMIZATION_FIXES.md` for detailed implementation steps.

