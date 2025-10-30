# 🚀 Quick Start - Web Interface

**Status:** ✅ Running NOW!  
**URL:** http://localhost:7860

---

## 🎯 Get Started in 30 Seconds

### 1. Open Your Browser
```
http://localhost:7860
```

### 2. See the Interface
You'll see a beautiful modern interface with:
- 📄 **Script Upload** section (left)
- 🎤 **Voice & Avatar** settings (left)
- ⚙️ **Video Settings** (right)
- 🚀 **Create Podcast** button (right)

### 3. Upload a Script
Click **"Upload Script File"** and select:
- `Creations/example_welcome.txt` (try this first!)
- Or any `.txt` or `.md` file

### 4. Select Your Voice
In the **"Voice Engine"** dropdown, choose:
- **gTTS** (currently active, works immediately)
- **coqui** (better quality, needs `pip install TTS`)
- **elevenlabs** (premium, needs API key)
- **azure** (cloud, needs API key)

### 5. Click Create!
Press the **"🚀 Create Podcast"** button and watch it work!

---

## 🎤 Voice Options Explained

### Currently Selected: gTTS (Free)
✅ Works right now, no setup  
✅ British Female voice  
✅ Fast and reliable  
⚠️ Basic quality (robotic)

**To Try Better Quality:**
1. Install Coqui: `pip install TTS`
2. In web interface: Change dropdown to "coqui"
3. Generate - sounds much more natural!

---

## 📝 Example Scripts Available

Try these pre-made scripts (in `Creations/` folder):

1. **example_welcome.txt** - Simple welcome message
2. **example_tech_news.txt** - Tech news format
3. **example_educational.txt** - Educational content
4. **example_storytelling.txt** - Story format

---

## 🎨 Interface Tabs

### Tab 1: Create Podcast ⭐
Main creation interface with all controls

### Tab 2: Examples
Pre-made script templates you can copy

### Tab 3: Settings & Help
Documentation and configuration help

---

## 💡 Pro Tips

### Music Options:
- **Upload file:** Use your own MP3/WAV
- **Describe style:** Type "calm ambient" and AI generates it
- **Skip:** Leave both blank for voice-only

### Voice Speed:
- Use the slider to adjust speed (0.5x - 2.0x)
- Default 1.0x is natural

### Video Quality:
- **High (1080p):** Best quality, larger file (~500MB)
- **Medium (720p):** Good balance (~200MB)
- **Low (480p):** Fast, small file (~100MB)

---

## 🔄 Common Workflows

### Simple Audio-Only Test:
1. Upload script
2. Leave music blank
3. Keep gTTS voice
4. Click Create
5. **Result:** Video with voice in 30 seconds!

### High Quality with Music:
1. Upload script
2. Add music file OR describe style
3. Switch to "coqui" voice (if installed)
4. Select "High (1080p)"
5. Click Create
6. **Result:** Professional podcast in 2-5 minutes!

### Quick Demo:
1. Upload `Creations/example_welcome.txt`
2. Type music: "upbeat intro"
3. Keep gTTS
4. Select "Medium (720p)"
5. Click Create
6. **Result:** Complete demo in 60 seconds!

---

## 🛠️ Troubleshooting

### Can't Access http://localhost:7860?
```powershell
# Restart the server
cd D:\dev\AI_Podcast_Creator
python launch_web_gui.py
```

### Want Different Port?
```powershell
python launch_web_gui.py --port 8080
```

### Slow Generation?
- Try "Low (480p)" quality
- Skip music generation
- Install PyTorch for GPU acceleration

### Voice Not Working?
- **gTTS:** Needs internet connection
- **coqui:** Needs `pip install TTS`
- **elevenlabs:** Needs API key in `.env`
- **azure:** Needs API key in `.env`

---

## 📊 What Happens When You Click Create?

1. **Reading script...** (5 seconds)
2. **Parsing script...** (2 seconds)
3. **Generating speech...** (10-30 seconds)
4. **Processing music...** (20-60 seconds if AI, instant if file)
5. **Mixing audio...** (5 seconds)
6. **Creating video...** (10-30 seconds)
7. **Complete!** Video preview appears

**Total time:** 30 seconds to 5 minutes depending on settings

---

## 🌐 Share Your Interface

Want others to access your interface?

### On Your Network:
```powershell
# Find your IP
ipconfig | findstr IPv4

# Start with network access
python launch_web_gui.py --host 0.0.0.0

# Others can access: http://YOUR_IP:7860
```

### Public Internet:
```powershell
# Create public link
python launch_web_gui.py --share

# You'll get: https://xxxxx.gradio.live (valid 72 hours)
```

---

## 🎯 Your First Podcast in 1 Minute

Follow these exact steps:

```
1. Open: http://localhost:7860
2. Click: "Upload Script File"
3. Select: Creations/example_welcome.txt
4. Leave: Everything else as default
5. Click: "🚀 Create Podcast"
6. Wait: 30-60 seconds
7. Watch: Progress bar update
8. See: Video preview appear!
9. Click: Download button
10. Done: You have a video podcast!
```

---

## ✅ Checklist

Before creating your first podcast:

- [x] Web interface running (http://localhost:7860)
- [x] Gradio installed
- [x] Script file ready (.txt or .md)
- [ ] Open browser to localhost:7860
- [ ] Upload script
- [ ] Select voice engine
- [ ] Click Create!

---

## 🎉 Ready to Go!

Your web interface is **live and waiting** at:

### http://localhost:7860

Just open your browser and start creating! 🎙️✨

---

## 📚 Need More Help?

- **WEB_INTERFACE_READY.md** - Full interface guide
- **GUI_GUIDE.md** - Complete GUI documentation
- **GTTS_VOICE_OPTIONS.md** - Voice options explained
- **README.md** - Main project documentation

---

**Happy Podcasting!** 🎉

*Interface ready at: http://localhost:7860*

