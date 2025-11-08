# GPU Optimization Plan - Budget-Friendly Solutions

**Date:** 2025-11-03  
**Goal:** Maximize GPU utilization for all components  
**Budget:** $0 (all solutions are free/open-source)

## Issues Identified

1. **TTS Generation (0% GPU)** - Using gTTS (cloud) instead of Coqui (GPU)
2. **Avatar Generation (0% GPU)** - Wav2Lip not using GPU despite "Using cuda" message
3. **Video Encoding (0% GPU)** - Using libx264 (CPU) instead of NVENC (GPU)

## Solutions (All FREE)

### 1. TTS: Switch to Coqui TTS ✅ FREE
**Current:** gTTS (cloud-based, no GPU)
**Solution:** Coqui TTS (free, open-source, GPU-accelerated)
**Cost:** $0
**Confidence:** Very High (already implemented, just need to switch default)
**Action:** Change `config.yaml` default from `gtts` to `coqui`

### 2. Video Encoding: Use PyNvVideoCodec or ffmpegcv ✅ FREE
**Current:** libx264 (CPU encoding)
**Solution A:** PyNvVideoCodec (NVIDIA's official Python library)
- **Cost:** $0 (free, open-source)
- **Confidence:** High (official NVIDIA library)
- **Installation:** `pip install pynvvideocodec`
- **Pros:** Direct hardware acceleration, official support
- **Cons:** May need FFmpeg integration

**Solution B:** ffmpegcv with CUDA support
- **Cost:** $0 (free, open-source)
- **Confidence:** High (widely used, CUDA support)
- **Installation:** `pip install ffmpegcv[cuda]`
- **Pros:** Drop-in replacement for OpenCV, easy integration
- **Cons:** New dependency

**Recommended:** Try Solution B first (ffmpegcv) - easier integration

### 3. Wav2Lip: Ensure Explicit GPU Device ✅ FREE
**Current:** Wav2Lip says "Using cuda" but 0% GPU utilization
**Solution:** Explicitly set device in Wav2Lip inference
**Cost:** $0 (code fix)
**Confidence:** High (standard PyTorch practice)
**Action:** 
- Check Wav2Lip inference script for device assignment
- Ensure model.to(device) is called
- Verify CUDA_VISIBLE_DEVICES is set correctly

## Implementation Priority

1. **TTS (Easiest)** - Just change config default
2. **Wav2Lip (Critical)** - Fix device assignment
3. **Video Encoding (High Impact)** - Integrate GPU encoding

## Expected Results

- **TTS:** 40-80% GPU utilization during generation
- **Avatar:** 80-100% GPU utilization (Wav2Lip)
- **Video Encoding:** 20-40% GPU utilization (NVENC)
- **Total Speedup:** 3-4x faster (68s → 15-20s)

## Alternative Considerations (If needed)

### SadTalker (Alternative to Wav2Lip)
- **Cost:** $0 (free, open-source)
- **GPU Support:** Excellent (designed for GPU)
- **Quality:** Better facial expressions than Wav2Lip
- **Confidence:** Very High (already integrated, just need to switch)

### OpenCV CUDA (Video Processing)
- **Cost:** $0 (free, open-source)
- **GPU Support:** Good (CUDA-accelerated operations)
- **Confidence:** High (widely used)

## Budget Summary

**Total Cost:** $0
**All solutions are free and open-source**
**No subscriptions or licenses required**

