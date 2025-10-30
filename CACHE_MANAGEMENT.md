# 🧹 Cache Management Guide

## Why Cache Matters

### The Good 👍
- **Speed**: Regenerating same content is instant
- **Bandwidth**: Saves gTTS API calls
- **Testing**: Quick iterations when tweaking other settings

### The Bad 👎
- **Stale data**: May use old voice when changing engines (like we just experienced!)
- **Disk space**: Cache grows over time
- **Confusion**: Hard to tell if changes took effect

---

## 🚨 **When Cache Causes Problems**

### Real Example from Today:

**Test 3 Issue**:
```
✅ Speech generated: data/cache/tts/34e6460442eddc145718d432db966844.mp3
```
This was **cached female voice** from Test 2!

**Test 4 Fix**:
```
✓ Using pyttsx3 voice: English (America) (Voice 24)
Audio saved to: 6ab155e14827b0eda35cae8a33d23f08.wav  👈 NEW cache!
```

**Lesson**: When changing TTS engines, **clear the cache first!**

---

## 🔧 **New Cleanup Command**

### 1️⃣ Preview What Will Be Deleted:
```bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate

python3 -m src.cli.main cleanup --dry-run
```

**Output Example**:
```
┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━┓
┃ Directory    ┃ Files ┃ Size   ┃ Action  ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━┩
│ data/cache   │ 6     │ 5.2 MB │ Preview │
│ data/outputs │ 5     │ 8.2 MB │ Preview │
└──────────────┴───────┴────────┴─────────┘

Dry run: Would delete 11 files (13.4 MB)
```

### 2️⃣ Clear Cache Only (Keep Your Videos):
```bash
python3 -m src.cli.main cleanup --cache-only
```
- ✅ Deletes: TTS audio, mixed audio, temp files
- ❌ Keeps: Your final MP4 videos

### 3️⃣ Clear Outputs Only (Keep Cache):
```bash
python3 -m src.cli.main cleanup --outputs-only
```
- ✅ Deletes: Generated MP4 videos
- ❌ Keeps: Cache for faster regeneration

### 4️⃣ Clear Everything (With Confirmation):
```bash
python3 -m src.cli.main cleanup
```
You'll be prompted:
```
Warning: About to delete 11 files (13.4 MB)
Are you sure you want to continue? [y/N]:
```

### 5️⃣ Clear Everything (No Prompt):
```bash
python3 -m src.cli.main cleanup --force
```
⚠️ **Use with caution!** Deletes immediately without asking.

---

## 📂 **What Gets Cached**

### Cache Directory (`data/cache/`):

#### `tts/` - Voice Audio
- **What**: Generated speech (MP3/WAV)
- **When**: After TTS generation
- **Size**: ~1-3 MB per script
- **Key**: MD5 hash of script text
- **Problem**: **Doesn't include engine/voice in key!**

#### `mixed/` - Mixed Audio
- **What**: Voice + music combined
- **When**: After audio mixing
- **Size**: ~2-4 MB per podcast
- **Key**: Based on voice audio filename

#### `models/` - AI Models (if using advanced TTS)
- **What**: Downloaded Coqui/SadTalker models
- **When**: First use of advanced engines
- **Size**: Can be **GBs**
- **Note**: Usually keep these!

### Output Directory (`data/outputs/`):

#### Final Videos
- **What**: Your generated MP4 files
- **Size**: ~800 KB - 2 MB per video
- **Note**: These are your final products!

---

## 🎯 **When to Clear Cache**

### ✅ **Always Clear When:**

1. **Changing TTS Engine**:
   ```bash
   # Switching from gTTS to pyttsx3?
   python3 -m src.cli.main cleanup --cache-only --force
   ```

2. **Changing Voice Settings**:
   - Different voice ID
   - Different rate/speed
   - Different accent

3. **Testing Voice Changes**:
   ```bash
   # Before each voice test
   rm data/cache/tts/*.mp3
   ```

4. **Script Changed But Key Same**:
   - Edited script slightly
   - Cache key might be identical
   - Force regeneration

### ⚠️ **Maybe Clear When:**

1. **Running Out of Disk Space**:
   ```bash
   python3 -m src.cli.main cleanup --dry-run
   # Review sizes, then cleanup
   ```

2. **Project Complete**:
   - Keep final videos
   - Clear cache to save space

3. **Troubleshooting Weird Issues**:
   - Cache corruption?
   - Clear and regenerate

### ❌ **Don't Clear When:**

1. **Just Testing Music/Video Settings**:
   - Cache helps speed up iteration
   - Only voice audio is cached

2. **Regenerating Same Content**:
   - Cache is your friend!
   - Instant generation

3. **Model Files**:
   - Don't delete `data/models/`
   - These are large downloads

---

## 🤖 **Automated Cleanup Options**

### Option 1: Auto-Cleanup Config (Already Available!)

Edit `config.yaml`:
```yaml
storage:
  # Cleanup old cache files
  auto_cleanup: true
  cache_retention_days: 7  # Delete cache older than 7 days
```

**How it works**:
- Runs automatically after each generation
- Only deletes cache files older than N days
- Keeps recent cache for quick regeneration

### Option 2: Manual After Each Video

Add to your workflow:
```bash
# Create podcast
python3 -m src.cli.main create "script.txt" -o output

# Review video
vlc data/outputs/output.mp4

# If good, clear cache
python3 -m src.cli.main cleanup --cache-only --force
```

### Option 3: Scheduled Cleanup (Cron Job)

Create `cleanup_weekly.sh`:
```bash
#!/bin/bash
cd /mnt/d/dev/AI_Podcast_Creator
source venv/bin/activate
python3 -m src.cli.main cleanup --cache-only --force
```

