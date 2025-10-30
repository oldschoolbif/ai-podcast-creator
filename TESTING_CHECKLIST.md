# Complete Testing Checklist

**Run these tests to verify your AI Podcast Creator setup from scratch.**

---

## ✅ Pre-Test Setup

```bash
cd d:\dev\AI_Podcast_Creator
```

---

## 📋 Test 1: Python & Environment (5 min)

### 1.1 Check Python Version
```bash
python --version
```
**Expected:** `Python 3.10.x` or higher

**Result:** ___________

---

### 1.2 Check if Virtual Environment Active
```bash
# Windows
venv\Scripts\activate

# Check prompt changes
```
**Expected:** `(venv)` appears in prompt

**Result:** ___________

---

### 1.3 Check PyTorch Installation
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
```
**Expected:** `PyTorch: 2.1.0` or similar

**Result:** ___________

---

## 📋 Test 2: GPU Detection (5 min)

### 2.1 Run GPU Check Script
```bash
python check_gpu.py
```

**Expected Output:**
```
✓ PyTorch version: 2.1.0+cu118
✓ CUDA available: Yes
✓ GPU: NVIDIA GeForce RTX 4060
✓ GPU Memory: 8.0 GB
✓ GPU is ready for AI Podcast Creator!
```

**Your Output:**
```
___________
___________
___________
```

**Pass/Fail:** ___________

---

### 2.2 Check NVIDIA Drivers
```bash
nvidia-smi
```

**Expected:** Shows GPU info, driver version, CUDA version

**Result:** ___________

---

## 📋 Test 3: Bug Fixes (2 min)

### 3.1 Run Bug Fix Script
```bash
python fix_bugs.py
```

**Expected Output:**
```
✓ Bug #2 fixed!
✓ Bug #4 fixed!
✓ Bug #7 fixed!
✓ Bug #9 fixed!
```

**Pass/Fail:** ___________

---

### 3.2 Verify .gitkeep Files Created
```bash
dir /s .gitkeep
```

**Expected:** Multiple .gitkeep files in data/, logs/, etc.

**Result:** ___________

---

## 📋 Test 4: Basic Dependencies (5 min)

### 4.1 Check Core Imports
```bash
python -c "import numpy, pydub, moviepy, yaml; print('Core deps OK')"
```

**Expected:** `Core deps OK`

**Result:** ___________

---

### 4.2 Check gTTS (Basic TTS)
```bash
python -c "from gtts import gTTS; print('gTTS OK')"
```

**Expected:** `gTTS OK`

**Result:** ___________

---

### 4.3 Test Simple TTS Generation
```bash
python -c "from gtts import gTTS; tts = gTTS('test', lang='en'); tts.save('test_tts.mp3'); print('TTS works')"
```

**Expected:** Creates `test_tts.mp3` file

**Result:** ___________

---

## 📋 Test 5: Project Structure (3 min)

### 5.1 Check Directory Structure
```bash
dir src\core
dir src\cli
dir src\utils
dir Creations
dir data\cache
dir data\outputs
```

**All exist?** Yes / No: ___________

---

### 5.2 Check Example Scripts
```bash
dir Creations\*.txt
```

**Expected:** Shows example_welcome.txt, example_educational.txt, etc.

**Result:** ___________

---

### 5.3 Check Config File
```bash
type config.yaml | findstr "engine:"
```

**Expected Output:**
```
  engine: "gtts"
  engine: "musicgen"
  engine: "none"
