# Progress Monitoring Guide

**Date:** 2025-11-03  
**Feature:** File growth monitoring for long-running operations

## Overview

File growth monitoring has been implemented to show progress during video generation, eliminating the "is it hung?" uncertainty.

## How It Works

### File Monitor (`src/utils/file_monitor.py`)

Monitors file size growth every 2 seconds and reports:
- **Current file size** (MB)
- **Growth rate** (MB/second)
- **Stall detection** (warns if no growth for 10+ seconds)

### Integration Points

1. **Avatar Generation** (Wav2Lip/SadTalker)
   - Monitors avatar video output
   - Shows: `📊 Avatar: X.X MB (Y.Y MB/s)`
   - Updates every 2 seconds

2. **Video Composition** (FFmpeg encoding)
   - Monitors final video output
   - Shows: `📊 File size: X.X MB, rate: Y.Y MB/s`
   - Updates every 2 seconds

3. **NVENC Encoding** (GPU two-pass method)
   - Monitors encoded video output
   - Shows: `📊 Encoding: X.X MB (Y.Y MB/s)`
   - Updates every 2 seconds

## Stall Detection

**Threshold:** 10 seconds of no growth (< 0.01 MB)

**Warning Display:**
```
📊 File size: 15.3 MB, rate: 0.00 MB/s [⚠️ Stalled 15s]
```

**What to Expect:**
- **Normal:** File size grows steadily, rate varies (0.1-5 MB/s typical)
- **Stalled:** No growth for 10+ seconds → Warning appears
- **Hung:** No growth for 30+ seconds → Likely stuck (consider canceling)

## Expected File Growth Rates

### Avatar Generation (Wav2Lip)
- **Normal:** 0.5-2 MB/s
- **Duration:** ~30-60 seconds for 5-minute video
- **Final size:** ~20-30 MB

### Video Composition (FFmpeg)
- **Normal:** 0.1-1 MB/s (CPU) or 2-5 MB/s (GPU if working)
- **Duration:** 5-30 minutes depending on quality and length
- **Final size:** Varies by quality and duration

### High Quality 5-Minute Video
- **Expected final size:** 50-200 MB
- **Expected duration:** 5-15 minutes
- **Expected rate:** 0.5-2 MB/s

## Troubleshooting

### "File size: 0.0 MB" for a long time
- **Possible:** File hasn't been created yet (normal for first few seconds)
- **Action:** Wait up to 10 seconds before concern

### "Stalled 30s" warning
- **Possible:** Process is hung or waiting for resources
- **Action:** Check CPU/GPU usage, consider canceling if no other activity

### File size grows but very slowly (< 0.1 MB/s)
- **Possible:** CPU encoding (expected for large files)
- **Action:** Normal for CPU encoding, will take longer

### File size jumps then stops
- **Possible:** Process completed or error occurred
- **Action:** Check if process finished (should see completion message)

## Time Expectations

### Before File Growth Starts
- **Avatar generation:** 5-15 seconds (model loading)
- **Video composition:** 2-5 seconds (FFmpeg initialization)

### If No Growth After:
- **30 seconds:** Likely issue (check logs)
- **60 seconds:** Probably hung (consider canceling)
- **2 minutes:** Definitely hung (cancel and investigate)

## Example Output

```
🎬 Generating talking head with Wav2Lip...
  📊 Avatar: 0.0 MB (0.00 MB/s)
  📊 Avatar: 2.3 MB (1.15 MB/s)
  📊 Avatar: 5.1 MB (1.40 MB/s)
  📊 Avatar: 8.7 MB (1.80 MB/s)
  📊 Avatar: 12.4 MB (1.85 MB/s)
  📊 Avatar: 15.9 MB (1.75 MB/s)
  📊 Avatar: 19.2 MB (1.65 MB/s)
  📊 Avatar: 22.1 MB (1.45 MB/s)
  📊 Avatar: 24.7 MB (1.30 MB/s)
✓ Avatar video generated
```

## Benefits

1. **Visual Progress:** See file growing = process working
2. **Stall Detection:** Know when process is stuck
3. **Time Estimation:** Growth rate helps estimate completion
4. **Peace of Mind:** No more "is it hung?" uncertainty

