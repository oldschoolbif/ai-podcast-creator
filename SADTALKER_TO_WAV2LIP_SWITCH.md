# SadTalker → Wav2Lip Switch Decision

**Date:** 2025-11-03  
**Decision:** Switch default avatar engine from SadTalker to Wav2Lip

## Why Switch?

### SadTalker Issues ❌

1. **NumPy 2.x Incompatibility**
   - SadTalker uses `np.VisibleDeprecationWarning` (removed in NumPy 2.0+)
   - Project has NumPy 2.2.6 installed
   - Causes ImportError: `AttributeError: module 'numpy' has no attribute 'VisibleDeprecationWarning'`

2. **Complex Dependencies**
   - Requires: face3d, basicsr, facexlib, gfpgan, safetensors
   - More setup complexity
   - Higher chance of dependency conflicts

3. **Large Model Downloads**
   - ~5GB of checkpoints required
   - Longer setup time

4. **Currently Broken**
   - Cannot run in current environment
   - Falls back to static avatar (no lip-sync)

### Wav2Lip Advantages ✅

1. **Already Working**
   - Fully implemented in codebase
   - GPU fixes already applied
   - Tested and functional

2. **Simpler Setup**
   - Fewer dependencies
   - Smaller model (~200MB vs 5GB)
   - Easier to maintain

3. **Better Integration**
   - Face detection already integrated
   - GPU environment variables configured
   - Path resolution working correctly

4. **Reliable**
   - No NumPy compatibility issues
   - Works with Python 3.13
   - Works with current NumPy version

## Trade-offs

| Feature | SadTalker | Wav2Lip |
|---------|-----------|---------|
| **Status** | ❌ Broken (NumPy 2.x) | ✅ Working |
| **Quality** | Excellent (head movement, expressions) | Good (lip-sync only) |
| **Setup** | Complex (5GB models, many deps) | Simple (200MB model) |
| **Dependencies** | Many (face3d, basicsr, etc.) | Few (standard ML libs) |
| **GPU Support** | ✅ Yes (when working) | ✅ Yes (configured) |
| **Reliability** | ❌ Broken | ✅ Working |

## Implementation

### Config Change

**Before:**
```yaml
avatar:
  engine: "sadtalker"
```

**After:**
```yaml
avatar:
  engine: "wav2lip"
```

### What This Means

- ✅ **Immediate:** Lip-sync will work
- ✅ **GPU:** GPU acceleration will work (already configured)
- ⚠️ **Quality:** No head movement (just lip-sync)
- ✅ **Reliability:** No dependency issues

## Future Options

### Option 1: Fix SadTalker (Later)
- Patch `preprocess.py` to remove deprecated NumPy warning
- Test with NumPy 2.x
- Keep as alternative option

### Option 2: Keep Wav2Lip as Default
- Simpler, more reliable
- Works with modern dependencies
- Good enough for most use cases

### Option 3: Support Both
- Wav2Lip as default (working)
- SadTalker as optional (when fixed)
- User can choose based on needs

## Recommendation

**Use Wav2Lip as default** until:
1. SadTalker NumPy compatibility is fixed, OR
2. Alternative solution with head movement is found

**Reasoning:**
- Working system > Broken system
- Lip-sync is the core requirement
- Head movement is nice-to-have, not essential
- Can add SadTalker back later when fixed

## Status

✅ **Switched:** Default avatar engine changed to Wav2Lip  
✅ **Config Updated:** `config.yaml` now uses `wav2lip`  
✅ **Ready:** System ready to use with Wav2Lip  