```

**Result:** ___________

---

## 📋 Test 6: Core Modules (5 min)

### 6.1 Test GPU Utils Import
```bash
python -c "from src.utils.gpu_utils import get_gpu_manager; mgr = get_gpu_manager(); print(f'GPU available: {mgr.gpu_available}')"
```

**Expected:** `GPU available: True` (or False if no GPU)

**Result:** ___________

---

### 6.2 Test TTS Engine Import
```bash
python -c "from src.core.tts_engine import TTSEngine; print('TTS Engine OK')"
```

**Expected:** `TTS Engine OK`

**Result:** ___________

---

### 6.3 Test Audio Mixer Import
```bash
python -c "from src.core.audio_mixer import AudioMixer; print('Audio Mixer OK')"
```

**Expected:** `Audio Mixer OK`

**Result:** ___________

---

## 📋 Test 7: Basic Generation - CPU Mode (10 min)

### 7.1 Check Current TTS Engine
```bash
python -c "import yaml; c=yaml.safe_load(open('config.yaml')); print(f\"TTS: {c['tts']['engine']}\")"
```

**Expected:** `TTS: gtts` (CPU mode)

**Result:** ___________

---

### 7.2 Test CLI Help
```bash
python -m src.cli.main --help
```

**Expected:** Shows command help

**Result:** ___________

---

### 7.3 Generate Simple Podcast (CPU Mode)
```bash
python -m src.cli.main create Creations/example_welcome.txt --preview
```

**Expected:**
- Process starts
- Shows progress
- Generates audio file
- Takes 2-5 minutes (CPU mode)

**Time taken:** ___________ minutes

**Output location:** data\outputs\___________

**Pass/Fail:** ___________

---

### 7.4 Check Output File
```bash
dir data\outputs\*latest*
```

**Expected:** Video file (MP4) or audio file exists

**Size:** ___________ MB

**Can play it?** Yes / No: ___________

---

## 📋 Test 8: GPU Packages Installation (5 min)

### 8.1 Install Coqui TTS
```bash
pip install TTS
```

**Expected:** Installation completes successfully

**Result:** ___________

---

### 8.2 Verify Coqui Installation
```bash
python -c "import TTS; print(f'TTS version: {TTS.__version__}')"
```

**Expected:** Shows version number

**Result:** ___________

---

### 8.3 Install AudioCraft
```bash
pip install audiocraft
```

**Expected:** Installation completes successfully

**Result:** ___________

---

### 8.4 Verify AudioCraft Installation
```bash
python -c "import audiocraft; print('AudioCraft OK')"
```

**Expected:** `AudioCraft OK`

**Result:** ___________

---

## 📋 Test 9: GPU Configuration (5 min)

### 9.1 Backup Original Config
```bash
copy config.yaml config.yaml.backup
```

**Result:** ___________

---

### 9.2 Update TTS to GPU Mode

**Manual Edit:** Open `config.yaml` and change:

```yaml
tts:
  engine: "coqui"  # Changed from "gtts"
```

**Done?** Yes / No: ___________

---

### 9.3 Update Music to GPU Mode

**Manual Edit:** In same `config.yaml`:

```yaml
music:
  engine: "musicgen"  # Should already be this
  musicgen:
    model: "facebook/musicgen-medium"  # Or "small" for 6GB GPU
    use_gpu: true
```

**Done?** Yes / No: ___________

---

### 9.4 Verify Config Changes
```bash
python -c "import yaml; c=yaml.safe_load(open('config.yaml')); print(f\"TTS: {c['tts']['engine']}, Music: {c['music']['engine']}\")"
```

**Expected:** `TTS: coqui, Music: musicgen`

**Result:** ___________

---

## 📋 Test 10: GPU-Accelerated TTS (10 min)

### 10.1 Test Coqui TTS First Load (Downloads Models)
```bash
python -c "from TTS.api import TTS; import os; os.environ['COQUI_TOS_AGREED']='1'; tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=True); print('Coqui loaded')"
```

**Expected:**
- Downloads models first time (~2-3 GB, 5-10 minutes)
- Shows "Coqui loaded"

**Time:** ___________ minutes

**Result:** ___________

---

### 10.2 Generate with GPU TTS
```bash
python -m src.cli.main create Creations/example_welcome.txt --preview
```

**Expected:**
- Uses GPU (check nvidia-smi in another window)
- Much faster than CPU mode
- Better quality voice

**GPU used?** (check nvidia-smi): Yes / No: ___________

**Time taken:** ___________ seconds

**Compare to CPU time:** ___________ times faster

**Pass/Fail:** ___________

---

## 📋 Test 11: GPU-Accelerated Music (15 min)

### 11.1 Test MusicGen First Load (Downloads Models)

**Note:** Creates example script with music tag

Create `test_music.txt`:
```
[SPEAKER: Host]
Welcome to this test.

[MUSIC: calm background music]