Add to crontab:
```bash
# Run every Sunday at 2 AM
0 2 * * 0 /mnt/d/dev/AI_Podcast_Creator/cleanup_weekly.sh
```

---

## 💡 **Best Practices**

### Workflow 1: Quick Iteration (Keep Cache)
```bash
# Create
python3 -m src.cli.main create "script.txt" -o v1

# Adjust music, recreate (uses cached voice!)
python3 -m src.cli.main create "script.txt" --music-offset 30 -o v2

# Try different music (still uses cached voice!)
python3 -m src.cli.main create "script.txt" --music-file "other.mp3" -o v3
```

✅ **Fast**: Voice cached, only video rerendering  
✅ **Efficient**: No redundant TTS calls

### Workflow 2: Voice Testing (Clear Cache)
```bash
# Test voice 1
python3 -m src.cli.main cleanup --cache-only --force
python3 -m src.cli.main create "script.txt" --config config1.yaml -o voice1

# Test voice 2
python3 -m src.cli.main cleanup --cache-only --force
python3 -m src.cli.main create "script.txt" --config config2.yaml -o voice2

# Compare videos
```

✅ **Accurate**: Fresh voice generation each time  
✅ **No confusion**: Cache doesn't interfere

### Workflow 3: Production (Selective Cleanup)
```bash
# Create final podcast
python3 -m src.cli.main create "final_script.txt" -o podcast_ep1

# Copy to safe location
cp data/outputs/podcast_ep1.mp4 ~/Videos/

# Clear cache but keep output
python3 -m src.cli.main cleanup --cache-only
```

✅ **Safe**: Final video preserved  
✅ **Clean**: Disk space recovered

---

## 📊 **Cache Size Monitoring**

### Check Current Cache Size:
```bash
# Preview cleanup (shows sizes)
python3 -m src.cli.main cleanup --dry-run

# Manual check
du -sh data/cache
du -sh data/outputs
```

### Typical Sizes:
- **Small project** (1-5 videos): 10-50 MB
- **Medium project** (10-20 videos): 50-200 MB
- **Large project** (50+ videos): 200 MB - 1 GB
- **With models** (Coqui/SadTalker): +2-5 GB

---

## 🔍 **Debugging Cache Issues**

### Issue: Voice Sounds Wrong
```bash
# Solution: Clear TTS cache
rm data/cache/tts/*.mp3
rm data/cache/tts/*.wav

# Or use cleanup command
python3 -m src.cli.main cleanup --cache-only --force
```

### Issue: Changes Not Appearing
```bash
# Check what's cached
ls -lh data/cache/tts/
ls -lh data/cache/mixed/

# Clear and regenerate
python3 -m src.cli.main cleanup --cache-only --force
python3 -m src.cli.main create "script.txt" -o test
```

### Issue: Out of Disk Space
```bash
# Check sizes
python3 -m src.cli.main cleanup --dry-run

# Clear old outputs you don't need
python3 -m src.cli.main cleanup --outputs-only

# Or clear everything
python3 -m src.cli.main cleanup --force
```

---

## 🎯 **Recommended Strategy**

### For Daily Use:
1. **Keep cache** for speed
2. **Clear cache** when changing voices
3. **Review cache size** weekly
4. **Keep important videos** in separate folder

### After Testing Session:
```bash
# Completed testing multiple voices?
python3 -m src.cli.main cleanup --cache-only --force

# Completed project?
# 1. Copy final videos to safe location
cp data/outputs/final_*.mp4 ~/Videos/

# 2. Clear everything
python3 -m src.cli.main cleanup --force
```

### Before Major Changes:
```bash
# Changing TTS engine (gTTS → pyttsx3)?
python3 -m src.cli.main cleanup --cache-only --force

# Upgrading Python/libraries?
python3 -m src.cli.main cleanup --force
```

---

## 📋 **Quick Reference**

| Command | What It Does | When to Use |
|---------|-------------|-------------|
| `cleanup --dry-run` | Preview deletion | Before cleaning |
| `cleanup --cache-only` | Clear cache only | Voice/engine changes |
| `cleanup --outputs-only` | Clear videos only | Keep cache, free space |
| `cleanup` | Clear everything | Start fresh |
| `cleanup --force` | No confirmation | Automated scripts |

---

## 🎓 **What We Learned Today**

### The Cache Problem:
```
Script Text → MD5 Hash → Cache Key
"Tech news..." → 34e6460442eddc145718d432db966844.mp3

Problem: Same script + different engine = same cache key!
gTTS voice   → 34e6460442eddc145718d432db966844.mp3
pyttsx3 voice → 34e6460442eddc145718d432db966844.mp3 (reused!)
```

### The Solution:
```bash
# Clear cache before engine change
rm data/cache/tts/34e6460442eddc145718d432db966844.mp3

# Or use new cleanup command
python3 -m src.cli.main cleanup --cache-only --force
```

### The New Cache Key:
```
Script Text + Engine → Better Cache Key (future improvement!)
"Tech news..." + gTTS → 34e6460442eddc145718d432db966844_gtts.mp3
"Tech news..." + pyttsx3 → 6ab155e14827b0eda35cae8a33d23f08_pyttsx3.mp3
```

---

## ✨ **Summary**

✅ **New cleanup command** added  
✅ **Dry-run mode** for safety  
✅ **Selective cleanup** (cache/outputs)  
✅ **Auto-cleanup** in config  
✅ **Best practices** documented  

**Key Takeaway**: Clear cache when changing voice engines!

---

*Cache management guide complete*  
*Command: `python3 -m src.cli.main cleanup --help`*





