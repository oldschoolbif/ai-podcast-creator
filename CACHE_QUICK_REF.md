# 🧹 Cache Quick Reference Card

## When to Clear Cache

| Situation | Command | Why |
|-----------|---------|-----|
| **Changing voice engine** | `cleanup --cache-only --force` | Cache key doesn't include engine |
| **Testing different voices** | `cleanup --cache-only --force` | Ensure fresh generation |
| **Script updated** | `rm data/cache/tts/*.mp3` | Force regeneration |
| **Weird audio issues** | `cleanup --cache-only` | Clear corrupted cache |
| **Project complete** | `cleanup` | Free disk space |
| **Just checking size** | `cleanup --dry-run` | Preview only |

---

## Quick Commands

```bash
# Preview (safe, shows what would be deleted)
python3 -m src.cli.main cleanup --dry-run

# Clear cache only (RECOMMENDED - keeps your videos)
python3 -m src.cli.main cleanup --cache-only --force

# Clear outputs only (keeps cache for speed)
python3 -m src.cli.main cleanup --outputs-only

# Clear everything (with confirmation)
python3 -m src.cli.main cleanup

# Clear everything (no prompt - use carefully!)
python3 -m src.cli.main cleanup --force
```

---

## Best Practice Workflow

### 1. Testing Voices:
```bash
# Before each voice test
python3 -m src.cli.main cleanup --cache-only --force

# Test voice
python3 -m src.cli.main create "script.txt" --config config.yaml -o test
```

### 2. Adjusting Music (Voice Unchanged):
```bash
# DON'T clear cache - reuse voice!
python3 -m src.cli.main create "script.txt" --music-offset 20 -o v1
python3 -m src.cli.main create "script.txt" --music-offset 30 -o v2
# Voice generation skipped = fast!
```

### 3. After Session:
```bash
# Keep videos, clear cache
python3 -m src.cli.main cleanup --cache-only
```

---

## What Gets Cached

```
data/
├── cache/              👈 Clear this often
│   ├── tts/           (voice audio: 1-3 MB each)
│   ├── mixed/         (voice+music: 2-4 MB each)
│   └── models/        (AI models: KEEP unless huge)
│
└── outputs/           👈 Your final videos (keep!)
    └── *.mp4          (videos: 800 KB - 2 MB each)
```

---

## Today's Lesson

### The Problem:
```
Test 3: Changed gTTS → pyttsx3
Result: Used cached female voice from Test 2!
Reason: Cache key = script text only (no engine info)
```

### The Fix:
```bash
python3 -m src.cli.main cleanup --cache-only --force
# Then regenerate = real male voice!
```

---

## Remember

✅ **DO**: Clear cache when changing voices/engines  
✅ **DO**: Preview with `--dry-run` first  
✅ **DO**: Use `--cache-only` to keep videos  
❌ **DON'T**: Clear cache for music/video tweaks  
❌ **DON'T**: Delete model files unless necessary  

---

**Most Common**: `python3 -m src.cli.main cleanup --cache-only --force`

*Use this before every voice test!*