This is a test of music generation.
```

Save to: `Creations/test_music.txt`

**Done?** Yes / No: ___________

---

### 11.2 Generate with Music
```bash
python -m src.cli.main create Creations/test_music.txt
```

**Expected:**
- Downloads MusicGen model first time (~3 GB, 5-10 minutes)
- Generates music on GPU
- Takes 1-3 minutes for music generation

**Time for music generation:** ___________ minutes

**GPU used?** (check nvidia-smi): Yes / No: ___________

**Pass/Fail:** ___________

---

## 📋 Test 12: Full GPU Pipeline (15 min)

### 12.1 Generate Complete Podcast with GPU
```bash
python -m src.cli.main create Creations/example_educational.txt
```

**Expected:**
- GPU-accelerated TTS
- GPU-accelerated music
- Complete video output
- Total time: 5-10 minutes (vs. 60-80 min on CPU)

**Time taken:** ___________ minutes

**Output location:** ___________

**File size:** ___________ MB

**Pass/Fail:** ___________

---

### 12.2 Performance Summary

**CPU Mode (Test 7.3):** ___________ minutes
**GPU Mode (Test 12.1):** ___________ minutes
**Speedup:** ___________x faster

**Expected:** 10-12x speedup

**Achieved target?** Yes / No: ___________

---

## 📋 Test 13: Verify Output Quality (5 min)

### 13.1 Play Generated Video
```bash
# Open in default player
start data\outputs\[latest_file].mp4
```

**Checklist:**
- [ ] Video plays
- [ ] Audio is clear
- [ ] Voice sounds natural (Coqui)
- [ ] Music is present (if script has [MUSIC] tags)
- [ ] No audio glitches
- [ ] Video length matches script

**Pass/Fail:** ___________

---

### 13.2 Check Audio Quality
**Compared to gTTS:**
- [ ] More natural intonation
- [ ] Better pronunciation
- [ ] Emotional expression
- [ ] British accent clear

**Pass/Fail:** ___________

---

## 📋 Test 14: Optional - Avatar (30+ min)

**Note:** Avatar setup is optional and requires additional setup.

### 14.1 Check if SadTalker Needed
**Do you want animated avatars?** Yes / No: ___________

**If No:** Skip this test

**If Yes:** Follow `GPU_SETUP_COMPLETE.md` Section 4

---

## 📊 FINAL RESULTS SUMMARY

### Core Functionality
- Python & Environment: **Pass / Fail**
- GPU Detection: **Pass / Fail**
- Bug Fixes Applied: **Pass / Fail**
- Basic Dependencies: **Pass / Fail**
- Project Structure: **Pass / Fail**
- Core Modules: **Pass / Fail**

### Basic Generation (CPU)
- CLI Works: **Pass / Fail**
- Can Generate Podcasts: **Pass / Fail**
- Output Quality OK: **Pass / Fail**

### GPU Features
- GPU Packages Installed: **Pass / Fail**
- GPU TTS Works: **Pass / Fail**
- GPU Music Works: **Pass / Fail**
- Full GPU Pipeline Works: **Pass / Fail**
- Performance Target Met (10x): **Pass / Fail**

### Overall Status
**READY FOR PRODUCTION?** ✅ Yes / ❌ No

**GPU ACCELERATION WORKING?** ✅ Yes / ❌ No

**SPEEDUP ACHIEVED:** ___________x

---

## 🐛 Issues Found During Testing

**Document any issues:**

1. ___________________________________________
2. ___________________________________________
3. ___________________________________________
4. ___________________________________________
5. ___________________________________________

---

## 📝 Notes

**Additional observations:**

___________________________________________
___________________________________________
___________________________________________
___________________________________________

---

## ✅ Next Steps After Testing

**If all tests pass:**
1. Commit changes to GitHub
2. Start creating real podcasts!
3. Read advanced docs for customization

**If some tests fail:**
1. Note which tests failed above
2. Check troubleshooting section of docs
3. Fix issues and re-run tests
4. Create GitHub issue if needed

---

**Testing completed:** _____ / _____ / _____

**Tested by:** ___________

**Total time:** ___________ minutes

---

**Save this completed checklist for your records!**


