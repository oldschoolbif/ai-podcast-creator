# 🚀 Launch GUI - Quick Start

## Two Options: Web or Desktop

### 🌐 Web Interface (Recommended)

**Beautiful, modern interface in your browser!**

```bash
# 1. Install Gradio (if needed)
pip install gradio

# 2. Launch
python launch_web_gui.py

# 3. Open browser to:
http://localhost:7860
```

**Features:**
- ✅ Drag & drop file uploads
- ✅ Live video preview
- ✅ Mobile responsive
- ✅ Can be embedded in websites
- ✅ Real-time progress tracking
- ✅ Example scripts included

**Advanced:**
```bash
# Create public link (share with anyone)
python launch_web_gui.py --share

# Different port
python launch_web_gui.py --port 8080

# Add password protection
python launch_web_gui.py --auth username:password
```

---

### 💻 Desktop GUI

**Native desktop application!**

```bash
# 1. Launch (tkinter included with Python)
python launch_desktop_gui.py

# 2. Window opens automatically!
```

**Features:**
- ✅ Traditional desktop app
- ✅ File browser dialogs
- ✅ Progress log window
- ✅ Quick output folder access
- ✅ GPU status display
- ✅ Runs entirely offline

---

## 📝 Using the GUI

### Both interfaces let you:

1. **Select script file** (.txt or .md)
2. **Add music** (optional):
   - Upload music file OR
   - Describe music style
3. **Choose settings**:
   - Voice engine (gTTS, Coqui, ElevenLabs, Azure)
   - Avatar style (Professional, Gradient, News, Tech)
   - Video quality (High/Medium/Low)
4. **Click "Create Podcast"**
5. **Wait** for processing
6. **Download** your video!

---

## 🎯 Quick Examples

### Example 1: Basic Podcast
1. Upload `Creations/example_welcome.txt`
2. Leave music blank
3. Voice: gTTS (Free)
4. Click Create
5. Wait ~30 seconds
6. Done!

### Example 2: With Music
1. Upload your script
2. Upload your music file (or describe: "calm ambient")
3. Voice: gTTS
4. Quality: High (1080p)
5. Click Create
6. Done!

### Example 3: High Quality (GPU)
1. Upload script
2. Voice: Coqui (High Quality, GPU)
3. Avatar: Professional Studio
4. Quality: High (1080p)
5. Click Create
6. Wait 2-5 minutes
7. Amazing quality video!

---

## 🔍 Interface Overview

### Web Interface Screenshot Layout:
```
┌──────────────────────────────────────────────────────┐
│  🎙️ AI Podcast Creator                              │
│  ⚡ GPU: NVIDIA RTX 3080 (10GB)                      │
├──────────────────────────────────────────────────────┤
│  ┌─────────────────┬─────────────────┐              │
│  │ 📄 Script       │ ⚙️ Settings     │              │
│  │ [Upload]        │ Voice: [▼]      │              │
│  │                 │ Avatar: [▼]     │              │
│  │ 🎵 Music        │ Quality: [▼]    │              │
│  │ [Upload]        │                 │              │
│  │ Or describe:    │ [🚀 Create]     │              │
│  │ [_________]     │                 │              │
│  │                 │ 📹 Output       │              │
│  │                 │ [Video Player]  │              │
│  └─────────────────┴─────────────────┘              │
└──────────────────────────────────────────────────────┘
```

### Desktop GUI Screenshot Layout:
```
┌──────────────────────────────────────────────────────┐
│  🎙️ AI Podcast Creator                              │
├──────────────────────┬───────────────────────────────┤
│  📄 Input Files      │  ⚙️ Settings                  │
│  Script: [Browse]    │  Voice: [Dropdown ▼]         │
│  Music: [Browse]     │  Avatar: [Dropdown ▼]        │
│  Or: [__________]    │  Quality: [Dropdown ▼]       │
│                      │  Output: [__________]         │
├──────────────────────┴───────────────────────────────┤
│  📝 Progress Log                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │ ⚡ GPU: RTX 3080                               │ │
│  │ 📄 Reading script: my_podcast.txt              │ │
│  │ 🗣️ Generating speech...                        │ │
│  │ ✅ Speech generated                            │ │
│  │ 🎬 Creating video...                           │ │
│  └────────────────────────────────────────────────┘ │
│  [🚀 Create] [📁 Open Output] [Clear]               │
└──────────────────────────────────────────────────────┘
```

---

## 🆘 Troubleshooting

### Web GUI won't start:
```bash
# Install Gradio
pip install gradio

# Try different port
python launch_web_gui.py --port 8080
```

### Desktop GUI won't start:
```bash
# Install tkinter (Linux only)
sudo apt-get install python3-tk

# Verify
python -c "import tkinter"
```

### Can't access from phone:
```bash
# Allow external access
python launch_web_gui.py --host 0.0.0.0

# Or create public link
python launch_web_gui.py --share
```

---

## 📚 Full Documentation

See **[GUI_GUIDE.md](GUI_GUIDE.md)** for complete documentation including:
- Advanced features
- Customization options
- Embedding in websites
- Security settings
- Mobile access
- Troubleshooting

---

## 🎉 That's It!

**No command line needed!**

Just launch the GUI and start creating amazing podcasts! 🎙️✨

**Which to choose?**
- 🌐 **Web**: Modern, embeddable, mobile-friendly
- 💻 **Desktop**: Traditional, offline, file dialogs

Both work great - pick what you prefer!

