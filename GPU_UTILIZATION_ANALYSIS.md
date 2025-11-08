# GPU Utilization Analysis - Test Results

**Date:** 2025-11-03  
**Test:** `test_script2 for JE.txt` with --avatar --visualize --background --skip-music

## Current GPU Utilization Status

### ❌ Components NOT Using GPU (0% Utilization):

1. **script_parsing** - 0% GPU ✅ Expected
   - Text parsing, no GPU needed

2. **tts_generation** - 0% GPU ❌ **ISSUE**
   - **Root Cause:** Using `gTTS` (cloud-based, CPU/network) instead of `Coqui TTS` (GPU-accelerated)
   - **Fix:** Switch to Coqui TTS in config.yaml or use `--tts-engine coqui`
   - **Expected GPU Usage:** 40-80% during TTS generation

3. **audio_mixing** - 0% GPU ✅ Expected
   - Using `pydub` which is CPU-based
   - Audio mixing is typically fast enough that GPU isn't needed

4. **avatar_generation** - 0% GPU ❌ **CRITICAL ISSUE**
   - **Root Cause:** Wav2Lip subprocess reports "Using cuda" but actual GPU compute utilization is 0%
   - **Possible Issues:**
     - Model loads on GPU but inference happens too fast to measure
     - Subprocess may not actually be using GPU despite environment variables
     - Metrics timing may be measuring before/after instead of during execution
   - **Evidence:**
     - GPU memory allocated: +0.18 GB (model loaded)
     - GPU utilization: 0% (no compute happening)
     - CPU usage: 16.1% (workload running on CPU)
   - **Expected GPU Usage:** 80-100% during Wav2Lip inference
   - **Duration:** 29.60s (should be much faster with GPU)

5. **video_composition** - 0% GPU ❌ **ISSUE**
   - **Root Cause:** Final composition uses `libx264` (CPU) instead of `h264_nvenc` (GPU)
   - **Evidence:** Log shows "[CPU] Using libx264 for final composition"
   - **Expected GPU Usage:** 20-40% during video encoding
   - **Duration:** 37.36s (could be 5-10x faster with NVENC)

## Summary

**Total GPU Utilization:** 0% across all components  
**Total Duration:** 68.62s  
**Expected Duration with Full GPU:** ~15-20s (3-4x faster)

### Critical Issues to Fix:

1. **Wav2Lip not using GPU compute** - Most critical
   - Wav2Lip says "Using cuda" but 0% GPU utilization
   - 29.6s duration suggests CPU execution
   - Need to verify Wav2Lip inference.py actually uses GPU

2. **Video encoding using CPU** - High impact
   - Final composition uses libx264 instead of NVENC
   - 37.36s duration could be 5-10x faster with GPU

3. **TTS using cloud service** - Medium impact
   - gTTS is cloud-based, should use Coqui for GPU acceleration

## Next Steps

1. Verify Wav2Lip inference.py is actually using GPU (check PyTorch device placement)
2. Fix video composition to use NVENC instead of libx264
3. Consider switching default TTS to Coqui for GPU acceleration
4. Add continuous GPU monitoring during subprocess execution

